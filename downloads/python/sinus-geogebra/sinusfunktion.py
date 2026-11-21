"""Interaktive Sinusfunktion: Python-Portierung der GeoGebra-Seite.

Ausgangspunkt: KN-RBG/Physik_Test_01/index.html
  f(x) = a * sin(b * (x - c)) + d

Installation: pip install numpy matplotlib
Start:        python sinusfunktion.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

DEFAULTS = {"a": 1.0, "b": 1.0, "c": 0.0, "d": 0.0}
X = np.linspace(-2 * np.pi, 2 * np.pi, 1600)

fig, ax = plt.subplots(figsize=(11.5, 7))
fig.canvas.manager.set_window_title("Sinusfunktion interaktiv")
fig.subplots_adjust(left=0.09, right=0.95, top=0.90, bottom=0.34)

ax.set_title("Sinusfunktion interaktiv", fontsize=16)
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

line, = ax.plot(X, np.sin(X), color="#235ab4", linewidth=2.7)
formula = fig.text(0.09, 0.94,
                   r"$f(x) = a\cdot\sin\!\left(b\cdot(x-c)\right)+d$",
                   fontsize=14)

# Matplotlib widgets keep the exact ranges and step sizes of the GeoGebra page.
slider_specs = [
    ("a", "Amplitude a", -3.0, 3.0, 1.0, 0.1, 0.245),
    ("b", "Faktor b", 0.1, 4.0, 1.0, 0.1, 0.195),
    ("c", "Verschiebung c", -6.3, 6.3, 0.0, 0.1, 0.145),
    ("d", "Verschiebung d", -3.0, 3.0, 0.0, 0.1, 0.095),
]

sliders = {}
for key, label, minimum, maximum, initial, step, y in slider_specs:
    slider_ax = fig.add_axes([0.26, y, 0.56, 0.026])
    sliders[key] = Slider(
        ax=slider_ax,
        label=label,
        valmin=minimum,
        valmax=maximum,
        valinit=initial,
        valstep=step,
        valfmt="%.1f",
    )

def update(_value=None):
    a = sliders["a"].val
    b = sliders["b"].val
    c = sliders["c"].val
    d = sliders["d"].val
    line.set_ydata(a * np.sin(b * (X - c)) + d)
    fig.canvas.draw_idle()

for slider in sliders.values():
    slider.on_changed(update)

reset_ax = fig.add_axes([0.83, 0.038, 0.13, 0.047])
reset_button = Button(reset_ax, "Zurücksetzen")

def reset(_event):
    for key, default in DEFAULTS.items():
        sliders[key].set_val(default)

reset_button.on_clicked(reset)
update()
plt.show()
