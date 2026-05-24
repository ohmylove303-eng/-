"""인간 검토 콘솔(Review Console) 구조 명세.

이 모듈은 UI를 직접 그리지 않는다. 다음을 정의한다:
  - 콘솔에 표시할 4개 패널 구조
  - 각 패널이 사용하는 표준 레이어/데이터
  - 사용자 인터랙션의 화이트리스트 (REJECT 행동 차단)
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class PanelSpec:
    panel_id: str
    title_ko: str
    bound_layers: tuple[str, ...]
    interactions: tuple[str, ...]


# 4-패널 표준 레이아웃
PANELS: tuple[PanelSpec, ...] = (
    PanelSpec(
        "map_panel", "지도/지형/레이어 패널",
        bound_layers=(
            "terrain", "transport", "hydrology",
            "civilian_areas", "restricted_zones",
            "friendly_forces", "deconfliction", "threat_layer",
            "target_candidates", "freshness_heatmap",
            "coord_quality", "risk_gate_overlay",
        ),
        interactions=(
            "pan", "zoom", "tilt",
            "toggle_layer", "filter_by_freshness",
            "filter_by_quality", "select_candidate",
            "add_custom_layer",
        ),
    ),
    PanelSpec(
        "evidence_panel", "증거 검토 패널",
        bound_layers=("evidence_markers",),
        interactions=(
            "play_video_clip", "view_observer_report",
            "view_sensor_event", "compare_sources",
        ),
    ),
    PanelSpec(
        "decision_panel", "의사결정 지원 패널",
        bound_layers=("review_queue",),
        interactions=(
            "request_more_evidence", "hold",
            "reject", "approve_for_next_review",
        ),
    ),
    PanelSpec(
        "audit_panel", "감사 패널",
        bound_layers=("audit_trail",),
        interactions=(
            "replay_case", "verify_chain", "export_report",
        ),
    ),
)


# 절대 콘솔에 노출 금지 (REJECT)
FORBIDDEN_INTERACTIONS = frozenset({
    "fire", "release_weapon", "open_turret_view",
    "send_fire_command", "auto_engage", "select_munition",
    "compute_firing_solution",
})
