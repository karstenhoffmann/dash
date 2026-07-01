import { html } from 'htm/preact';

const STEP = 5; // 5%-Raster

/** Tipp-Lautstärkeleiste: ganze Leiste antippen → rastet auf 5% (DESIGN §6).
 * Füllung reist als Inline-Custom-Property (Datenkanal, ADR-0009). */
export function SegBar({ value = 0, onSet }) {
  const pick = (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    const frac = (e.clientX - r.left) / r.width;
    const level = Math.max(0, Math.min(100, Math.round((frac * 100) / STEP) * STEP));
    onSet?.(level);
  };
  return html`<div
    class="segbar"
    role="slider"
    aria-valuemin="0"
    aria-valuemax="100"
    aria-valuenow=${value}
    aria-label="Gruppen-Lautstärke"
    onClick=${pick}
  >
    <div class="segbar__fill" style=${{ '--seg-fill': `${value}%` }}></div>
    <div class="segbar__ticks"></div>
  </div>`;
}
