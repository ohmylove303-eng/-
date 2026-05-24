"""표준 시각화 레이어 정의.

각 레이어는 (id, name, display_only, default_visible, source) 메타를 갖는다.
display_only=True 인 레이어는 인간 판단 보조용일 뿐이며,
좌표값을 사격제원으로 사용할 수 없다 (정책 잠금).
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class LayerSpec:
    layer_id: str
    name_ko: str
    name_en: str
    default_visible: bool
    display_only: bool   # 항상 True 권장
    source_hint: str     # 데이터 출처(자유 문자열)
    z_order: int         # 그리기 순서(작을수록 아래)


STANDARD_LAYERS: tuple[LayerSpec, ...] = (
    LayerSpec("terrain", "지형", "Terrain",
              True, True, "DTED/SRTM/DEM/위성영상", 0),
    LayerSpec("transport", "교통망", "Transport",
              True, True, "OSM road/rail", 5),
    LayerSpec("hydrology", "수계", "Hydrology",
              False, True, "OSM water", 6),
    LayerSpec("civilian_areas", "민간거주·시설", "Civilian Areas",
              True, True, "OSM amenity (school/hospital/place)", 10),
    LayerSpec("restricted_zones", "제한구역", "Restricted Zones",
              True, True, "ROE/공역제한 데이터", 15),
    LayerSpec("friendly_forces", "아군 위치", "Friendly Forces",
              True, True, "Blue Force Tracking (BFT)", 20),
    LayerSpec("deconfliction", "임무 충돌영역", "Deconfliction",
              True, True, "인접부대 임무영역 / 공역", 25),
    LayerSpec("threat_layer", "적 위험도", "Threat",
              True, True, "위협분석/근거 다중출처", 30),
    LayerSpec("target_candidates", "표적후보", "Target Candidates",
              True, True, "L4 후보탐지 결과", 40),
    LayerSpec("evidence_markers", "증거 마커", "Evidence Markers",
              False, True, "출처별 marker (UAV/관측/센서/위성)", 41),
    LayerSpec("freshness_heatmap", "정보신선도", "Freshness Heatmap",
              True, True, "L3 GREEN/YELLOW/RED/BLACK", 45),
    LayerSpec("coord_quality", "좌표품질", "Coordinate Quality",
              True, True, "L5 HIGH/MEDIUM/LOW", 46),
    LayerSpec("risk_gate_overlay", "안전게이트 결과", "Safety Gate Overlay",
              True, True, "L6 PASS/HOLD/REJECT", 50),
    LayerSpec("review_queue", "검토 대기열", "Review Queue",
              True, True, "L7 의사결정 지원 큐", 60),
    LayerSpec("audit_trail", "감사 추적", "Audit Trail",
              False, True, "L8 JSONL 해시체인", 70),
)
