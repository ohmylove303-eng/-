# K-AFAS 적용 가능 기술/제품/OSS 전체 나열

> 본 문서는 K-AFAS 8계층(L1~L8)에 **현재 시점에서 실제로 채택 가능한**
> 시스템·제품·오픈소스를 카테고리별로 정리한다.
> 표시: 🇰🇷 한국, 🇺🇦 우크라이나(전장 검증), 🇺🇸/🇪🇺 NATO/미국,
> 🟢 OSS, 💼 상용, 🛠 표준.

## 1. 전장관리·지휘통제(C2) 참조 시스템

| 시스템 | 출처 | K-AFAS 매핑 | 비고 |
|---|---|---|---|
| ATCIS / AKJCCS / KCCS-A | 🇰🇷 | L3 COP, L7 의사결정 지원 | 국방부/DAPA, 2026~2029 단계 배치 |
| 화력감시정찰체계(K-CFISR) | 🇰🇷 | L1 ingest, L3 COP | 군 운용 데이터 표준화 |
| Delta | 🇺🇦 | L3 COP, L4 detection | 무인기·위성·센서 통합 |
| Vezha | 🇺🇦 | L4 detection (영상 라우팅) | 영상 스트리밍 |
| Avengers | 🇺🇦 | L4 detection (객체 식별) | 주당 12,000개 차량 탐지 |
| Mission Control | 🇺🇦 | L7 의사결정 지원 | 드론 임무관리 |
| GIS Arta | 🇺🇦 | L5 좌표 표시·지원 | 전술 화력지원 의사결정(참고) |
| Kropyva | 🇺🇦 | L3 COP (현장 단말) | 태블릿 기반 |
| Maven Smart System | 🇺🇸 | L3·L4·L7 | NATO 채택, 표적 추천 + 인간 승인 |
| AFATDS / AXS | 🇺🇸 | L7 (참고만) | 화력 의사결정 — K-AFAS는 차용 X |
| IBCS | 🇺🇸 | L3·L6 표준연동 참고 | "Any Sensor, Any Shooter" |
| ATAK / CivTAK | 🇺🇸 🟢 | L3 COP UI | 안드로이드 전술 정보표시 |
| Project Convergence | 🇺🇸 | 통합 참고 | JADC2 실험 |
| Anduril Lattice | 🇺🇸 💼 | L4·L7 참고 | 자율탐지 + HiTL |
| Palantir AIP / Foundry | 🇺🇸 💼 | L1~L7 데이터 통합 | 기관급 데이터 메시 |

## 2. 영상분석·AI 모델 (L4 후보탐지)

| 항목 | 종류 | 비고 |
|---|---|---|
| YOLOv9 / Ultralytics | 🟢 | 실시간 객체 탐지, ONNX/TensorRT 변환 가능 |
| MMDetection / MMRotate | 🟢 | OpenMMLab, 회전박스(항공·위성용) |
| Detectron2 | 🟢 | Meta, 인스턴스 분할 |
| Roboflow Train/Deploy | 💼 | 데이터셋·모델 파이프라인 |
| OpenCV | 🟢 | 전처리/모션탐지 기본 |
| NVIDIA DeepStream | 💼 | 다중 스트림 영상 추론 파이프라인 |
| Triton Inference Server | 🟢 | 모델 서빙 |
| ONNX Runtime / TensorRT | 🟢 | 엣지 추론 가속 |
| NVIDIA Jetson AGX/Orin | 💼 | 야전 엣지 GPU |
| Hailo-8 / Coral TPU | 💼 | 저전력 엣지 가속기 |

## 3. 지도/3D/지형 (L3 COP, viz/layers)

| 항목 | 종류 | 비고 |
|---|---|---|
| OpenStreetMap | 🟢 | 도로·시설·민간지물 (viz: civilian_areas, transport) |
| QGIS | 🟢 | 데스크톱 분석 |
| GDAL/OGR | 🟢 | 좌표·포맷 변환 |
| Cesium / CesiumJS | 🟢/💼 | 3D 글로브, 실 지형 + 시각화 |
| MapLibre GL / Mapbox | 🟢/💼 | 2D 벡터 지도 |
| Leaflet | 🟢 | 경량 2D 지도 |
| Deck.gl | 🟢 | WebGL 대용량 시각화 (히트맵·점) |
| GeoServer | 🟢 | OGC WMS/WMTS 서비스 |
| SRTM / DTED / DEM | 🛠 | 표고 데이터 |
| Sentinel-2 / Landsat | 🟢 | 위성영상 (라이선스 확인) |



## 4. 데이터링크/메시징/통신 (L1 ingest, L3 COP 동기화)

