"""Interaktive Sinus- und Cosinusfunktionen ohne GeoGebra.

f_sin(x) = a * sin(b * (x-c)) + d
f_cos(x) = a * cos(b * (x-c)) + d

Installation: pip install numpy matplotlib
Start: python sinusfunktion.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons

DEFAULTS = {"a": 1.0, "b": 1.0, "c": 0.0, "d": 0.0}
X = np.linspace(-2 * np.pi, 2 * np.pi, 1600)

fig, ax = plt.subplots(figsize=(13.2, 8.4))
fig.canvas.manager.set_window_title("Sinus- und Cosinusfunktionen")
fig.subplots_adjust(left=0.075, right=0.77, top=0.88, bottom=0.39)

ax.set_title("Sinus- und Cosinusfunktionen interaktiv", fontsize=15)
ax.set_xlabel("x")
ax.set_ylabel("f(x)")
ax.set_xlim(-2 * np.pi, 2 * np.pi)
ax.set_ylim(-4, 4)
ax.set_xticks(np.pi * np.arange(-2, 2.01, 0.5))
ax.set_xticklabels([
    r"$-2\pi$", r"$-\frac{3\pi}{2}$", r"$-\pi$",
    r"$-\frac{\pi}{2}$", "$0$", r"$\frac{\pi}{2}$",
    r"$\pi$", r"$\frac{3\pi}{2}$", r"$2\pi$"
])
ax.grid(True, alpha=0.25)
ax.axhline(0, color="#475569", linewidth=1, alpha=0.6)
ax.axvline(0, color="#475569", linewidth=1, alpha=0.6)

line_sin, = ax.plot(X, np.sin(X), color="#235ab4", linewidth=2.7,
                    label="Sinus")
line_cos, = ax.plot(X, np.cos(X), color="#c26c20", linewidth=2.7,
                    label="Cosinus", visible=False)

fig.text(0.075, 0.950,
         r"$f_{\mathrm{sin}}(x)=a\sin(b(x-c))+d$"
         r"     $f_{\mathrm{cos}}(x)=a\cos(b(x-c))+d$",
         fontsize=14)

# Both curves can be enabled individually or at the same time.
fig.text(0.79, 0.875, "Kurven anzeigen", fontsize=11, weight="bold")
checks_ax = fig.add_axes([0.80, 0.760, 0.17, 0.100])
curve_checks = CheckButtons(checks_ax, ["Sinus", "Cosinus"],
                             [True, False])
for label, color in zip(curve_checks.labels, ["#235ab4", "#c26c20"]):
    label.set_color(color)

fig.text(0.79, 0.708, "Bedeutung der Parameter", fontsize=11, weight="bold")
explanations = [
    (0.666, r"$a$  Amplitude: $|a|$"),
    (0.628, "      a < 0: Spiegelung"),
    (0.574, r"$b$  horizontale Stauchung"),
    (0.536, r"      Periode $T=2\pi/b$"),
    (0.482, r"$c$  Verschiebung in x-Richtung"),
    (0.444, "      c > 0: nach rechts"),
    (0.390, r"$d$  Verschiebung nach oben"),
    (0.352, "      d < 0: nach unten"),
]
for y, explanation in explanations:
    fig.text(0.79, y, explanation, fontsize=9.4, va="center")

# Ranges and steps match the original GeoGebra program.
slider_specs = [
    ("a", "Amplitude a", -3.0, 3.0, 1.0, 0.1, 0.270),
    ("b", "Faktor b", 0.1, 4.0, 1.0, 0.1, 0.207),
    ("c", "Verschiebung c", -6.3, 6.3, 0.0, 0.1, 0.144),
    ("d", "Verschiebung d", -3.0, 3.0, 0.0, 0.1, 0.081),
]
sliders = {}
for key, label, minimum, maximum, initial, step, y in slider_specs:
    slider_ax = fig.add_axes([0.25, y, 0.47, 0.026])
    sliders[key] = Slider(slider_ax, label, minimum, maximum,
                          valinit=initial, valstep=step, valfmt="%.1f")


def update(_value=None):
    a = sliders["a"].val
    b = sliders["b"].val
    c = sliders["c"].val
    d = sliders["d"].val
    line_sin.set_ydata(a * np.sin(b * (X - c)) + d)
    line_cos.set_ydata(a * np.cos(b * (X - c)) + d)

    # Keep large amplitudes and vertical offsets visible.
    bound = max(4.0, abs(a) + abs(d) + 0.4)
    ax.set_ylim(-bound, bound)
    fig.canvas.draw_idle()


def toggle_curve(label):
    line = {"Sinus": line_sin, "Cosinus": line_cos}[label]
    line.set_visible(not line.get_visible())
    fig.canvas.draw_idle()


for slider in sliders.values():
    slider.on_changed(update)
curve_checks.on_clicked(toggle_curve)

reset_ax = fig.add_axes([0.82, 0.071, 0.13, 0.047])
reset_button = Button(reset_ax, "Zurücksetzen")


def reset(_event):
    for key, default in DEFAULTS.items():
        sliders[key].set_val(default)
    for index, desired in enumerate((True, False)):
        if curve_checks.get_status()[index] != desired:
            curve_checks.set_active(index)
    update()


reset_button.on_clicked(reset)
update()
plt.show()
