# Zeigerdiagramm und Sinuskurve – HTML-Version

Browserbasierte Umsetzung des Python-Programms [KN-RBG/Zeigerdiagramm](https://github.com/KN-RBG/Zeigerdiagramm).

## Bedienung

- Schieberegler: Winkel `α` von 0° bis 720°, Schrittweite 1°.
- **Start / Stopp**: Zeiger und Sinuskurve laufen synchron. Automatische Animation in 2°-Schritten alle 25 ms, nach 720° beginnt die Animation erneut bei 0° (wie in Python).
- **Zurück**: Animation stoppen und auf 0° zurücksetzen.
- Darstellung des rotierenden roten Zeigers auf dem Einheitskreis, der Projektion auf die Zeitachse und der bisher entstandenen blauen Sinuskurve.
- Anzeige von `α` in Grad sowie als Vielfaches von `2π`.
- Zwei Skalen unter dem Sinusdiagramm: Bogenmaß und Gradmaß.

## Physikalisches Modell

```text
alpha_rad = alpha_deg * pi / 180
x = cos(alpha_rad)
y = sin(alpha_rad)
Sinuskurve: y(beta) = sin(beta), 0 <= beta <= alpha_rad
```

Das Zeigerdiagramm zeigt die Projektion des Kreisbewegungsradius auf die vertikale Achse. Für die Ausbreitung gibt es keine zusätzlichen physikalischen Parameter.

## Vergleich mit Python: Prüfpunkte

| Winkel | x = cos α | y = sin α | Skala in rad |
| --- | ---: | ---: | --- |
| 0° | 1 | 0 | 0 |
| 90° | 0 | 1 | π/2 |
| 180° | −1 | 0 | π |
| 270° | 0 | −1 | 3π/2 |
| 360° | 1 | 0 | 2π |
| 720° | 1 | 0 | 4π |

Zusätzliche Prüfpunkte:
- Der blaue Graph reicht nur bis zum eingestellten Winkel.
- Schieberegler und rote Markierung am Kurvenende bleiben synchron.
- Nach Stopp bleibt die aktuelle Stellung erhalten.
- Nach 720° folgt während Play erneut 0°.
- Zurück setzt auf 0° und beendet die Animation.
- Mit Maus und Touch auf verschiedenen Bildschirmgrößen testen.

## Status

Erste HTML-Version implementiert und Quellcode auf GitHub gespeichert. **Noch kein vollständiger visueller Browser-Test auf Schulgeräten erfolgt.** Die Python-Version wurde nicht verändert.
