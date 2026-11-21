# Wellenüberlagerung – HTML-Version

Dies ist die browserbasierte Umsetzung der Python-Simulation [KN-RBG/Wellenueberlagerung](https://github.com/KN-RBG/Wellenueberlagerung/blob/main/Ueberlagerung_Wellen.py).

## Start

`index.html` direkt im Browser öffnen oder über das [Simulationsportal](https://kn-rbg.github.io/Physik_Simulationen/). Es werden keine externen JavaScript-Bibliotheken oder Netzwerkdienste benötigt.

## Funktionen

- Zwei Wellen mit unabhängigem Betrag der Amplitude, Wellenlänge und Frequenz.
- Ausbreitungsrichtung links/rechts, Startform `+sin` / `-sin`.
- Separate Sichtbarkeit der Einzelwellen und ihrer Überlagerung.
- Wellenfronten und physikalisch korrekte Aktivierung der erreichten Ortsbereiche.
- Zeitregler 0–200 %, Play/Pause und Zurück zum Start.
- Deutschsprachige Beschriftungen; Dezimalkomma wird akzeptiert.

## Modell und Übereinstimmung mit Python

Für eine Welle mit Ausbreitungsweg `s=x` (Richtung nach rechts) beziehungsweise `s=L-x` (Richtung nach links):

```
v = f * lambda
y(s,t) = vorzeichen * A * sin(2*pi*s/lambda - 2*pi*f*t)  für 0 <= s <= v*t und t>0
```

Außerhalb des erreichten Raumbereichs ist die physikalische Auslenkung 0, im Einzelwellen-Diagramm wird keine Linie gezeichnet.

Die Überlagerung wird **nur** dort gezeichnet, wo beide Wellen bereits angekommen sind.

`t_basis = L / min(v1,v2)`: 100 % entspricht dem Erreichen des gegenüberliegenden Endes durch die langsamere Welle; 200 % entspricht der doppelten Zeit. Die automatische Wiedergabe läuft mit einer Modellsekunde pro Echtzeitsekunde bis 200 % und endet dort.

## Prüffälle (noch durch praktischen Browservergleich zu bestätigen)

1. Grundeinstellung: L=16 m, A1=A2=1 m, λ1=λ2=4 m, f1=f2=0,32 Hz. Beide Wellenfronten treffen sich bei x=8 m, sobald 50 % erreicht sind.
2. Bei 0 % werden keine Wellen gezeichnet.
3. Bei 25 % und Grundeinstellungen sind die aktiven Bereiche voneinander getrennt und es erscheint keine resultierende Welle.
4. Bei 50 % berühren sich die Wellenfronten im Zentrum; bei 100 % sind beide über die ganze Strecke angekommen.
5. Mit +sin / −sin, gleicher Ausbreitungsrichtung und gleichen Parametern muss im gemeinsamen Bereich destruktive Überlagerung sichtbar sein.
6. Die manuelle Bewegung des Zeitreglers pausiert Play; bei 200 % endet Play automatisch.
7. Änderungen an Richtung oder der Schaltfläche „Werte übernehmen“ starten bei 0 % neu.

**Status:** Erste browserbasierte Fassung; ein grafischer und didaktischer Test auf Tablet/Schulgeräten steht noch aus.
