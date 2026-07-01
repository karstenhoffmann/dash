import { html } from 'htm/preact';
import { Icon } from '../lib/icons.js';

/** Kopfzeile: Titel (+ ▾-Umschalter, wenn mehrere Gruppen) links, Uhr rechts. */
export function AppBar({ title, clock, canSwitch = false, onSwitch }) {
  return html`<header class="appbar cluster cluster--between">
    <button
      class="appbar__title"
      onClick=${canSwitch ? onSwitch : undefined}
      disabled=${!canSwitch}
      aria-label="Gruppe wechseln"
    >
      <span class="appbar__name">${title}</span>
      ${canSwitch ? html`<${Icon} name="chevron-down" size="sm" />` : null}
    </button>
    <span class="appbar__clock">${clock}</span>
  </header>`;
}
