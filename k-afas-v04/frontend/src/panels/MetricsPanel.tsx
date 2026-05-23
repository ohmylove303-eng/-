/**
 * MetricsPanel — 시뮬레이션 지표 패널
 *
 * 표시: TTSR, 시나리오별 성공률, 검토흐름 6단계 스택바
 * 금지: Time-to-Fire, Kill Rate, 무기 효율
 * DISPLAY_ONLY 안전 문구 필수
 */
import { MetricsPanelProps, Scenario, StageKey } from "../types/kafas";
import "./MetricsPanel.css";

const scenarioLabel: Record<Scenario, string> = {
  CLEAN: "정상망(Clean)",
  DEGRADED: "저하망(Degraded)",
  CONTESTED: "경합망(Contested)",
};

const scenarioColor: Record<Scenario, string> = {
  CLEAN: "#22c55e",
  DEGRADED: "#eab308",
  CONTESTED: "#ef4444",
};

const stageLabel: Record<StageKey, string> = {
  SENSOR: "센서(Sensor)",
  AI: "AI분석(AI)",
  TRACK: "트랙품질(Track)",
  REVIEW_PACKAGE: "검토패키지(Review)",
  HITL: "인간검토(HITL)",
  LINK: "연동상태(Link)",
};

const stageColor: Record<StageKey, string> = {
  SENSOR: "#38bdf8",
  AI: "#a78bfa",
  TRACK: "#34d399",
  REVIEW_PACKAGE: "#fbbf24",
  HITL: "#fb7185",
  LINK: "#94a3b8",
};

function getScenarioClass(scenario: Scenario): string {
  return `scenario-${scenario.toLowerCase()}`;
}

function formatSec(v: number): string {
  return Number.isFinite(v) ? `${v.toFixed(1)}s` : "-";
}

export default function MetricsPanel({ metrics, targetId }: MetricsPanelProps) {
  const currentStat = metrics.statsByScenario.find(
    (s) => s.scenario === metrics.currentScenario
  );

  const stageTotal = metrics.stagesForScenario.reduce(
    (sum, s) => sum + s.meanSec, 0
  );

  return (
    <section className="metrics-panel" aria-label="시뮬레이션 메트릭 패널">
      {/* 헤더 */}
      <div className="metrics-header">
        <div>
          <h3>시뮬레이션 지표(Simulation Metrics)</h3>
          <p>대상: <strong>{targetId ?? "선택 없음"}</strong></p>
        </div>
        <div className={`scenario-badge ${getScenarioClass(metrics.currentScenario)}`}>
          {scenarioLabel[metrics.currentScenario]}
        </div>
      </div>

      {/* 3카드 */}
      <div className="metrics-grid">
        <div className="metric-card primary">
          <span className="metric-label">TTSR</span>
          <strong>{formatSec(metrics.ttsrSec)}</strong>
          <small>첩보→검토준비</small>
        </div>
        <div className="metric-card">
          <span className="metric-label">성공률(Success)</span>
          <strong>{currentStat ? `${currentStat.successRatePct.toFixed(1)}%` : "-"}</strong>
          <small>현재 시나리오 기준</small>
        </div>
        <div className="metric-card">
          <span className="metric-label">평균지연(Mean)</span>
          <strong>{currentStat ? formatSec(currentStat.meanLatencySec) : "-"}</strong>
          <small>검토흐름 평균</small>
        </div>
      </div>

      {/* 시나리오별 성공률 바 */}
      <div className="chart-block">
        <div className="chart-title">시나리오별 성공률(Success Rate by Scenario)</div>
        <div className="success-bars">
          {metrics.statsByScenario.map((s) => (
            <div key={s.scenario} className="bar-row">
              <span className="bar-label">{scenarioLabel[s.scenario]}</span>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${s.successRatePct}%`, background: scenarioColor[s.scenario] }}
                />
              </div>
              <span className="bar-val" style={{ color: scenarioColor[s.scenario] }}>
                {s.successRatePct.toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* 검토흐름 6단계 스택바 */}
      <div className="chart-block">
        <div className="chart-title">검토흐름 단계별 지연(Review Flow Stage Latency)</div>
        <div className="stage-stack">
          {metrics.stagesForScenario.map((stage) => {
            const widthPct = stageTotal > 0
              ? Math.max((stage.meanSec / stageTotal) * 100, 4)
              : 0;
            return (
              <div
                key={stage.stage}
                className="stage-seg"
                style={{ width: `${widthPct}%`, background: stageColor[stage.stage] }}
                title={`${stageLabel[stage.stage]} · ${formatSec(stage.meanSec)}`}
              >
                {stage.stage.slice(0, 3)}
              </div>
            );
          })}
        </div>
        <div className="stage-legend">
          {metrics.stagesForScenario.map((stage) => (
            <div key={stage.stage} className="legend-item">
              <span className="legend-dot" style={{ background: stageColor[stage.stage] }} />
              <span>{stageLabel[stage.stage]}</span>
              <strong>{formatSec(stage.meanSec)}</strong>
            </div>
          ))}
        </div>
      </div>

      {/* 안전 문구 */}
      <div className="metrics-safety-note">
        표시전용(DISPLAY_ONLY): 본 패널은 시뮬레이션·검토지표만 표시하며
        자동사격(Autonomous Fire), 사격제원(Firing Data), 탄도계산(Ballistic Calculation)을 수행하지 않습니다.
      </div>
    </section>
  );
}
