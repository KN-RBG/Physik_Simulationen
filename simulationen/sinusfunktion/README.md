# Sinus- und Cosinusfunktionen – HTML-Version

Die Browser-Version folgt der Python-Version `downloads/python/sinus-geogebra/sinusfunktion.py` und benötigt kein GeoGebra.

## Funktionen

`f_sin(x) = a · sin(b(x−c)) + d` und `f_cos(x) = a · cos(b(x−c)) + d`.

Beide Kurven können mit eigenen Checkboxen ein- und ausgeblendet werden; als Startwert ist nur Sinus eingeschaltet.

Parameter und Regler, jeweils mit Schrittweite 0,1:

- a: −3 bis 3, Start 1; Betrag ist die Amplitude, negative Werte spiegeln an der Mittellinie.
- b: 0,1 bis 4, Start 1; Periodenlänge T = 2π/b.
- c: −6,3 bis 6,3, Start 0; positive Werte verschieben die Kurve nach rechts.
- d: −3 bis 3, Start 0; vertikale Verschiebung, Mittellinie y=d.

Ansicht x ∈ [−2π, 2π], y mindestens [−4,4], bei großem |a|+|d| automatisch erweitert. **Zurücksetzen** setzt Parameter und Kurvenauswahl zurück.

## Testfälle

- Standard: Sinus bei x=0 gleich 0; bei x=π/2 gleich 1.
- Nur Cosinus: bei x=0 gleich 1.
- Beide an: Phasenabstand π/2 bei a=b=1 und c=d=0.
- a=−2, d=1: Spiegelung; Wertebereich [−1,3].
- b=2: Periodenlänge π.
- c=π (auf 0,1-Schritte gerundet): Verschiebung nach rechts.
- Checkboxen unabhängig sowie Reset testen.

**Stand:** Implementiert und JavaScript-Syntax geprüft. Ein praktischer Browser-Test auf den gewünschten Schulgeräten steht noch aus.

Der Katalog enthält `html_url` und `qr_url` und keinen Webprojekt-Prototyp-Link mehr.
