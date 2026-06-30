# web/vendor — lokal vendored Runtime (committed)

LAN-only/offline: Preact + htm liegen als ESM **im Repo** (kein CDN zur Laufzeit). Aufgelöst via Import Map in [`../index.html`](../index.html). Siehe [ADR-0006](../../docs/adr/0006-js-schicht-preact-htm-light-dom.md) / [ADR-0008](../../docs/adr/0008-no-build-start-guardrails-ab-tag-1.md).

| Datei | Quelle (npm) | Version |
|---|---|---|
| `preact.module.js` | `preact/dist/preact.module.js` | 10.29.3 |
| `preact-hooks.module.js` | `preact/hooks/dist/hooks.module.js` | 10.29.3 |
| `htm.module.js` | `htm/dist/htm.module.js` | 3.1.1 |
| `htm-preact.module.js` | `htm/preact/index.module.js` | 3.1.1 |

## Re-vendor (nach `npm update`)
```sh
cp node_modules/preact/dist/preact.module.js      web/vendor/preact.module.js
cp node_modules/preact/hooks/dist/hooks.module.js web/vendor/preact-hooks.module.js
cp node_modules/htm/dist/htm.module.js            web/vendor/htm.module.js
cp node_modules/htm/preact/index.module.js        web/vendor/htm-preact.module.js
```

Diese Dateien sind Drittanbieter-Builds → **nicht** von stylelint/prettier geprüft (in den Ignore-Listen) und **nicht** editieren.
