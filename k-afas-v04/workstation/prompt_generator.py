"""
자동 프롬프트 생성기 — 작업 유형별 최적 프롬프트 자동 생성 + 실행

원칙:
  - 인간 개입 0: task_type만 입력하면 프롬프트 자동 생성 → 파이프라인 자동 실행
  - Tier별 프롬프트 길이 제한 (LOW=짧고 직접, HIGH=구조화)
  - 불필요한 재확인/설명/코드블록 제거 — 결과만 반환
  - 컨텍스트 L2 압축: 핵심 키워드만 주입
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from .harness_bridge import Tier
from .pipeline import WorkstationPipeline, PipelineContext


# ── 프롬프트 템플릿 (Tier별 최적화) ───────────────────
TEMPLATES: dict[str, str] = {
    # LOW — 최소 토큰, 직접 지시
    "status_check": "현재 {target} 상태 반환. 설명 불필요. JSON만.",
    "file_read": "{path} 파일 내용 중 {section}만 추출. 코드블록 없이 텍스트만.",
    "format_convert": "{input} → {output_format} 변환. 결과만.",
    "log_query": "최근 {n}건 로그에서 {filter} 해당 항목만. 테이블 형식.",
    "config_lookup": "{key} 설정값 반환. 한 줄.",
    "simple_confirm": "{question} → 예/아니오 + 1줄 근거.",

    # MID — 구조화된 짧은 지시
    "code_edit_single": "파일: {path}\n변경: {change}\n제약: 해당 부분만 수정, diff 형식 반환.",
    "summarize": "{content}\n위를 {max_lines}줄 이내로 요약. 핵심만.",
    "test_run": "{test_target} 테스트 실행 후 결과만 반환. PASS/FAIL + 실패 사유.",
    "bug_fix_simple": "버그: {description}\n파일: {path}\n수정 코드만 반환. 설명 불필요.",

    # HIGH — 구조화 + 제약조건 명시
    "architecture_design": (
        "목표: {goal}\n"
        "제약: {constraints}\n"
        "산출: 구조도 + 파일목록 + 핵심결정 3개\n"
        "형식: 마크다운. 불필요 설명 제거."
    ),
    "multi_file_refactor": (
        "대상: {files}\n"
        "리팩터 목표: {goal}\n"
        "규칙: 1) 기존 API 유지 2) 테스트 깨지면 안됨\n"
        "산출: 파일별 diff만."
    ),
    "complex_reasoning": (
        "문제: {problem}\n"
        "맥락: {context}\n"
        "산출: 결론 + 근거 3개. 200토큰 이내."
    ),
    "security_audit": (
        "대상: {target}\n"
        "점검: {checklist}\n"
        "산출: PASS/FAIL 목록 + 위험 항목 상세."
    ),
}

# ── Tier별 토큰 한도 ──────────────────────────────────
MAX_PROMPT_TOKENS: dict[Tier, int] = {
    Tier.LOW: 100,     # 극소화
    Tier.MID: 500,     # 중간
    Tier.HIGH: 2000,   # 구조화 허용
}


@dataclass
class GeneratedPrompt:
    task_type: str
    tier: Tier
    prompt: str
    token_estimate: int
    within_limit: bool


class PromptGenerator:
    """
    작업 유형 + 파라미터 → 최적 프롬프트 자동 생성

    사용법:
        gen = PromptGenerator()
        prompt = gen.generate("status_check", target="PR #2")
        # → "현재 PR #2 상태 반환. 설명 불필요. JSON만."
    """

    def __init__(self, pipeline: WorkstationPipeline | None = None):
        self.pipeline = pipeline or WorkstationPipeline()

    def generate(self, task_type: str, **params: Any) -> GeneratedPrompt:
        """프롬프트 생성 (실행 안함)"""
        tier = self.pipeline.bridge.classify(task_type)
        template = TEMPLATES.get(task_type, "{prompt}")

        # 파라미터 주입
        try:
            prompt = template.format(**params)
        except KeyError:
            # 누락 파라미터 → 빈값 대체
            prompt = template
            for k, v in params.items():
                prompt = prompt.replace(f"{{{k}}}", str(v))

        # 토큰 추정 + 한도 체크
        token_est = len(prompt) // 4
        limit = MAX_PROMPT_TOKENS[tier]
        within = token_est <= limit

        # 한도 초과 시 자동 압축
        if not within:
            prompt = self._compress(prompt, limit)
            token_est = len(prompt) // 4
            within = True

        return GeneratedPrompt(
            task_type=task_type,
            tier=tier,
            prompt=prompt,
            token_estimate=token_est,
            within_limit=within,
        )

    def generate_and_run(self, task_type: str, executor: Any = None, **params: Any) -> PipelineContext:
        """프롬프트 생성 → 파이프라인 자동 실행 (인간 개입 0)"""
        gp = self.generate(task_type, **params)
        return self.pipeline.run(
            task_type=task_type,
            prompt=gp.prompt,
            executor=executor,
        )

    def batch_run(self, tasks: list[dict[str, Any]], executor: Any = None) -> list[PipelineContext]:
        """배치 실행 — 여러 작업 순차 자동 처리"""
        results = []
        for task in tasks:
            task_type = task.pop("task_type")
            ctx = self.generate_and_run(task_type, executor=executor, **task)
            results.append(ctx)
        return results

    def _compress(self, prompt: str, max_tokens: int) -> str:
        """L2 압축: 핵심 키워드만 유지"""
        max_chars = max_tokens * 4
        if len(prompt) <= max_chars:
            return prompt

        # 줄바꿈 제거 → 공백 압축 → 잘라내기
        compressed = " ".join(prompt.split())
        if len(compressed) > max_chars:
            compressed = compressed[:max_chars - 3] + "..."
        return compressed

    def available_tasks(self) -> list[str]:
        """사용 가능한 작업 유형 목록"""
        return list(TEMPLATES.keys())

    def stats(self) -> dict[str, Any]:
        """파이프라인 누적 통계 위임"""
        return self.pipeline.stats()
