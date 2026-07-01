# ADR-0009: Dynamische Werte über Inline-Custom-Properties (nicht Inline-Style-Deklarationen)

**Status:** Accepted · **Datum:** 2026-07-01

## Kontext
Manche Werte sind **Daten**, nicht Design (Lautstärke-Füllung 0–100%, später Fortschritt, Positionen). Sie müssen zur Laufzeit aus JS ins CSS. Die Verfassung verbietet Inline-Styles — aber irgendein Kanal für dynamische Daten ist nötig.

## Entscheidung
- **Erlaubt:** dynamische Daten als **Inline-Custom-Property** setzen, z. B. `style=${{ '--seg-fill': value + '%' }}`. Die Komponente-CSS konsumiert sie: `inline-size: var(--seg-fill, 0%)`. Der *Design*-Wert (Farbe, Maß, Rhythmus) bleibt im CSS/Token; inline reist nur die **Zahl/der Datenwert**.
- **Weiterhin verboten:** Inline-Style-**Deklarationen** mit Design-Werten (`style="color:…"`, `style="width:13px"`, `style="gap:…"`). Das ist Magic-Number/Skin am falschen Ort.

## Konsequenzen
- Data-driven UI (Meter, Fortschritt) ohne Bruch der Token-Disziplin.
- stylelint prüft CSS-Dateien; diese Grenze ist eine **Review-Regel** (JS wird nicht gelintet) → bewusst schmal halten: nur echte Laufzeit-Daten, nie ein getarnter Design-Wert.

## Alternativen
- **20 Segment-Divs per Klassen-Toggle** (kein Inline nötig): möglich, wirkt aber schmal „unruhig" (Visual-QA-Befund). Verworfen zugunsten ruhiger gefüllter Spur.
- **CSS-Klassen je 5%-Stufe** (`.v-0`…`.v-100`): 21 Klassen, starr, schlecht erweiterbar. Verworfen.
