import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider, CheckButtons

# ------------------------------------------------------------
# Federschwerependel – animierte Darstellung
# ------------------------------------------------------------
# Physikalisches Modell:
#   m * y'' = m*g - D*(L - L0)
#
# y wächst nach unten.
# L ist die aktuelle Federlänge.
# ------------------------------------------------------------

# Grundparameter
g = 9.81          # m/s²
L0 = 0.30         # unbelastete Federlänge in m
A0 = 0.08         # Anfangsamplitude in m
D0 = 12.0         # Federhärte in N/m
m0 = 0.25         # Masse in kg

# Zeichenparameter
x_spring = 0.0
spring_width = 0.035
mass_width = 0.13
mass_height = 0.075
force_scale = 0.055  # m pro N für Pfeillängen

fig, ax = plt.subplots(figsize=(8.8, 8.0))
plt.subplots_adjust(left=0.08, right=0.72, bottom=0.51, top=0.94)

ax.set_xlim(-0.55, 0.55)
ax.set_ylim(1.05, -0.05)   # y-Achse nach unten
ax.set_aspect('equal')
ax.axis('off')
ax.set_title("Federschwerependel: Bewegung und Kräfte", fontsize=15, pad=18)

# Aufhängung
ax.plot([-0.24, 0.24], [0.02, 0.02], color='black', lw=2)

# Gleichgewichtslage – wird bei Änderungen von D oder m angepasst
eq_line, = ax.plot([-0.05, 0.48], [0, 0], ls='--', lw=1.4, color='tab:blue', alpha=0.9)
eq_label = ax.text(0.30, 0, "Gleichgewichtslage", va='bottom', fontsize=10, color='tab:blue')

# Feder
spring_line, = ax.plot([], [], color='black', lw=1.15)

# Masse
mass = plt.Rectangle(
    (-mass_width / 2, 0.5),
    mass_width,
    mass_height,
    facecolor='tab:green',
    edgecolor='black',
    lw=1.2
)
ax.add_patch(mass)

# Einzelkräfte links neben dem Massekörper.
# Beide beginnen am selben Angriffspunkt, damit ihre Beträge direkt
# miteinander verglichen werden können.
Fg_arrow = ax.annotate(
    "", xy=(0, 0), xytext=(0, 0),
    arrowprops=dict(arrowstyle='-|>', lw=2.3, color='tab:red')
)
Ff_arrow = ax.annotate(
    "", xy=(0, 0), xytext=(0, 0),
    arrowprops=dict(arrowstyle='-|>', lw=2.3, color='tab:blue')
)
fg_label = ax.text(0, 0, r"$F_{\mathrm{G}}$", color='tab:red', fontsize=11, ha='right', va='center')
ff_label = ax.text(0, 0, r"$F_{\mathrm{F}}$", color='tab:blue', fontsize=11, ha='right', va='center')

# Resultierende Kraft noch weiter links
Fres_arrow = ax.annotate(
    "", xy=(0, 0), xytext=(0, 0),
    arrowprops=dict(arrowstyle='-|>', lw=2.7, color='tab:orange')
)
fres_label = ax.text(0, 0, r"$F_{\mathrm{res}}$", color='tab:orange', fontsize=11, ha='right', va='center')

# Auslenkungspfeil rechts
s_arrow = ax.annotate(
    "", xy=(0, 0), xytext=(0, 0),
    arrowprops=dict(arrowstyle='<->', lw=1.8, color='tab:purple')
)
s_label = ax.text(0, 0, r"$s$", color='tab:purple', fontsize=11, ha='left', va='center')

# Wertebox rechts neben der Simulation
info = fig.text(
    0.76, 0.82, "",
    fontsize=10.5,
    va='top',
    ha='left',
    bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="0.65")
)

# Checkboxen für die Kraftdarstellung
ax_checks = plt.axes([0.75, 0.29, 0.22, 0.12])
ax_checks.set_frame_on(False)
check_buttons = CheckButtons(
    ax_checks,
    ["Einzelkräfte", "Resultierende Kraft"],
    [True, True]
)

