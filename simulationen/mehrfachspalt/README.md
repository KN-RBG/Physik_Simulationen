# Interferenz am Mehrfachspalt – HTML-Version

Browser-Portierung von `KN-RBG/Interferenz-am-Mehrfachspalt/Mehrfachspalt_GUI.py`. Die Python-Quelle und der bisherige öffentliche Python-Download bleiben unverändert.

## Bedienung und Standardwerte

- Anzahl der Spalte: **2**
- Spaltbreite b: **0,05 mm**
- Spaltabstand g: **0,20 mm**
- Schirmabstand a: **2,0 m**
- Wellenlänge λ: **650 nm**
- Schirmbereich: **−60 mm bis +60 mm**
- Checkbox **Einzelspalt berücksichtigen**: zunächst aus
- Checkbox **Einzelspalt-Hüllkurve anzeigen**: zunächst aus

Eingaben akzeptieren Komma oder Punkt. Wie in Python wird das Diagramm mit dem Button **Interferenzbild zeichnen** oder durch Umschalten der Checkboxen aktualisiert. **Standardwerte** setzt die Eingaben zurück. Für die Kurven werden jeweils 5000 Punkte berechnet.

## Unverändert übernommenes physikalisches Modell

Für jeden Schirmpunkt x (in m):

- `θ = atan(x/a)`
- `α = π g sin(θ) / λ`
- `I_N = (sin(N α)/sin α)² / N²`, im Grenzfall `sin α ≈ 0` wird der Grenzwert gesetzt
- `β = π b sin(θ) / λ`
- `I_1 = (sin β/β)²` mit Grenzwert 1 bei β = 0.
- Mit Einzelspalt-Beugung: `I = I_N · I_1`; andernfalls `I = I_N`.
- Abschließend Maximumsnormierung der im gewählten Schirmbereich berechneten Gesamtintensität auf 1, sofern es positiv ist.
- Die separat anzeigbare Einzelspalt-Hüllkurve entspricht `I_1` (wird nicht zusätzlich maximumsnormiert).

Anzahl der Spalte mindestens 1; b, g, a, λ positiv, b ≤ g und Bereich von < bis. Zusätzlich begrenzt die Browser-Version die Spaltzahl zur Laufzeitstabilität auf 2000.

## Prüffälle

1. In der Mitte (`x=0`) ergibt sich unabhängig von der Spaltzahl `I_N=1` und `I_1=1`.
2. N=1: `I_N=1` für alle Positionen (ohne Einzelspalt-Beugung konstante Intensität).
3. Hüllkurve aktivieren: zweite rote Kurve ergänzen; deren Checkbox soll die Hauptkurve nicht verändern.
4. Einzelspalt berücksichtigen: Intensitätskurve wird mit der Hüllkurve multipliziert.
5. Parameter verändern: Das Diagramm wird auf Klick oder Enter neu berechnet; Fehler beim ungültigen Parameter werden angezeigt.
6. Standardwerte setzen alle Eingaben und Checkboxen zurück.

**Status:** HTML-Simulation implementiert und JavaScript-Syntax geprüft; visueller Funktionstest im Zielbrowser sowie direkter Vergleich mit der Python-Anwendung stehen noch aus.
