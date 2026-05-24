"""K-AFAS 평가 지표 측정 모듈.

핵심 KPI: Time-to-Review-Ready (TTRR)
  = 첩보(raw)가 시스템에 들어온 시각부터
    검토 패키지가 인간 검토대기에 도달한 시각까지의 경과(초).

NOTE: 사격까지의 시간(Time-to-Fire)은 측정하지 않는다 (REJECT 항목).
      K-AFAS는 첩보→정보→검토 단계 단축에만 관여한다.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from typing import Iterable

KST = timezone(timedelta(hours=9))


@dataclass
class MetricsAggregator:
    """후보 다수의 운용 KPI 집계."""
    ttrr_seconds: list[float] = field(default_factory=list)
    candidates_total: int = 0
    passed_to_review: int = 0
    held: int = 0
    rejected: int = 0
    audit_complete: int = 0

    def record(
        self,
        ingest_at_kst: str,
        review_ready_at_kst: str,
        terminal_state: str,        # "PASS" | "HOLD" | "REJECT"
        audit_logged: bool,
    ) -> None:
        self.candidates_total += 1
        if terminal_state == "PASS":
            self.passed_to_review += 1
        elif terminal_state == "HOLD":
            self.held += 1
        elif terminal_state == "REJECT":
            self.rejected += 1
        if audit_logged:
            self.audit_complete += 1
        try:
            t0 = datetime.fromisoformat(ingest_at_kst)
            t1 = datetime.fromisoformat(review_ready_at_kst)
            self.ttrr_seconds.append((t1 - t0).total_seconds())
        except (ValueError, TypeError):
            pass

    def percentile(self, p: float) -> float:
        if not self.ttrr_seconds:
            return 0.0
        s = sorted(self.ttrr_seconds)
        k = max(0, min(len(s) - 1, int(round(p / 100 * (len(s) - 1)))))
        return s[k]



    def report(self) -> dict[str, float | int | str]:
        """현재 집계 상태를 보고 형식으로 반환 (KPI 권고치 비교 가능)."""
        n = self.candidates_total or 1
        return {
            "report_kst": datetime.now(KST).isoformat(timespec="seconds"),
            "candidates_total": self.candidates_total,
            "passed_to_review": self.passed_to_review,
            "held": self.held,
            "rejected": self.rejected,
            "audit_completeness": round(self.audit_complete / n, 4),
            "ttrr_p50_sec": self.percentile(50),
            "ttrr_p95_sec": self.percentile(95),
            "ttrr_p99_sec": self.percentile(99),
        }


def time_to_review_ready(
    ingest_at_kst: str,
    review_ready_at_kst: str,
) -> float:
    """단일 케이스의 첩보→검토준비 소요시간(초)."""
    t0 = datetime.fromisoformat(ingest_at_kst)
    t1 = datetime.fromisoformat(review_ready_at_kst)
    return (t1 - t0).total_seconds()
