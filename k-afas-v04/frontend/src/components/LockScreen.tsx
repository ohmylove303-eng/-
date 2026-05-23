/**
 * LockScreen — 세션 만료 시 화면 잠금 오버레이
 * 모든 패널 위에 렌더링. 재인증까지 조작 차단.
 */
import { useState } from "react";

interface Props {
  onUnlock: (token: string) => boolean;
}

export default function LockScreen({ onUnlock }: Props) {
  const [token, setToken] = useState("");
  const [error, setError] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const ok = onUnlock(token);
    if (!ok) {
      setError(true);
      setToken("");
    }
  };

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 9999,
      background: "rgba(15, 23, 42, 0.95)",
      backdropFilter: "blur(8px)",
      display: "flex", alignItems: "center", justifyContent: "center",
      flexDirection: "column", gap: "16px",
    }}>
      <div style={{ fontSize: "48px" }}>🔒</div>
      <h2 style={{ color: "#f1f5f9", fontSize: "18px", fontWeight: 700 }}>
        세션 만료 — 재인증 필요
      </h2>
      <p style={{ color: "#94a3b8", fontSize: "12px", maxWidth: "300px", textAlign: "center" }}>
        5분간 활동이 없어 보안 잠금되었습니다.<br/>
        인증 토큰을 입력하여 잠금 해제하세요.
      </p>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "8px" }}>
        <input
          type="password"
          value={token}
          onChange={(e) => { setToken(e.target.value); setError(false); }}
          placeholder="인증 토큰"
          autoFocus
          style={{
            padding: "8px 12px", borderRadius: "6px",
            border: error ? "2px solid #ef4444" : "1px solid #334155",
            background: "#1e293b", color: "#f1f5f9",
            fontSize: "14px", width: "200px",
          }}
        />
        <button
          type="submit"
          style={{
            padding: "8px 16px", borderRadius: "6px",
            background: "#3b82f6", color: "#fff",
            border: "none", fontWeight: 600, cursor: "pointer",
          }}
        >
          잠금 해제
        </button>
      </form>
      {error && (
        <span style={{ color: "#ef4444", fontSize: "11px" }}>토큰이 유효하지 않습니다</span>
      )}
    </div>
  );
}
