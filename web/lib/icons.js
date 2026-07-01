// Lucide-SVG-Icons (Verfassung §7: nur Lucide, nie Emoji). Größe via CSS-Token
// (.icon--sm/-md/-lg), nicht per Pixel — damit Icon-Maße auch Tokens folgen.
import { html } from 'htm/preact';

const PATHS = {
  'skip-back': '<polygon points="19 20 9 12 19 4"/><line x1="5" x2="5" y1="19" y2="5"/>',
  play: '<polygon points="6 3 20 12 6 21"/>',
  pause:
    '<rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/>',
  'skip-forward': '<polygon points="5 4 15 12 5 20"/><line x1="19" x2="19" y1="5" y2="19"/>',
  minus: '<line x1="5" x2="19" y1="12" y2="12"/>',
  plus: '<line x1="5" x2="19" y1="12" y2="12"/><line x1="12" x2="12" y1="5" y2="19"/>',
  'volume-2':
    '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>',
  'volume-x':
    '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19"/><line x1="22" x2="16" y1="9" y2="15"/><line x1="16" x2="22" y1="9" y2="15"/>',
  music: '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
  'chevron-down': '<polyline points="6 9 12 15 18 9"/>',
  home: '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
  'layout-grid':
    '<rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/>',
  radio:
    '<path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9"/><path d="M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5"/><circle cx="12" cy="12" r="2"/><path d="M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5"/><path d="M19.1 4.9C23 8.8 23 15.1 19.1 19"/>',
  star: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
};

/** <${Icon} name="play" size="lg" />. size ∈ sm|md|lg (CSS-Token). */
export function Icon({ name, size = 'md' }) {
  return html`<svg
    class="icon icon--${size}"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    dangerouslySetInnerHTML=${{ __html: PATHS[name] || '' }}
  ></svg>`;
}
