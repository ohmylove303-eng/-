/**
 * DISPLAY_ONLY 보안 가드
 * - 레이어 정규화 (string[] → LayerDefinition[])
 * - 금지 키워드 검증
 * - 좌표 클립보드/우클릭/드래그 차단
 */
import { LayerDefinition } from "../types/kafas";

// 금지 키워드 (기능명/API명/버튼명으로 사용 불가)
const FORBIDDEN_KEYWORDS = [
  "fire_control", "weapon_release", "turret",
  "kill_chain", "firing_solution",
  "사격제원", "사격지시", "발사명령",
  "autonomous_fire", "ballistic",
];

/**
 * 기존 layers:string[] + activeLayers:string[] → LayerDefinition[] 변환
 * displayOnly=true 강제. 금지 키워드 포함 레이어 제거.
 */
export function normalizeLayers(
  layers: string[],
  activeLayers: string[]
): LayerDefinition[] {
  return layers
    .filter((id) => !isForbiddenLayer(id))
    .map((id) => ({
      id,
      label: id,
      active: activeLayers.includes(id),
      displayOnly: true as const,
    }));
}

/** 금지 키워드 포함 여부 */
export function isForbiddenLayer(layerId: string): boolean {
  const lower = layerId.toLowerCase();
  return FORBIDDEN_KEYWORDS.some((kw) => lower.includes(kw.toLowerCase()));
}

/** 클립보드 복사 차단 이벤트 핸들러 */
export function blockClipboard(e: ClipboardEvent): void {
  e.preventDefault();
}

/** 우클릭 차단 */
export function blockContextMenu(e: MouseEvent): void {
  e.preventDefault();
}

/** 드래그 차단 */
export function blockDrag(e: DragEvent): void {
  e.preventDefault();
}

/**
 * 지도 컨테이너에 DISPLAY_ONLY 보안 이벤트 등록
 * cleanup 함수 반환
 */
export function attachDisplayOnlyGuards(el: HTMLElement): () => void {
  el.addEventListener("copy", blockClipboard as EventListener);
  el.addEventListener("contextmenu", blockContextMenu as EventListener);
  el.addEventListener("dragstart", blockDrag as EventListener);

  return () => {
    el.removeEventListener("copy", blockClipboard as EventListener);
    el.removeEventListener("contextmenu", blockContextMenu as EventListener);
    el.removeEventListener("dragstart", blockDrag as EventListener);
  };
}
