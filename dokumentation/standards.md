# Standards für KN-RBG Physik-Simulationen

## Grundprinzip
Jede Simulation erhält **zwei Versionen**: Python (lokal) und HTML/CSS/JavaScript (direkt im Browser). Beide verwenden dieselben physikalischen Gleichungen, Anfangsbedingungen, Parameter, Einheiten und Vorzeichenkonventionen.

## Themenbereiche
1. Elektrische und magnetische Felder
2. Induktion
3. Mechanische Schwingungen und Wellen
4. Elektromagnetische Schwingungen und Wellen
5. Atom- und Quantenphysik

## Benutzeroberfläche
- Einfache, konsistente Beschriftungen auf Deutsch.
- Je nach Simulation: Start/Pause, Reset, veränderbare Parameter und Einblendung von Diagrammen.
- Bedienbarkeit mit Tastatur, Maus und Touchscreen.
- Mobilfreundliche HTML-Oberflächen.
- Keine externe Anmeldung für Schüler.
- Keine personenbezogenen Daten erheben.

## Qualität und Freigabe
- Python- und HTML-Ergebnisse anhand identischer Testwerte vergleichen.
- Grenzfälle, Einheiten, Anfangsbedingungen und Vorzeichen prüfen.
- Browsertests auf Desktop und Tablet durchführen.
- Erst danach eine Simulation als unterrichtstauglich kennzeichnen.

## Veröffentlichungsprinzip
Das zentrale Portal enthält die Browser-Versionen bzw. Links zu ihnen und verweist auf die jeweiligen Python-Repositories. Bestehende Repositories bleiben bestehen. Neue HTML-Implementierungen können hier im Ordner `simulationen/` gepflegt werden.

## Stand
Die Portalseite ist ein Grundgerüst, kein Nachweis abgeschlossener Tests.

## Zuordnung und Katalog (ab November 2026)
Die Datei `daten/simulationen.json` verwaltet jede Simulation einmalig. `thema` ist der fachliche Themenbereich; `klassenstufen` ist eine Liste aus 7, 8, 9, 10, JG1, JG2; `bildungsgaenge` eine unabhängige Liste aus G8 und G9. Solange die didaktische Zuordnung nicht geprüft wurde, bleiben die Listen leer und werden **nicht** automatisch erschlossen. `python_url` und `html_url` sind voneinander unabhängige Felder. Für bestehende GeoGebra-Prototypen dient `webprojekt_url` als Verweis, ohne eine geprüfte HTML-Version zu suggerieren.

Neue Themen für die unteren Klassen können später ergänzt werden; die fünf beschlossenen Kursstufen-Themen bleiben bestehen.
