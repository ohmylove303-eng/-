"""K-AFAS 시각화 레이어 시스템.

인간 검토자가 언제든지 레이어를 커스텀하고 토글할 수 있도록 설계.
실제 렌더링은 외부 GIS(Cesium/Deck.gl/QGIS/MapLibre 등)에서 수행하며,
이 패키지는 레이어 메타데이터와 표시 정책만 표준화한다.

REJECT: 무기제어 화면, 포탑 카메라 직접 표시, 사격 카운트다운.
"""
from kafas.viz import layers, custom, console

__all__ = ["layers", "custom", "console"]
