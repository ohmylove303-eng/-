"""K-AFAS v0.4 — 한국형 지능형 포병 의사결정 지원체계.

Korean Artillery AI Decision-support System (Decision Support Only).

엄격 금지: 자동사격, 사격제원, 탄도계산, 무기 직접연동, 포탑제어,
         발사명령, 사격지시, 특정 표적 공격절차, 재밍 회피 구현.

공개 모듈:
  schemas      : 7개 데이터 객체 TypedDict
  harness      : 6개 불변조건 검증
  validators   : 진입점 런타임 dict 검증
  metrics      : KPI (Time-to-Review-Ready 포함, Time-to-Fire 금지)
  pipeline     : 8계층 통합 + run/run_batch
  layers       : L1~L9
  viz          : 시각화 레이어/콘솔 명세
"""
__version__ = "0.4.1"
__all__ = [
    "schemas", "harness", "validators", "metrics",
    "pipeline", "layers", "viz",
]
