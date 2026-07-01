import { html } from 'htm/preact';

const SEGMENTS = 20; // 5%-Schritte

/** Tipp-Lautstärkeleiste: ganze Leiste antippen → rastet auf 5% (DESIGN §6). */
export function SegBar({ value = 0, onSet }) {
  const filled = Math.round(value / 5);
  const pick = (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    const frac = (e.clientX - r.left) / r.width;
    const level = Math.max(0, Math.min(100, Math.round(frac * SEGMENTS) * 5));
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
    ${Array.from(
      { length: SEGMENTS },
      (_, i) => html`<span class="segbar__seg ${i < filled ? 'is-on' : ''}"></span>`
    )}
  </div>`;
}