# Steuerung: Schwingungsphase, Amplitude, Federhärte D und Masse m
# Der Phasenregler läuft während der Animation mit. Wird er von Hand
# verschoben, pausiert die Animation und kann schrittweise untersucht werden.
ax_phase = plt.axes([0.16, 0.18, 0.48, 0.028])
phase_slider = Slider(
    ax_phase,
    r"Phase $\varphi$ [°]",
    0.0,
    360.0,
    valinit=0.0,
    valstep=1.0
)

ax_amp = plt.axes([0.16, 0.135, 0.48, 0.028])
amp_slider = Slider(ax_amp, "Amplitude", 0.01, 0.15, valinit=A0, valstep=0.005)

ax_D = plt.axes([0.16, 0.09, 0.48, 0.028])
D_slider = Slider(ax_D, r"Federhärte $D$ [N/m]", 8.0, 25.0, valinit=D0, valstep=0.5)

ax_m = plt.axes([0.16, 0.045, 0.48, 0.028])
m_slider = Slider(ax_m, r"Masse $m$ [kg]", 0.10, 0.40, valinit=m0, valstep=0.01)

ax_btn = plt.axes([0.76, 0.07, 0.13, 0.065])
pause_button = Button(ax_btn, "Pause")

paused = False
frame_counter = 0
show_individual_forces = True
show_resultant_force = True
updating_phase_slider = False

# Zeitdiagramm unmittelbar unter der mechanischen Animation.
# Drei eigene farbige y-Skalen: reale Werte und reale Einheiten, nicht normiert.
ax_time = fig.add_axes([0.12, 0.28, 0.48, 0.19])
ax_vel = ax_time.twinx()
ax_acc = ax_time.twinx()
ax_acc.spines["right"].set_position(("outward", 54))
ax_time.set_xlabel("Zeit t in s", fontsize=9)
ax_time.set_ylabel("s in m", color="tab:purple", fontsize=9)
ax_vel.set_ylabel("v in m/s", color="tab:blue", fontsize=9)
ax_acc.set_ylabel("a in m/s²", color="tab:orange", fontsize=9)
for plot_ax, color in ((ax_time, "tab:purple"), (ax_vel, "tab:blue"), (ax_acc, "tab:orange")):
    plot_ax.tick_params(axis="y", colors=color, labelsize=8)
ax_time.tick_params(axis="x", labelsize=8)
ax_time.grid(True, alpha=0.25)
ax_time.set_title("Zeitverläufe über zwei Perioden", fontsize=10)

line_s, = ax_time.plot([], [], color="tab:purple", lw=1.7, label="s(t)")
line_v, = ax_vel.plot([], [], color="tab:blue", lw=1.7, label="v(t)")
line_a, = ax_acc.plot([], [], color="tab:orange", lw=1.7, label="a(t)")
cursor = ax_time.axvline(0.0, color="0.2", ls="--", lw=1.2)
dot_s, = ax_time.plot([], [], "o", color="tab:purple", ms=4)
dot_v, = ax_vel.plot([], [], "o", color="tab:blue", ms=4)
dot_a, = ax_acc.plot([], [], "o", color="tab:orange", ms=4)

ax_curve_checks = fig.add_axes([0.75, 0.47, 0.22, 0.13])
ax_curve_checks.set_frame_on(False)
curve_checks = CheckButtons(ax_curve_checks, ["s(t)", "v(t)", "a(t)"], [True, True, True])
show_curves = [True, True, True]


def update_time_graph(phase, omega, amp, frame_time):
    """Zwei Perioden und aktuellen Zeitpunkt; reale Achsenwerte je Größe."""
    T = 2 * np.pi / omega
    ts = np.linspace(0, 2 * T, 700)
    phases = omega * ts
    line_s.set_data(ts, amp * np.cos(phases))
    line_v.set_data(ts, -amp * omega * np.sin(phases))
    line_a.set_data(ts, -amp * omega**2 * np.cos(phases))

    ax_time.set_xlim(0, 2 * T)
    ax_time.set_ylim(-1.15 * amp, 1.15 * amp)
    ax_vel.set_ylim(-1.15 * amp * omega, 1.15 * amp * omega)
    ax_acc.set_ylim(-1.15 * amp * omega**2, 1.15 * amp * omega**2)

    cursor_time = frame_time % (2 * T)
    cursor.set_xdata([cursor_time, cursor_time])
    dot_s.set_data([cursor_time], [amp * np.cos(phase)])
    dot_v.set_data([cursor_time], [-amp * omega * np.sin(phase)])
    dot_a.set_data([cursor_time], [-amp * omega**2 * np.cos(phase)])

    for visible, graph, dot in zip(
        show_curves, (line_s, line_v, line_a), (dot_s, dot_v, dot_a)
    ):
        graph.set_visible(visible)
        dot.set_visible(visible)


