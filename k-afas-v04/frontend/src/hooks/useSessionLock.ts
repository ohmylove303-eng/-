/**
 * useSessionLock — R19 세션 5분 비활동 자동잠금
 *
 * 정책:
 * - 5분(300초) 비활동 → 화면 잠금 + 재인증 요구
 * - 활동: mouse/keyboard/touch 이벤트
 * - 잠금 시: 모든 패널 블러 + 재인증 모달
 * - 토큰 만료 시 API 호출 차단
 */
import { useState, useEffect, useCallback, useRef } from "react";

const LOCK_TIMEOUT_MS = 5 * 60 * 1000; // 5분

export interface SessionState {
  locked: boolean;
  remainingSec: number;
  unlock: (token: string) => boolean;
  resetTimer: () => void;
}

export function useSessionLock(): SessionState {
  const [locked, setLocked] = useState(false);
  const [remainingSec, setRemainingSec] = useState(LOCK_TIMEOUT_MS / 1000);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastActivityRef = useRef(Date.now());

  const lock = useCallback(() => {
    setLocked(true);
    setRemainingSec(0);
    if (countdownRef.current) clearInterval(countdownRef.current);
  }, []);

  const resetTimer = useCallback(() => {
    lastActivityRef.current = Date.now();
    setRemainingSec(LOCK_TIMEOUT_MS / 1000);

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(lock, LOCK_TIMEOUT_MS);
  }, [lock]);

  const unlock = useCallback((token: string): boolean => {
    // 간단 검증: 빈 토큰 거부
    if (!token || token.length < 3) return false;
    setLocked(false);
    resetTimer();
    return true;
  }, [resetTimer]);

  // 활동 감지 이벤트 등록
  useEffect(() => {
    const events = ["mousemove", "keydown", "touchstart", "click", "scroll"];

    const handler = () => {
      if (!locked) resetTimer();
    };

    events.forEach((e) => window.addEventListener(e, handler, { passive: true }));
    resetTimer(); // 초기 타이머

    // 남은 시간 카운트다운
    countdownRef.current = setInterval(() => {
      if (!locked) {
        const elapsed = Date.now() - lastActivityRef.current;
        const remaining = Math.max(0, Math.ceil((LOCK_TIMEOUT_MS - elapsed) / 1000));
        setRemainingSec(remaining);
      }
    }, 1000);

    return () => {
      events.forEach((e) => window.removeEventListener(e, handler));
      if (timerRef.current) clearTimeout(timerRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, [locked, resetTimer]);

  return { locked, remainingSec, unlock, resetTimer };
}
