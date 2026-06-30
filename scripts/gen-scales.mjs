#!/usr/bin/env node
/**
 * Utopia-Generator für fluide Typo-/Space-Scales → web/tokens/scale.css.
 *
 * Erzeugt clamp()-Werte (min @ MIN_VW … max @ MAX_VW) nach der Utopia-Logik
 * (https://utopia.fyi). Ausgabe ist STATISCHES CSS — die einzige Stelle im
 * Projekt, an der clamp()/px-Mathematik leben darf (ADR-0003/0007).
 *
 * Lauf:  node scripts/gen-scales.mjs > web/tokens/scale.css
 *
 * Das Token-Set ist GESCHLOSSEN. Neue Stufe/Token nur per ADR (ADR-0007) —
 * nicht hier „mal eben" eine Zeile dazu.
 */

const MIN_VW = 320;
const MAX_VW = 1240;
const REM = 16;

/** clamp(min … max) als Utopia-Interpolation zwischen MIN_VW und MAX_VW. */
function fluid(minPx, maxPx) {
  const minRem = minPx / REM;
  const maxRem = maxPx / REM;
  const slope = (maxPx - minPx) / (MAX_VW - MIN_VW);
  const interceptRem = (minPx - slope * MIN_VW) / REM;
  const slopeVw = slope * 100;
  const lo = Math.min(minRem, maxRem);
  const hi = Math.max(minRem, maxRem);
  return `clamp(${r(lo)}rem, ${r(interceptRem)}rem + ${r(slopeVw)}vw, ${r(hi)}rem)`;
}
const r = (n) => Number(n.toFixed(4)).toString();

// --- Typo-Scale: Basis 16→18, Ratio 1.2 (minor third) → 1.25 (major third) ---
const TYPE_MIN_BASE = 16;
const TYPE_MAX_BASE = 18;
const TYPE_MIN_RATIO = 1.2;
const TYPE_MAX_RATIO = 1.25;
// step n relativ zur Basis; Name → step
const TYPE_STEPS = [
  ['xs', -1],
  ['sm', 0],
  ['md', 1],
  ['lg', 2],
  ['xl', 3],
  ['2xl', 4],
  ['3xl', 5],
  ['4xl', 6],
];

// --- Space-Scale: Basis = Typo-Basis (16→18), Vielfache wie Utopia-Default ---
const SPACE_STEPS = [
  ['3xs', 0.25],
  ['2xs', 0.5],
  ['xs', 0.75],
  ['sm', 1],
  ['md', 1.5],
  ['lg', 2],
  ['xl', 3],
  ['2xl', 4],
  ['3xl', 6],
];

function typeRow([name, step]) {
  const minPx = TYPE_MIN_BASE * Math.pow(TYPE_MIN_RATIO, step);
  const maxPx = TYPE_MAX_BASE * Math.pow(TYPE_MAX_RATIO, step);
  return `  --t-${name}: ${fluid(minPx, maxPx)};`;
}
function spaceRow([name, mult]) {
  return `  --s-${name}: ${fluid(TYPE_MIN_BASE * mult, TYPE_MAX_BASE * mult)};`;
}

const out = `/* GENERIERT von scripts/gen-scales.mjs — NICHT von Hand editieren.
 * Fluide Utopia-Scales (${MIN_VW}px … ${MAX_VW}px). Einzige erlaubte clamp()/px-Quelle.
 * Token-Set ist geschlossen; neue Stufe nur per ADR (ADR-0007).
 */
:root {
  /* Fluide Typo-Scale (font-size) */
${TYPE_STEPS.map(typeRow).join('\n')}

  /* Fluide Space-Scale (gap, padding, margin) */
${SPACE_STEPS.map(spaceRow).join('\n')}
}
`;
process.stdout.write(out);