def toggle_curve(label):
    index = {"s(t)": 0, "v(t)": 1, "a(t)": 2}[label]
    show_curves[index] = not show_curves[index]
    fig.canvas.draw_idle()


curve_checks.on_clicked(toggle_curve)


def spring_coordinates(y_top, y_bottom, coils=16):
    """Erzeugt eine dünne, optisch realistischere Schraubenfeder."""
    lead = 0.035
    body_top = y_top + lead
    body_bottom = y_bottom - lead

    # Gerade Endstücke
    x1 = np.array([x_spring, x_spring])
    y1 = np.array([y_top, body_top])

    # Sinusförmiger Federkörper
    u = np.linspace(0, 1, 420)
    y2 = body_top + (body_bottom - body_top) * u
    envelope = np.sin(np.pi * u) ** 0.25
    x2 = x_spring + spring_width * envelope * np.sin(2 * np.pi * coils * u)

    x3 = np.array([x_spring, x_spring])
    y3 = np.array([body_bottom, y_bottom])

    return np.concatenate([x1, x2, x3]), np.concatenate([y1, y2, y3])


def update_force_visibility():
    """Blendet die ausgewählten Kraftdarstellungen ein oder aus."""
    for artist in (Fg_arrow, Ff_arrow, fg_label, ff_label):
        artist.set_visible(show_individual_forces)

    for artist in (Fres_arrow, fres_label):
        artist.set_visible(show_resultant_force)


