# 시각화 레이어 명세 (kafas/viz)

## 표준 레이어 15종

| layer_id | 한글 | 영문 | 기본표시 | 출처 힌트 |
|---|---|---|---|---|
| terrain | 지형 | Terrain | ✓ | DTED/SRTM/DEM/위성 |
| transport | 교통망 | Transport | ✓ | OSM road/rail |
| hydrology | 수계 | Hydrology | | OSM water |
| civilian_areas | 민간거주·시설 | Civilian Areas | ✓ | OSM amenity |
| restricted_zones | 제한구역 | Restricted Zones | ✓ | ROE/공역 |
| friendly_forces | 아군 위치 | Friendly Forces | ✓ | BFT |
| deconfliction | 임무 충돌영역 | Deconfliction | ✓ | 인접부대 임무 |
| threat_layer | 적 위험도 | Threat | ✓ | 다중출처 분석 |
| target_candidates | 표적후보 | Target Candidates | ✓ | L4 결과 |
| evidence_markers | 증거 마커 | Evidence Markers | | 출처별 marker |
| freshness_heatmap | 정보신선도 | Freshness Heatmap | ✓ | L3 |
| coord_quality | 좌표품질 | Coordinate Quality | ✓ | L5 |
| risk_gate_overlay | 안전게이트 결과 | Safety Gate | ✓ | L6 |
| review_queue | 검토 대기열 | Review Queue | ✓ | L7 |
| audit_trail | 감사 추적 | Audit Trail | | L8 hashchain |

## 4-패널 검토 콘솔

| 패널 | 사용 레이어 | 허용 인터랙션 |
|---|---|---|
| 지도 | terrain~review_queue | pan/zoom/tilt/toggle/filter/select/add_custom |
| 증거 | evidence_markers | play_video/view_report/compare_sources |
| 의사결정 | review_queue | request_more / hold / reject / approve_for_next_review |
| 감사 | audit_trail | replay_case / verify_chain / export_report |

## 금지 인터랙션 (절대 노출 금지)
```
fire, release_weapon, open_turret_view, send_fire_command,
auto_engage, select_munition, compute_firing_solution
```

## 사용자 정의 레이어 규칙
1. `display_only=True` 강제 (사격제원으로 사용 불가)
2. 금지 키워드 포함 시 `add_custom()` 호출이 ValueError로 차단
3. z_order로 그리기 순서 제어 (작을수록 아래)
4. 검토자 역할별 기본 설정은 `default_config_for(role)` 사용

## 외부 렌더링 권장 스택 (`docs/ECOSYSTEM.md` 참조)
- 2D: Leaflet / MapLibre GL / Mapbox / Deck.gl
- 3D: CesiumJS (실 지형 + 표적후보 3D 표시)
- 데스크톱: QGIS (오프라인/분석)
- 야전 단말: ATAK + CoT 메시지 연동 (Cursor on Target)
