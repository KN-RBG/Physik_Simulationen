# Federschwerependel – HTML-Version

Browserbasierte Portierung von `KN-RBG/Federschwerependel/federschwerependel_animation.py`.

## Physikalisches Modell

- `g = 9,81 m/s²`, `L₀ = 0,30 m`.
- `L_eq = L₀ + m*g/D`.
- `ω = √(D/m)`, `s = A*cos(φ)`, `L = L_eq - s`.
- **Positives s** bedeutet Masse **oberhalb** der Gleichgewichtslage.
- `F_G = m*g` zeigt nach unten; `F_F = D*(L-L₀)` zeigt nach oben; `F_res = F_G - F_F` (positiv nach unten).
- Idealisiertes, reibungsfreies Federpendel.

## Bedienelemente wie in Python

- Phase 0° bis 360°, 1°-Schritte; beim manuellen Verschieben automatische Pause.
- Amplitude 0,01–0,15 m in 0,005-m-Schritten (Startwert 0,08 m).
- Federhärte 8–25 N/m in 0,5-N/m-Schritten (Startwert 12 N/m).
- Masse 0,10–0,40 kg in 0,01-kg-Schritten (Startwert 0,25 kg).
- Einzelkräfte und resultierende Kraft separat ein-/ausblenden.
- Pause/Weiter ab der gewählten Phase.
- Im Browser läuft die physikalische Zeit mit `requestAnimationFrame`, unabhängig von der Bildwiederholrate; im Python-Original beträgt die numerische Zeitsteigerung 0,035 s je 35-ms-Animationsframe.

## Prüffälle

1. Grundeinstellung: `m=0,25 kg`, `D=12 N/m`, `A=0,08 m`, `φ=0°`. `L_eq = 0,504375 m`, `s = +0,08 m`, `F_G = 2,4525 N`, `F_F = 1,4925 N`, `F_res = +0,96 N` (nach unten).
2. Bei 90°: `s=0`, `L=L_eq`, `F_res=0`.
3. Bei 180°: `s=-0,08 m`, `F_res=-0,96 N` (nach oben).
4. Bei 270°: `s=0`, `F_res=0`.
5. Phase manuell bewegen: Animation hält an; Weiter führt ohne Positionssprung fort.
6. Einzelkraftdarstellung und resultierende Kraft getrennt ausblenden.
7. Parameteränderungen: Gleichgewichtslage, Frequenz und Kraftpfeile prüfen.

## Status

HTML-Version implementiert, aber noch **nicht vollständig visuell auf Desktop und Tablet getestet**. Die private Python-Entwicklungsversion bleibt unverändert. Öffentlicher Python-Download steht im Portal bereit.

## Ergänzung: Zeitdiagramm s(t), v(t), a(t)

Die Python- und Browser-Version zeigen **direkt unter der Federanimation** ein Zeitdiagramm über **zwei vollständige Perioden** (`0 ≤ t ≤ 2T`; `T = 2π√(m/D)`):

- `s(t) = A cos(ωt)` in **m** (violett).
- `v(t) = −Aω sin(ωt)` in **m/s** (blau).
- `a(t) = −Aω² cos(ωt)` in **m/s²** (orange).

Die Kurven liegen in einem gemeinsamen Diagramm, besitzen aber **getrennte, farbige y-Achsen mit realen Skalenwerten**, damit verschiedene physikalische Einheiten nicht auf einer einzigen Skala vermischt werden. Alle drei Verläufe lassen sich unabhängig per Checkbox ein- und ausblenden; eine vertikale gestrichelte Markierung zeigt den aktuellen Zeitpunkt.

Beim manuellen Verschieben des Phasenreglers wird der Zeitpunkt innerhalb der **ersten Periode** gewählt. Während der automatischen Animation läuft die Markierung über beide Perioden und kehrt danach zum Anfang zurück.

### Vergleichswerte für den Test (Grundeinstellung)

`A=0,08 m`, `D=12 N/m`, `m=0,25 kg`, `ω≈6,9282 rad/s`, `T≈0,9069 s`:

| Phase | s [m] | v [m/s] | a [m/s²] |
|---|---:|---:|---:|
| 0° | +0,080 | 0,000 | −3,840 |
| 90° | 0,000 | −0,554 | 0,000 |
| 180° | −0,080 | 0,000 | +3,840 |
| 270° | 0,000 | +0,554 | 0,000 |

Die Werte ergeben sich aus den analytischen Formeln; der visuelle Test auf den Zielgeräten steht noch aus.
