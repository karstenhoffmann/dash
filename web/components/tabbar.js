import { html } from 'htm/preact';
import { Icon } from '../lib/icons.js';

export const TABS = [
  { id: 'now', icon: 'home', label: 'Start' },
  { id: 'raeume', icon: 'layout-grid', label: 'Räume' },
  { id: 'quellen', icon: 'radio', label: 'Quellen' },
  { id: 'szenen', icon: 'star', label: 'Szenen' },
];

/** Untere Navigation zwischen den Screens (Hub-and-Spoke, DESIGN §4). */
export function TabBar({ view, onNav }) {
  return html`<footer class="tabbar cluster">
    ${TABS.map(
      (t) =>
        html`<button class="tab ${view === t.id ? 'is-active' : ''}" onClick=${() => onNav(t.id)}>
          <${Icon} name=${t.icon} />
          <span>${t.label}</span>
        </button>`
    )}
  </footer>`;
}
