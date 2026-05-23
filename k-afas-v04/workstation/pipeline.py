"""
워크스테이션 파이프라인 — 단계별 자동 구동

흐름:
  TASK → CLASSIFY → VALIDATE → ROUTE → EXECUTE → MEASURE → REPORT
    │        │          │         │        │         │         │
    ▼        ▼          ▼         ▼        ▼         ▼         ▼
  입력    Tier결정   PII/중복   AI선택   프롬프트    수치화    결과
  수신     자동       REJECT     자동     자동실행    자동      출력

불변조건:
  - 단계 건너뛰기 금지 (순차 실행 강제)
  - REJECT 발생 시 즉시 중단 + 사유 반환
  - 모든 단계 소요시간 측정
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .harness_bridge import HarnessBridge, Tier, UsageRecord


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    REJECTED = "rejected"
    ERROR = "error"


@dataclass
class StepResult:
    step: str
    status: StepStatus
    data: Any = None
    reason: str = ""
    elapsed_ms: float = 0.0


@dataclass
class PipelineContext:
    """파이프라인 실행 컨텍스트 — 전 단계 공유"""
    task_type: str = ""
    prompt: str = ""
    tier: Tier = Tier.LOW
    model: str = ""
    response: str = ""
    usage: UsageRecord | None = None
    steps: list[StepResult] = field(default_factory=list)
    total_ms: float = 0.0

    def summary(self) -> dict[str, Any]:
        return {
            "task_type": self.task_type,
            "tier": self.tier.value,
            "model": self.model,
            "steps": len(self.steps),
            "all_passed": all(s.status == StepStatus.PASSED for s in self.steps),
            "total_ms": round(self.total_ms, 2),
            "cost_units": self.usage.cost_units if self.usage else 0,
            "efficiency": self.usage.efficiency_score if self.usage else 0,
        }


class WorkstationPipeline:
    """
    단계별 파이프라인 실행기

    사용법:
        pipe = WorkstationPipeline()
        result = pipe.run(task_type="status_check", prompt="현재 상태 확인")
    """

    def __init__(self):
        self.bridge = HarnessBridge()

    def run(self, task_type: str, prompt: str, executor: Any = None) -> PipelineContext:
        """전체 파이프라인 실행 (task→routing→execute→measure)"""
        ctx = PipelineContext(task_type=task_type, prompt=prompt)
        t0 = time.time()

        # Step 1: CLASSIFY
        ctx = self._step_classify(ctx)
        if self._is_rejected(ctx):
            return self._finalize(ctx, t0)

        # Step 2: VALIDATE
        ctx = self._step_validate(ctx)
        if self._is_rejected(ctx):
            return self._finalize(ctx, t0)

        # Step 3: ROUTE
        ctx = self._step_route(ctx)
        if self._is_rejected(ctx):
            return self._finalize(ctx, t0)

        # Step 4: EXECUTE
        ctx = self._step_execute(ctx, executor)
        if self._is_rejected(ctx):
            return self._finalize(ctx, t0)

        # Step 5: MEASURE
        ctx = self._step_measure(ctx)

        return self._finalize(ctx, t0)

    # ── 개별 단계 구현 ────────────────────────────────

    def _step_classify(self, ctx: PipelineContext) -> PipelineContext:
        t = time.time()
        try:
            ctx.tier = self.bridge.classify(ctx.task_type)
            ctx.steps.append(StepResult(
                step="classify",
                status=StepStatus.PASSED,
                data={"tier": ctx.tier.value},
                elapsed_ms=_ms(t),
            ))
        except Exception as e:
            ctx.steps.append(StepResult(
                step="classify", status=StepStatus.ERROR,
                reason=str(e), elapsed_ms=_ms(t),
            ))
        return ctx

    def _step_validate(self, ctx: PipelineContext) -> PipelineContext:
        t = time.time()
        ok, reason = self.bridge.validate(ctx.prompt)
        if ok:
            ctx.steps.append(StepResult(
                step="validate", status=StepStatus.PASSED,
                elapsed_ms=_ms(t),
            ))
        else:
            ctx.steps.append(StepResult(
                step="validate", status=StepStatus.REJECTED,
                reason=reason, elapsed_ms=_ms(t),
            ))
        return ctx

    def _step_route(self, ctx: PipelineContext) -> PipelineContext:
        t = time.time()
        ctx.model = self.bridge.route(ctx.tier)
        ctx.steps.append(StepResult(
            step="route", status=StepStatus.PASSED,
            data={"model": ctx.model}, elapsed_ms=_ms(t),
        ))
        return ctx

    def _step_execute(self, ctx: PipelineContext, executor: Any) -> PipelineContext:
        t = time.time()
        if executor and callable(executor):
            try:
                ctx.response = executor(ctx.model, ctx.prompt)
                ctx.steps.append(StepResult(
                    step="execute", status=StepStatus.PASSED,
                    data={"response_len": len(ctx.response)},
                    elapsed_ms=_ms(t),
                ))
            except Exception as e:
                ctx.steps.append(StepResult(
                    step="execute", status=StepStatus.ERROR,
                    reason=str(e), elapsed_ms=_ms(t),
                ))
        else:
            # executor 미제공 시 드라이런 (토큰 추정만)
            ctx.response = f"[DRY_RUN] model={ctx.model} prompt_len={len(ctx.prompt)}"
            ctx.steps.append(StepResult(
                step="execute", status=StepStatus.PASSED,
                data={"mode": "dry_run"}, elapsed_ms=_ms(t),
            ))
        return ctx

    def _step_measure(self, ctx: PipelineContext) -> PipelineContext:
        t = time.time()
        # 토큰 추정 (실제 API 응답에서 가져오거나 근사)
        input_tokens = len(ctx.prompt) // 4   # ~4chars/token 근사
        output_tokens = len(ctx.response) // 4
        total_ms = sum(s.elapsed_ms for s in ctx.steps)

        ctx.usage = self.bridge.measure(
            task_type=ctx.task_type,
            tier=ctx.tier,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=total_ms,
            prompt=ctx.prompt,
        )
        ctx.steps.append(StepResult(
            step="measure", status=StepStatus.PASSED,
            data={
                "tokens": input_tokens + output_tokens,
                "cost": ctx.usage.cost_units,
                "efficiency": ctx.usage.efficiency_score,
            },
            elapsed_ms=_ms(t),
        ))
        return ctx

    # ── 유틸 ──────────────────────────────────────────

    def _is_rejected(self, ctx: PipelineContext) -> bool:
        return ctx.steps[-1].status in (StepStatus.REJECTED, StepStatus.ERROR)

    def _finalize(self, ctx: PipelineContext, t0: float) -> PipelineContext:
        ctx.total_ms = (time.time() - t0) * 1000
        return ctx

    def stats(self) -> dict[str, Any]:
        """누적 워크스테이션 통계"""
        return self.bridge.stats()


def _ms(start: float) -> float:
    return round((time.time() - start) * 1000, 2)
