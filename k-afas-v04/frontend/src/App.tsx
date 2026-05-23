/**
 * K-AFAS v0.4.1 검토 콘솔 — 4-패널 레이아웃
 *
 * ┌─────────────────────────────────┬──────────────────┐
 * │                                 │  Evidence Panel   │
 * │         Map Panel (60%)         │     (40% top)     │
 * │                                 ├──────────────────┤
 * │                                 │  Decision Panel   │
 * │                                 │   (40% mid)       │
 * │                                 ├──────────────────┤
 * │                                 │   Audit Panel     │
 * │                                 │   (40% bottom)    │
 * └─────────────────────────────────┴──────────────────┘
 *
 * 핵심 결정: 무기/사격/발사 관련 UI 요소 절대 금지
 */
import { useState, useEffect, useCallback } from "react";
import MapPanel from "./panels/MapPanel";
import EvidencePanel from "./panels/EvidencePanel";
import DecisionPanel from "./panels/DecisionPanel";
import AuditPanel from "./panels/AuditPanel";
import { CaseResponse } from "./types";
import { fetchCases, subscribeCases } from "./api";
import "./App.css";

export default function App() {
  const [cases, setCases] = useState<CaseResponse[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseResponse | null>(null);
  const [connected, setConnected] = useState(false);

  // 초기 데이터 로드 (mock 또는 API)
  useEffect(() => {
    fetchCases().then((data) => {
      setCases(data);
      if (data.length > 0) setSelectedCase(data[0]);
    });
  }, []);

  // WebSocket 실시간 스트림
  useEffect(() => {
    const unsub = subscribeCases((newCase) => {
      setCases((prev) => [newCase, ...prev]);
      setConnected(true);
    });
    return unsub;
  }, []);

  const handleSelectCase = useCallback((c: CaseResponse) => {
    setSelectedCase(c);
  }, []);

  return (
    <div className="console-root">
      {/* 헤더 */}
      <header className="console-header">
        <h1 className="console-title">K-AFAS 검토 콘솔</h1>
        <div className="console-status">
          <span className={`status-dot ${connected ? "online" : "offline"}`} />
          <span>{connected ? "실시간 연결" : "오프라인"}</span>
          <span className="case-count">대기 {cases.length}건</span>
        </div>
      </header>

      {/* 4-패널 그리드 */}
      <main className="console-grid">
        <section className="panel panel-map">
          <MapPanel cases={cases} selectedCase={selectedCase} onSelect={handleSelectCase} />
        </section>
        <section className="panel panel-evidence">
          <EvidencePanel selectedCase={selectedCase} />
        </section>
        <section className="panel panel-decision">
          <DecisionPanel selectedCase={selectedCase} />
        </section>
        <section className="panel panel-audit">
          <AuditPanel cases={cases} />
        </section>
      </main>
    </div>
  );
}
