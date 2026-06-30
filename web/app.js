// dash — App-Shell (Foundation-Skelett).
// Beweist: Preact + htm bootet im Light DOM, State/Hooks laufen, Primitive + Tokens
// komponieren. Echte Screens (Now Playing, Räume, Quellen, Szenen) folgen separat
// als Kompositionen aus Primitiven + Komponenten-Katalog (Verfassung §5).

import { render } from 'preact';
import { useEffect, useState } from 'preact/hooks';
import { html } from 'htm/preact';

const clock = () => new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });

/** Fragt das Backend-Health ab (Backend-Adapter, ADR-0002). Fehlt es, sauber degradieren. */
function useBackendHealth() {
  const [status, setStatus] = useState('lädt …');
  useEffect(() => {
    let alive = true;
    fetch('./api/health')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((d) => alive && setStatus(`verbunden · ${d.backend ?? 'backend'}`))
      .catch(() => alive && setStatus('Backend nicht erreichbar'));
    return () => {
      alive = false;
    };
  }, []);
  return status;
}

function AppShell() {
  const [now, setNow] = useState(clock());
  const health = useBackendHealth();
  useEffect(() => {
    const id = setInterval(() => setNow(clock()), 30000);
    return () => clearInterval(id);
  }, []);

  return html`
    <div class="cover">
      <header class="cluster cluster--between">
        <strong>dash</strong>
        <span>${now}</span>
      </header>

      <div class="cover__center center center--intrinsic stack">
        <p>Foundation läuft.</p>
        <small>${health}</small>
      </div>

      <footer class="cluster cluster--center">
        <small>Tokens · Primitive · Skin — bereit für Screens</small>
      </footer>
    </div>
  `;
}

render(html`<${AppShell} />`, document.getElementById('app'));