def update(frame):
    global frame_counter, updating_phase_slider

    if not paused:
        frame_counter += 1

    dt = 0.035

    # Aktuelle Einstellungen
    amp = amp_slider.val
    D = D_slider.val
    m = m_slider.val

    # Gleichgewichtslage und Kreisfrequenz
    L_eq = L0 + m * g / D
    omega = np.sqrt(D / m)

    # Während des normalen Ablaufs wird die Phase aus der Zeit berechnet.
    # Im Pausenmodus bestimmt der Phasenregler die Position direkt.
    if paused:
        phase_deg = phase_slider.val
        phase = np.deg2rad(phase_deg)
        chart_time = phase / omega
    else:
        t = frame_counter * dt
        phase = omega * t
        chart_time = t
        phase_deg = np.degrees(phase) % 360.0

        # Regler während der Animation mitführen, ohne dadurch zu pausieren.
        updating_phase_slider = True
        phase_slider.set_val(phase_deg)
        updating_phase_slider = False

    # Auslenkung relativ zur Gleichgewichtslage.
    # Konvention: Oberhalb der Gleichgewichtslage ist s positiv,
    # unterhalb der Gleichgewichtslage ist s negativ.
    s = amp * np.cos(phase)
    L = L_eq - s
    mass_center_y = L

    # Kräfte
    Fg = m * g
    spring_extension = L - L0
    Ff = D * spring_extension
    F_res = Fg - Ff

    # Gleichgewichtslage
    eq_line.set_ydata([L_eq, L_eq])
    eq_label.set_position((0.30, L_eq - 0.012))

    # Feder
    spring_bottom = mass_center_y - mass_height / 2
    xs, ys = spring_coordinates(0.02, spring_bottom)
    spring_line.set_data(xs, ys)

    # Masse
    mass.set_xy((-mass_width / 2, mass_center_y - mass_height / 2))

    # Einzelkräfte links neben der Masse – gemeinsamer Angriffspunkt
    x_force = -0.17

    # Gewichtskraft nach unten
    fg_len = Fg * force_scale
    Fg_arrow.xy = (x_force, mass_center_y + fg_len)
    Fg_arrow.set_position((x_force, mass_center_y))
    fg_label.set_position((x_force - 0.025, mass_center_y + fg_len * 0.55))

    # Federkraft nach oben
    ff_len = Ff * force_scale
    Ff_arrow.xy = (x_force, mass_center_y - ff_len)
    Ff_arrow.set_position((x_force, mass_center_y))
    ff_label.set_position((x_force - 0.025, mass_center_y - ff_len * 0.55))

    # Resultierende Kraft noch weiter links.
    # Positive Werte zeigen nach unten, negative nach oben.
    x_resultant = -0.34
    fres_len = abs(F_res) * force_scale
    direction = 1 if F_res >= 0 else -1
    Fres_arrow.xy = (x_resultant, mass_center_y + direction * fres_len)
    Fres_arrow.set_position((x_resultant, mass_center_y))

    if fres_len > 0.004:
        fres_label.set_position(
            (x_resultant - 0.025, mass_center_y + direction * fres_len * 0.55)
        )
    else:
        fres_label.set_position((x_resultant - 0.025, mass_center_y - 0.02))

    # Auslenkung relativ zur Gleichgewichtslage
    x_s = 0.19
    s_arrow.xy = (x_s, mass_center_y)
    s_arrow.set_position((x_s, L_eq))
    s_label.set_position((x_s + 0.025, (mass_center_y + L_eq) / 2))

    # Wertebox im mathematischen Schriftsatz.
    # Kraftwerte erscheinen nur bei aktivierter Darstellung.
    info_lines = [
        "Aktuelle Werte",
        "",
        rf"$D = {D:.1f}\,\mathrm{{N/m}}$",
        rf"$m = {m:.2f}\,\mathrm{{kg}}$",
        "",
        rf"$s = {s * 100:+.1f}\,\mathrm{{cm}}$",
    ]

    if show_individual_forces:
        info_lines.extend([
            rf"$F_{{\mathrm{{G}}}} = {Fg:.2f}\,\mathrm{{N}}$",
            rf"$F_{{\mathrm{{F}}}} = {Ff:.2f}\,\mathrm{{N}}$",
        ])

    if show_resultant_force:
        info_lines.append(rf"$F_{{\mathrm{{res}}}} = {F_res:+.2f}\,\mathrm{{N}}$")

    info.set_text("\n".join(info_lines))

    update_time_graph(phase, omega, amp, chart_time)

    update_force_visibility()

    return (
        spring_line, mass, eq_line, eq_label,
        Fg_arrow, Ff_arrow, fg_label, ff_label,
        Fres_arrow, fres_label,
        s_arrow, s_label, info,
        line_s, line_v, line_a, cursor, dot_s, dot_v, dot_a
    )


def toggle_pause(event):
    global paused, frame_counter

    if paused:
        # Beim Weiterlaufen an die aktuell gewählte Phase anschließen.
        D = D_slider.val
        m = m_slider.val
        omega = np.sqrt(D / m)
        phase = np.deg2rad(phase_slider.val)
        frame_counter = int(phase / (omega * 0.035))
        paused = False
        pause_button.label.set_text("Pause")
    else:
        paused = True
        pause_button.label.set_text("Weiter")


def toggle_force_display(label):
    global show_individual_forces, show_resultant_force

    if label == "Einzelkräfte":
        show_individual_forces = not show_individual_forces
    elif label == "Resultierende Kraft":
        show_resultant_force = not show_resultant_force

    update_force_visibility()
    fig.canvas.draw_idle()


def set_phase_manually(value):
    """Manuelles Verschieben des Phasenreglers pausiert die Animation."""
    global paused

    if updating_phase_slider:
        return

    paused = True
    pause_button.label.set_text("Weiter")
    fig.canvas.draw_idle()


pause_button.on_clicked(toggle_pause)
check_buttons.on_clicked(toggle_force_display)
phase_slider.on_changed(set_phase_manually)

ani = FuncAnimation(
    fig,
    update,
    interval=35,
    blit=False,
    cache_frame_data=False
)

plt.show()
