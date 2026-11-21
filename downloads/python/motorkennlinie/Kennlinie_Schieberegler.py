# Motorkennlinie_mit_Schiebereglern.py
# Option B: Wirkungsgrad wird physikalisch auf 0..1 begrenzt (clip),
# damit nichts abgeschnitten wird und η-Achse fest 0..1 bleiben kann.
# Läuft direkt in Python (Thonny/IDLE/VS Code "Run"), ohne Streamlit/Terminal.

import matplotlib
# Falls Slider in Thonny/Inline nicht sauber laufen: TkAgg erzwingen
matplotlib.use("TkAgg")

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.ticker import FuncFormatter


# ===============================
# Komma-Formatter
# ===============================
def comma_formatter(decimals: int) -> FuncFormatter:
    def _f(x, pos):
        return f"{x:.{decimals}f}".replace(".", ",")
    return FuncFormatter(_f)


# ===============================
# Zusätzliche y-Achse links
# ===============================
def left_axis(base_ax, offset):
    ax = base_ax.twinx()
    ax.yaxis.set_label_position("left")
    ax.yaxis.tick_left()
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_position(("axes", offset))
    ax.spines["left"].set_visible(True)
    ax.patch.set_visible(False)
    return ax


# ===============================
# Motor-Modell: Kennlinie aus Parametern
# ===============================
POINTS = 300

def compute(M_max, n0, I_0, I_max, U):
    M = np.linspace(0, M_max, POINTS)          # Drehmoment [Nm]
    n = n0 * (1 - M / M_max)                   # Drehzahl [1/s]
    omega = 2 * np.pi * n                      # [rad/s]

    I = I_0 + (I_max - I_0) * (M / M_max)      # Strom [A]
    P_mech = M * omega                         # mech. Leistung [W]
    P_el = U * I                               # el. Leistung [W]

    # Wirkungsgrad
    with np.errstate(divide="ignore", invalid="ignore"):
        eta = P_mech / P_el

    # NaN/Inf -> 0, danach physikalisch begrenzen
    eta = np.nan_to_num(eta, nan=0.0, posinf=0.0, neginf=0.0)
    eta = np.clip(eta, 0.0, 1.0)

    return M, n, I, P_mech, eta

def top_with_margin(arr, min_top=1e-6, margin=0.12):
    m = float(np.nanmax(arr))
    m = max(m, min_top)
    return m * (1.0 + margin)


# ===============================
# Startparameter
# ===============================
M_max0 = 0.050   # Nm
n00    = 50.0   # 1/s  (3000 rpm = 50 1/s)
I_00   = 0.80   # A
I_max0 = 0.50   # A
U0     = 4.0   # V

# Initial berechnen
M, n, I, P_mech, eta = compute(M_max0, n00, I_00, I_max0, U0)


# ===============================
# Plot aufbauen
# ===============================
fig, ax_n = plt.subplots(figsize=(12, 7))
fig.subplots_adjust(left=0.52, bottom=0.33)

ax_n.set_title("Motorkennlinie – Schieberegler (alle y-Achsen links)")
ax_n.set_xlabel("Drehmoment M [Nm]")
ax_n.set_ylabel("Drehzahl n [1/s]")
ax_n.grid(True)

ln_n, = ax_n.plot(M, n, lw=2, color="tab:blue", label="Drehzahl n [1/s]")

ax_I = left_axis(ax_n, -0.18)
ax_I.set_ylabel("Strom I [A]")
ln_I, = ax_I.plot(M, I, lw=2, color="tab:green", label="Strom I [A]")

ax_P = left_axis(ax_n, -0.36)
ax_P.set_ylabel("mechanische Leistung P [W]")
ln_P, = ax_P.plot(M, P_mech, lw=2, color="tab:red", label="P_mech [W]")

ax_eta = left_axis(ax_n, -0.54)
ax_eta.set_ylabel("Wirkungsgrad η [-]")
ln_eta, = ax_eta.plot(M, eta, lw=2, color="tab:purple", label="η")