| 항목 | 종류 | 비고 |
|---|---|---|
| Link 16 (MIDS-LVT/JREAP) | 🛠 | 한미 공유 표준, 115.2 kbps |
| Link 22 (NILE) | 🛠 | 저속·고생존성 |
| MUOS / 위성 | 🛠 | 64 kbps 위성 |
| TACNet-K | 🇰🇷 | 미래 목표 500 kbps [추론] |
| Cursor on Target (CoT) | 🛠 🟢 | ATAK 표준 메시지 |
| NATO STANAG 4609 | 🛠 | Motion Imagery (UAV 영상) |
| MISB 0601 KLV | 🛠 | 영상 메타데이터(위치/시각/센서) |
| ZeroMQ / NATS / MQTT | 🟢 | 내부 메시지 버스 |
| Apache Kafka / Pulsar | 🟢 | 이벤트 스트리밍 |
| gRPC / Protobuf | 🟢 | 서비스간 RPC |

## 5. 보안·감사·신원 (L8 audit, L9 audit_gate)

| 항목 | 종류 | 비고 |
|---|---|---|
| HashiCorp Vault | 🟢/💼 | 비밀/토큰 관리 |
| FIDO2 / WebAuthn | 🛠 | 검토자 하드웨어 키 |
| OpenID Connect / OAuth 2.1 | 🛠 | 신원·인가 |
| mTLS (X.509) | 🛠 | 서비스간 상호 인증 |
| Sigstore / cosign | 🟢 | 모델·아티팩트 서명 |
| in-toto / SLSA | 🟢 | 공급망 무결성 |
| Hyperledger Indy/Fabric | 🟢 | 감사로그 분산 원장 (선택) |
| Linux audit / OSQuery | 🟢 | 호스트 감사 |
| KMS / HSM | 💼 | 키 관리 |

## 6. ML 학습·운영(MLOps) — 모델 자동갱신은 금지

| 항목 | 종류 | 비고 |
|---|---|---|
| PyTorch / TensorFlow | 🟢 | 학습 프레임워크 |
| Hugging Face | 🟢 | 모델 허브 (검증된 가중치만) |
| MLflow / Weights & Biases | 🟢/💼 | 실험 추적 |
| DVC / LakeFS | 🟢 | 데이터 버전관리 |
| Kubeflow / Argo | 🟢 | 파이프라인 |
| Determined / Ray | 🟢 | 분산 학습 |

> ⚠️ AAR 통과 + 인간승인 + 보안검토를 거치지 않은 자동 재학습은 금지
> (`model_update_allowed: False`, `review_required_before_training: True`).

## 7. 시뮬레이션·훈련 (실전 연결 전 검증)

| 항목 | 종류 | 비고 |
|---|---|---|
| OneSAF / JCATS | 💼 | 미군 합동 시뮬레이션 |
| VBS4 (Bohemia) | 💼 | 가상 전장 |
| Unreal Engine + AirSim | 🟢 | UAV 영상 합성 |
| Gazebo | 🟢 | 로봇 시뮬레이션 |
| MOOS-IvP | 🟢 | 무인 해상 시뮬레이션 |

## 8. 운영체제·인프라 (실전 환경)

| 항목 | 종류 | 비고 |
|---|---|---|
| Red Hat Enterprise Linux / Rocky | 💼/🟢 | 서버 OS |
| Kubernetes / k3s | 🟢 | 엣지 오케스트레이션 |
| Nomad + Consul | 🟢 | 경량 대안 |
| eBPF / Cilium | 🟢 | 네트워크 격리 (무기제어망 분리 보조) |
| AppArmor / SELinux | 🟢 | MAC 정책 |
| Tang / Clevis | 🟢 | 디스크 자동 잠금 |

## 9. 표준·정책 참조

| 항목 | 종류 | 비고 |
|---|---|---|
| MIL-STD-810H | 🛠 | 환경시험 표준(맞춤화) |
| MIL-STD-461G | 🛠 | EMI/EMC |
| DoD Directive 3000.09 | 🛠 | 자율무기 정책 |
| NATO AAP-15 | 🛠 | 용어 표준 |
| ISO/IEC 27001 / 27017 | 🛠 | 보안 |
| OGC GeoPackage / WMTS | 🛠 | 지리공간 표준 |

## 10. 한국 공공 데이터 (참고용)

| 항목 | 출처 | 비고 |
|---|---|---|
| 국가공간정보포털 (NSDI) | 🇰🇷 | 도로·건물·행정경계 |
| V-WORLD | 🇰🇷 | 3D 공간정보 |
| 기상청 OpenAPI | 🇰🇷 | 기상 데이터 (L1) |
| 통계청 SGIS | 🇰🇷 | 인구·민간지역 |
| 국토지리정보원 DEM | 🇰🇷 | 표고 |

> ⚠️ 위 항목 전체에서 "사격제원/탄도계산/자동사격/포탑제어/발사명령"
> 기능을 **K-AFAS 코드/UI/연동에 도입하는 것은 금지**.
> 해당 기능은 별도 인가받은 무기체계(분리망)에서 인간 권한자가 수행.
