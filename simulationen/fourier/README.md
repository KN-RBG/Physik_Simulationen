# Fourier-Transformation: zwei Browser-Demos

Beide HTML-Versionen sind unabhängig von Python/GeoGebra direkt im Browser ausführbar und erreichen ihre Startseite über `index.html`.

## 1. Eindimensionale Fourier-Demo (`index.html`)

Die Vorlage ist `KN-RBG/Fourier_Transformation/Fourier_1D_GUI.py`.

- Signale: **Sinus, Rechteck, Dreieck, Sägezahn**
- 1600 äquidistante Abtastpunkte im Intervall `0 ≤ x < 2π`
- Bis zu 50 nach Betrag ihrer diskreten Fourier-Koeffizienten sortierte harmonische Komponenten (ohne Gleichanteil)
- Unabhängige Checkboxen: Originalsignal, Fourier-Summe, einzelne Komponenten (max. 12)
- Filter: Alle, Tiefpass und Hochpass, Grenzfrequenz 1–50
- Diagramme: Signal mit Fourier-Näherung, Frequenzspektrum, Komponenten und Summe
- Anzeige: Anzahl tatsächlich aktiver Frequenzanteile und RMS-Abweichung
- Der Gleichanteil bleibt analog zur Python-Implementierung erhalten.
- Die dynamische Auswahl nutzt den gesamten **einseitigen DFT-Satz** und wählt daraus die stärksten nichtkonstanten harmonischen Anteile; danach greift der Frequenzfilter.
- Bei Rechtecksignalen kann das Gibbs-Phänomen sichtbar werden.

## 2. Fourier-Epizykel und Wortkonturen (`epizykel.html`)

Die Vorlage ist `KN-RBG/Fourier_Transformation/Fourier_Demo_GUI.py`.

- Wort-Eingabe, Neu berechnen, Start/Stopp, Zurücksetzen
- 1–250 Fourier-Komponenten, Anfangswert 25
- Optionale Epizykel (max. 40 Kreise), optionale Zielkontur
- Drei Diagramme: rekonstruierte Kontur, Frequenzspektrum, x(t)/y(t)
- 2200 konturabgetastete Punkte, komplexe Fourier-Transformation (Bluestein-FFT)
- Auswahl der stärksten Fourier-Koeffizienten, inklusive positiver und negativer Frequenzen
- Relativer RMS-Fehler bezogen auf die größte Ausdehnung der Wortkontur

**Unterschied zur Python-Version:** Die Python-GUI erstellt Konturen aus Vektor-Schriftpfaden (`matplotlib.textpath.TextPath`), die Browserfassung extrahiert die Schriftumrisse aus einem lokal gezeichneten Canvas. Deshalb können einzelne Konturen und die daraus berechneten Koeffizienten leicht voneinander abweichen. Beide nutzen dieselbe Fourier-Zerlegung und Epizykel-Mathematik.

## QR-Code und Links

Der öffentliche Katalog verlinkt auf `simulationen/fourier/index.html`; von dort führt die Navigation zur Wortkontur-Demo. Der gespeicherte QR-Code `assets/qr/fourier.svg` verweist auf dieselbe Startseite.

Beide Python-Programme sind als öffentliche Downloads vorhanden:
- `downloads/python/fourier/Fourier_1D_GUI.py`
- `downloads/python/fourier/Fourier_Demo_GUI.py`

## Funktionstests

1. **1D Sinus, k=1, Filter Alle:** Die Fourier-Summe sollte praktisch deckungsgleich mit dem Ausgangssignal sein; RMS nahe null.
2. **1D Rechteck:** Mit steigender Komponentenanzahl muss sich die Näherung verbessern; nahe der Sprungstellen wird das Gibbs-Phänomen erkennbar.
3. **1D Filter:** Tiefpass lässt nur Frequenzen bis zur Grenzfrequenz zu, Hochpass ab dieser Grenze; Anzahl aktiver Komponenten und RMS ändern sich.
4. **1D Anzeige:** Originalsignal, Summe und Einzelkomponenten unabhängig ein-/ausblenden.
5. **Epizykel:** Das Wort „Physik“ sollte eine erkennbare Kontur liefern; bei steigender Anzahl an Komponenten verbessert sich die Rekonstruktion im Allgemeinen.
6. **Epizykel Animation:** Der Endpunkt der rotierenden Vektoren folgt dem gezeichneten Kurvenpunkt; x(t)/y(t) zeigen denselben Zeitpunkt.
7. **Epizykel Eingaben:** Leerstring meldet einen Fehler, Start/Stopp und Reset funktionieren.

**Status:** Dateien implementiert und JavaScript-Syntax überprüft. Der mathematische Bluestein-Algorithmus wurde mit analytischen komplexen Testschwingungen bis 2200 Punkte geprüft; die sichtbare Darstellung und der Vergleich auf realen Zielgeräten stehen noch aus.
