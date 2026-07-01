// dash — App-Shell: State + Poll + Hub-and-Spoke-Router. Screens sind reine
// Kompositionen (Verfassung §5); die App hält Zustand und reicht Aktionen durch.
import { render } from 'preact';
import { useEffect, useState } from 'preact/hooks';
import { html } from 'htm/preact';

import { api } from './lib/api.js';
import { AppBar } from './components/appbar.js';
import { TabBar, TABS } from './components/tabbar.js';
import { NowPlaying } from './screens/now-playing.js';

const POLL_MS = 5000;
const clock = () => new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
const labelFor = (view) => TABS.find((t) => t.id === view)?.label ?? '';

function App() {
  const [snap, setSnap] = useState(null);
  const [err, setErr] = useState(false);
  const [view, setView] = useState('now');
  const [activeId, setActiveId] = useState(null);
  const [now, setNow] = useState(clock());

  const refresh = async () => {
    try {
      setSnap(await api.getState());
      setErr(false);
    } catch {
      setErr(true);
    }
  };

  // Poll (kein Push im MVP; e-ink-Endausbau später ohne Auto-Poll, ADR-0005).
  useEffect(() => {
    refresh();
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, []);
  useEffect(() => {
    const id = setInterval(() => setNow(clock()), 30000);
    return () => clearInterval(id);
  }, []);

  const groups = snap?.groups ?? [];
  const active = groups.find((g) => g.id === activeId) ?? groups[0] ?? null;
  const room = active?.coordinator;

  // Aktion ausführen → danach sofort neu laden (Reconcile mit echtem Speaker-Zustand).
  const run =
    (fn) =>
    async (...a) => {
      try {
        await fn(...a);
      } catch {
        /* Fehler → nächster Poll korrigiert den Zustand */
      }
      refresh();
    };
  const actions = active
    ? {
        play: run(() => api.play(room)),
        pause: run(() => api.pause(room)),
        next: run(() => api.next(room)),
        previous: run(() => api.previous(room)),
        setVolume: run((v) => api.groupVolume(room, v)),
        volumeRel: run((d) => api.groupVolumeRel(room, d)),
        toggleMute: run(() => api.groupMute(room, !active.mute)),
      }
    : null;

  const title = active ? active.name : err ? 'Nicht erreichbar' : 'dash';

  return html`<div class="cover">
    <${AppBar}
      title=${title}
      clock=${now}
      canSwitch=${groups.length > 1}
      onSwitch=${() => setActiveId(nextGroupId(groups, active))}
    />
    ${
      view === 'now'
        ? html`<${NowPlaying} group=${active} actions=${actions} />`
        : html`<div class="cover__center np stack">
            <p>${labelFor(view)}</p>
            <small>kommt als Nächstes</small>
          </div>`
    }
    <${TabBar} view=${view} onNav=${setView} />
  </div>`;
}

/** Provisorischer Umschalter: nächste Gruppe (echter ▾-Popover folgt mit dem Räume-Screen). */
function nextGroupId(groups, active) {
  if (groups.length < 2) return active?.id ?? null;
  const i = groups.findIndex((g) => g.id === active?.id);
  return groups[(i + 1) % groups.length].id;
}

render(html`<${App} />`, document.getElementById('app'));
