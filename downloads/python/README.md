# Öffentliche Python-Versionen

Hier liegen **separate Kopien** der Python-Programme für den Unterricht. Die ursprünglichen Entwicklungs-Repositories bleiben in ihrer bisherigen Sichtbarkeit und werden **nicht** automatisch öffentlich.

Die Dateien sind auf offensichtliche Zugangsdaten und externe Projektdatei-Abhängigkeiten gesichtet worden. **Ein vollständiger grafischer Funktionstest auf Schulgeräten steht aus.** Diese Kopien sind eigenständig: Änderungen an den privaten Originalen werden nicht automatisch übernommen.

## Herunterladen und starten

1. Python 3 auf dem Rechner installieren.
2. Die gewünschte `.py`-Datei über das Physik-Simulationsportal herunterladen.
3. Ein Terminal in dem Download-Ordner öffnen.
4. Die passenden Pakete installieren, z. B. `python -m pip install numpy matplotlib`.
5. Das Programm mit `python dateiname.py` starten.

Unter Windows kann anstelle von `python` der Python-Starter `py` verwendet werden. Für die GUI-Versionen muss Python mit Tkinter installiert sein; unter Windows ist das normalerweise der Fall.

## Dateien und Bibliotheken

| Programm | Datei | Zusätzliche Pakete |
| --- | --- | --- |
| Gegenläufige Wellen | `wellenueberlagerung/Ueberlagerung_Wellen.py` | numpy, matplotlib |
| Zeigerdiagramm | `zeigerdiagramm/zeigerdiagramm.py` | numpy, matplotlib |
| Elektrische Feldlinien | `elektrische-feldlinien/elektrische_feldlinien.py` | numpy, matplotlib |
| Gleichlaufende Wellen | `gleichlaufende-wellen/gleichlaufende_wellen.py` | numpy, matplotlib; sounddevice für optionale Tonwiedergabe |
| Interferenz am Mehrfachspalt | `mehrfachspalt/Mehrfachspalt_GUI.py` | numpy, matplotlib |
| Federschwerependel | `federschwerependel/federschwerependel_animation.py` | numpy, matplotlib |
| LC-Schwingkreis und Federpendel | `schwingkreis-vergleich/schwingkreis_vergleich.py` | numpy, matplotlib |
| Fourier 1D | `fourier/Fourier_1D_GUI.py` | numpy, matplotlib |
| Fourier Demo | `fourier/Fourier_Demo_GUI.py` | numpy, matplotlib |
| Motorkennlinie | `motorkennlinie/Kennlinie_Schieberegler.py` | numpy, matplotlib |

Für das **Sternbilder-/LED-Modell** wird zunächst noch kein öffentlicher Python-Download angeboten, da es zusätzliche Pakete, Datenabfragen und Ausgabedateien benötigt. Das prüfen wir gesondert.

## Veröffentlichungsprozess

1. Im privaten Entwicklungsprojekt Änderungen fertigstellen.
2. Code auf Zugangsdaten, lokale Pfade und Abhängigkeiten prüfen.
3. Lokal ausführen und Funktionen testen.
4. Freigegebene Fassung hierher kopieren.
5. Portal-Metadaten sowie gegebenenfalls erforderliche Hilfsdateien aktualisieren.

Diese öffentlichen Dateien sind keine automatische Spiegelung der privaten Repositories.
