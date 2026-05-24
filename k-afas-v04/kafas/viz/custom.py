"""사용자 정의 레이어 토글/커스텀.

검토자(role별)에 따라 레이어 표시·숨김을 제어할 수 있다.
무기 직접연동, 사격 카운트다운, 포탑 카메라 직접 표시 같은
'행동 자동화' 시각화는 절대 추가 불가.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable

from kafas.viz.layers import STANDARD_LAYERS, LayerSpec

_FORBIDDEN_LAYER_KEYWORDS = (
    "fire_control", "weapon_release", "turret",
    "kill_chain_view", "strike_planner", "fire_command_panel",
    "사격제원", "사격지시", "발사명령",
)


@dataclass
class LayerConfig:
    """단일 사용자/세션의 레이어 표시 설정."""
    role: str                                 # commander / analyst / safety_officer / auditor
    visible_ids: set[str] = field(default_factory=set)
    custom_layers: list[LayerSpec] = field(default_factory=list)

    def toggle(self, layer_id: str, on: bool) -> None:
        if on:
            self.visible_ids.add(layer_id)
        else:
            self.visible_ids.discard(layer_id)

    def add_custom(self, spec: LayerSpec) -> None:
        # 금지 키워드가 layer_id, name, source에 들어가면 거부.
        blob = " ".join(
            [spec.layer_id, spec.name_ko, spec.name_en, spec.source_hint]
        ).lower()
        for kw in _FORBIDDEN_LAYER_KEYWORDS:
            if kw.lower() in blob:
                raise ValueError(f"forbidden_custom_layer:{kw}")
        if not spec.display_only:
            raise ValueError("display_only_required_true")
        self.custom_layers.append(spec)

    def resolve(self) -> list[LayerSpec]:
        """현재 설정에 따라 보여줄 레이어 목록 반환 (z_order 정렬)."""
        all_layers = list(STANDARD_LAYERS) + list(self.custom_layers)
        visible = [
            l for l in all_layers
            if l.layer_id in self.visible_ids or l.default_visible
        ]
        return sorted(visible, key=lambda l: l.z_order)


def default_config_for(role: str) -> LayerConfig:
    """역할별 권장 기본 설정."""
    cfg = LayerConfig(role=role)
    # 모든 default_visible 레이어를 켠다 (이후 사용자가 토글 가능).
    for l in STANDARD_LAYERS:
        if l.default_visible:
            cfg.visible_ids.add(l.layer_id)
    return cfg
