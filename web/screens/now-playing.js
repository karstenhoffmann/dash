// Now Playing (Hub) — Komposition aus Primitiven (Cover/Center/Stack/Cluster/Frame)
// + Komponenten (IconButton/SegBar). Führt KEIN eigenes Skin/CSS ein (DESIGN §4/§6).
import { html } from 'htm/preact';
import { Icon } from '../lib/icons.js';
import { IconButton } from '../components/button.js';
import { SegBar } from '../components/segbar.js';

const VOL_STEP = 5;

function Cover({ artUrl }) {
  return html`<div class="np__cover frame">
    ${artUrl ? html`<img src=${artUrl} alt="" />` : html`<${Icon} name="music" size="lg" />`}
  </div>`;
}

export function NowPlaying({ group, actions }) {
  if (!group) {
    return html`<div class="cover__center np stack">
      <p>Nichts läuft.</p>
      <small>Wähle eine Quelle oder Szene.</small>
    </div>`;
  }

  const now = group.now || {};
  const playing = group.state === 'playing';

  return html`<div class="cover__center np stack">
    <${Cover} artUrl=${now.art_url} />

    <div class="stack np__text">
      <div class="np__title">${now.title || 'Nichts läuft'}</div>
      <div class="np__artist">${now.artist || now.source || ''}</div>
    </div>

    <div class="cluster cluster--center np__transport">
      <${IconButton} icon="skip-back" size="lg" label="Zurück" onClick=${actions.previous} />
      <${IconButton}
        icon=${playing ? 'pause' : 'play'}
        size="xl"
        variant="btn--primary"
        label=${playing ? 'Pause' : 'Abspielen'}
        onClick=${playing ? actions.pause : actions.play}
      />
      <${IconButton} icon="skip-forward" size="lg" label="Weiter" onClick=${actions.next} />
    </div>

    <div class="stack np__volume">
      <div class="np__vol-row">
        <${IconButton} icon="minus" label="Leiser" onClick=${() => actions.volumeRel(-VOL_STEP)} />
        <${SegBar} value=${group.volume} onSet=${actions.setVolume} />
        <${IconButton} icon="plus" label="Lauter" onClick=${() => actions.volumeRel(VOL_STEP)} />
        <${IconButton}
          icon=${group.mute ? 'volume-x' : 'volume-2'}
          variant="iconbtn--plain"
          label=${group.mute ? 'Ton an' : 'Stumm'}
          onClick=${actions.toggleMute}
        />
      </div>
    </div>
  </div>`;
}
