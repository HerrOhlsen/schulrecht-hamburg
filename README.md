# Schulrecht Hamburg: Lerntrainer zum Hamburgischen Schulgesetz

**Live:** https://herrohlsen.github.io/schulrecht-hamburg/

Ein Lern- und Hörangebot zum Hamburgischen Schulgesetz (HmbSG) für Lehrkräfte im Vorbereitungsdienst in Hamburg, gedacht als Vorbereitung auf den schul- und dienstrechtlichen Abschnitt der mündlichen Prüfung (Zweite Staatsprüfung). Läuft im Browser, lässt sich auf dem Handy zum Home-Bildschirm hinzufügen und funktioniert danach auch offline.

## Was drin ist

- **Hörbuch** (gut 4 Stunden, 9 Teile): der Gesetzestext im Wortlaut, nach jedem Paragrafen eine Kurzfassung in Alltagssprache und bei den praxisrelevanten Paragrafen ein Beispielfall. Synthetische Stimmen, Kapitelmarken pro Paragraf, mitlaufender Text, offline speicherbar.
- **Erklärvideos:** „Das Gesetz als Schulhaus“ (Aufbau der neun Teile) und „§ 49: Die Treppe der Maßnahmen“.
- **Übungsmodi:** Lesen, Paragraf-Recall, „Wer entscheidet?“ (62 Zuständigkeitsfragen), „E oder O?“ (Erziehungs- oder Ordnungsmaßnahme), Praxisfälle mit 5-Minuten-Timer, Struktur mit Fortschrittsanzeige.

## Entstehung

Den Anstoß gab ein Lehrer aus Niedersachsen, der mit dem Hamburger Schulrecht beruflich nichts zu tun hat. Er hat das Projekt für eine Freundin angeregt, die in Hamburg im Referendariat ist und für die mündliche Prüfung lernt. Idee, Auswahl und Rückmeldungen kamen von den beiden. Recherche, Kurzfassungen, Fälle, Sprachaufnahmen, Videos und Programmierung hat Claude (ein KI-Modell von Anthropic) übernommen.

## Weiterentwicklung: feel free

An dem Projekt wird nicht aktiv weitergearbeitet, und Issues werden voraussichtlich nicht beantwortet. Wer Lust hat, kann das Repository gern forken und selbst weiterbauen: Fehler korrigieren, Fälle ergänzen, eine neue Gesetzesfassung einpflegen oder das Ganze auf ein anderes Bundesland übertragen.

Für den Einstieg:

- `index.html` ist die komplette App (eine Datei, Daten eingebettet), `sw.js` der Service Worker für den Offline-Betrieb, `info.html` die Anleitung.
- `audio/` enthält die Hörbuch-MP3s, Sprechskripte (`.txt`) und Kapitelmarken (`.chapters.json`), `video/` die Erklärvideos mit Untertiteln (`.vtt`).
- `quelltexte/` enthält die bearbeitbaren Daten und Skripte:
  - `hmbsg.json`: Gesetzestext nach Teilen, Abschnitten, Paragrafen und Absätzen
  - `erklaerungen.json`: Kurzfassung (`alltag`) und Beispielfall (`fall`) je Paragraf
  - `zustaendigkeit.json` und `massnahmen.json`: die Aufgaben für „Wer entscheidet?“ und „E oder O?“
  - `tools/parse_hmbsg.py` (PDF-Text zu JSON), `tools/render_hoerbuch.py` (Hörbuch über Gemini-TTS, braucht `GEMINI_API_KEY`), `tools/build_lerntrainer.py` (baut `index.html`)

## Quellen und Hinweise

- Gesetzestext: Hamburgisches Schulgesetz in der Ausgabe der Behörde für Schule und Berufsbildung, Stand der letzten Änderung 3. Mai 2023. Spätere Änderungen sind nicht eingearbeitet; maßgeblich ist die aktuelle Fassung auf [landesrecht-hamburg.de](https://www.landesrecht-hamburg.de/bsha/document/jlr-SchulGHArahmen).
- Prüfungsformat: Verwaltungsvorschrift zur VVZS vom 6. Juni 2025 (Landesinstitut Hamburg), Kapitel C.
- Kurzfassungen und Fälle sind Lernhilfen, keine Rechtsberatung und kein Angebot der Behörde oder des Landesinstituts. Das Dienstrecht ist nicht enthalten.

## Lizenz

- **Code** (App, Service Worker, Skripte): MIT, siehe [`LICENSE`](LICENSE).
- **Inhalte** (Kurzfassungen, Fälle, Übungsaufgaben, Hörbuch, Videos): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de), siehe [`LICENSE-INHALTE.md`](LICENSE-INHALTE.md).
- **Gesetzestext:** als amtliches Werk gemeinfrei (§ 5 UrhG).
