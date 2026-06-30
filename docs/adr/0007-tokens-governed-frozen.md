# ADR-0007: Tokens sind geschlossen, eingefroren und ADR-gated

**Status:** Accepted · **Datum:** 2026-07-01

## Kontext
Drift-Sorge: neue Werte schleichen sich „mal eben" rein und unterwandern das System. Wichtige Einsicht: **Was Drift verhindert, ist nicht die Token-Quelle, sondern die Governance.** Ob Open Props oder selbst geschrieben — beides driftet, wenn jemand einen Wert außerhalb des Systems einführt.

## Entscheidung
1. **Geschlossenes, kleines, eingefrorenes Token-Set** als CSS Custom Properties (`web/tokens/`), aus dem Utopia/cu.css-Anker abgeleitet.
2. **Tokens sind leicht zu *lesen*, bewusst schwer zu *erweitern*.** Ein neuer Token (oder eine neue Skala-Stufe) entsteht **nur per ADR** — nie als Einzelfall.
3. **Mechanischer Anker = stylelint** (siehe ADR-0008): `declaration-strict-value` erzwingt `var(--token)` statt roher Werte; `declaration-property-value-disallowed-list` / `-unit-disallowed-list` verbieten rohe `px`/`clamp()` in Komponenten. CI rot bei Verstoß.
4. **Open Props: nein.** Nicht nötig, überlappt mit Utopia, größere Palette = größere Drift-Fläche.

## Konsequenzen
- Ein kleines geschlossenes Set ist der stärkere Anti-Drift-Anker als eine große Lib.
- „Brauche neuen Wert" wird zur bewussten, dokumentierten Entscheidung (ADR), nicht zum Reflex.
- Token-Datei bleibt überschaubar und für Claude trivial zu **lesen** (aber nicht beliebig zu erweitern).

## Alternativen
- **Selbst geschrieben + frei erweiterbar:** verworfen — „trivial erweiterbar" ist genau der Drift-Vektor.
- **Open Props als Token-Quelle:** verworfen (s.o.). Bleibt technisch sicher (klein, niedriger Lock-in), aber nicht gewählt.
