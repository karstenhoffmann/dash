// Button + IconButton — komponieren Icon + .btn-Klassen (Light DOM, nur Tokens im CSS).
import { html } from 'htm/preact';
import { Icon } from '../lib/icons.js';

const SIZE_CLASS = { md: '', lg: 'iconbtn--lg', xl: 'iconbtn--xl' };

/** Icon-Button. size ∈ md|lg|xl · variant z. B. 'btn--primary' | 'iconbtn--plain'. */
export function IconButton({ icon, size = 'md', variant = '', label, onClick, disabled }) {
  const cls = ['btn', 'iconbtn', SIZE_CLASS[size] || '', variant].filter(Boolean).join(' ');
  return html`<button class=${cls} aria-label=${label} onClick=${onClick} disabled=${disabled}>
    <${Icon} name=${icon} size=${size === 'md' ? 'md' : 'lg'} />
  </button>`;
}