# Komma auf Achsen
ax_n.xaxis.set_major_formatter(comma_formatter(2))   # Drehmoment
ax_n.yaxis.set_major_formatter(comma_formatter(2))   # Drehzahl
ax_I.yaxis.set_major_formatter(comma_formatter(2))   # Strom
ax_P.yaxis.set_major_formatter(comma_formatter(2))   # Leistung
ax_eta.yaxis.set_major_formatter(comma_formatter(2)) # Wirkungsgrad

# X-Limits für ALLE Achsen gleich
for a in (ax_n, ax_I, ax_P, ax_eta):
    a.set_xlim(0, M_max0)

# Y-Limits Start bei 0 + initiale Skalierung
ax_n.set_ylim(0, top_with_margin(n, min_top=1e-3))
ax_I.set_ylim(0, top_with_margin(I, min_top=1e-3))
ax_P.set_ylim(0, top_with_margin(P_mech, min_top=1e-3))
ax_eta.set_ylim(0, 1)  # bleibt stabil, weil eta geclippt ist

# Legende
ax_n.legend([ln_n, ln_I, ln_P, ln_eta],
            [l.get_label() for l in (ln_n, ln_I, ln_P, ln_eta)],
            loc="upper right")


# ===============================
# Slider-Achsen
# ===============================
axcolor = "lightgoldenrodyellow"
ax_Mmax = plt.axes([0.15, 0.23, 0.70, 0.03], facecolor=axcolor)
ax_n0   = plt.axes([0.15, 0.19, 0.70, 0.03], facecolor=axcolor)
ax_I0   = plt.axes([0.15, 0.15, 0.70, 0.03], facecolor=axcolor)
ax_Imax = plt.axes([0.15, 0.11, 0.70, 0.03], facecolor=axcolor)
ax_U    = plt.axes([0.15, 0.07, 0.70, 0.03], facecolor=axcolor)

s_Mmax = Slider(ax_Mmax, "M_max [Nm]", 0.05, 1.0,   valinit=M_max0)
s_n0   = Slider(ax_n0,   "n0 [1/s]",   1.0, 300.0,  valinit=n00)
s_I0   = Slider(ax_I0,   "I0 [A]",     0.0, 5.0,   valinit=I_00)
s_Imax = Slider(ax_Imax, "I_max [A]",  0.1, 5.0,  valinit=I_max0)
s_U    = Slider(ax_U,    "U [V]",      1.0, 12.0,   valinit=U0)


# ===============================
# Update: Daten + Skalierung
# ===============================
def update(val):
    M, n, I, P_mech, eta = compute(
        s_Mmax.val, s_n0.val, s_I0.val, s_Imax.val, s_U.val
    )

    ln_n.set_data(M, n)
    ln_I.set_data(M, I)
    ln_P.set_data(M, P_mech)
    ln_eta.set_data(M, eta)

    # X-Limits für ALLE Achsen gleich (wichtig bei twinx!)
    for a in (ax_n, ax_I, ax_P, ax_eta):
        a.set_xlim(0, s_Mmax.val)

    # Y-Limits neu (Start bei 0)
    ax_n.set_ylim(0, top_with_margin(n, min_top=1e-3))
    ax_I.set_ylim(0, top_with_margin(I, min_top=1e-3))
    ax_P.set_ylim(0, top_with_margin(P_mech, min_top=1e-3))
    ax_eta.set_ylim(0, 1)  # bleibt 0..1, da eta geclippt ist

    fig.canvas.draw_idle()


for s in (s_Mmax, s_n0, s_I0, s_Imax, s_U):
    s.on_changed(update)


# ===============================
# Reset-Button
# ===============================
ax_reset = plt.axes([0.86, 0.015, 0.12, 0.04])
btn_reset = Button(ax_reset, "Reset")

def reset(event):
    s_Mmax.reset()
    s_n0.reset()
    s_I0.reset()
    s_Imax.reset()
    s_U.reset()

btn_reset.on_clicked(reset)


plt.show()
