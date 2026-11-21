import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.patches import Circle, FancyArrowPatch, Arc, ConnectionPatch
from matplotlib.path import Path as MplPath


# ------------------------------------------------------------
# Interaktives Zeigerdiagramm zur Entstehung einer Sinuskurve
# Darstellung bewusst nah an der Vorlage aus dem Schulmaterial.
# ------------------------------------------------------------

MAX_ALPHA = 4 * np.pi          # 0 ... 4pi = 0 ... 720 Grad
RADIUS = 1.0
ANIMATION_STEP = np.deg2rad(2)
INTERVAL_MS = 25


class Zeigerdiagramm:
    def __init__(self):
        self.alpha = 0.0
        self.running = False

        self.fig = plt.figure(figsize=(14.8, 7.0), facecolor="white")
        self.fig.canvas.manager.set_window_title("Zeigerdiagramm und Sinuskurve")

        # Kreis und Sinusdarstellung haben exakt dieselbe vertikale Lage und Höhe.
        self.ax_circle = self.fig.add_axes([0.0135, 0.28, 0.3265, 0.64])
        self.ax_sine = self.fig.add_axes([0.34, 0.28, 0.625, 0.64])

        # Skalenbereich darunter
        self.ax_rad = self.fig.add_axes([0.34, 0.195, 0.625, 0.055])
        self.ax_deg = self.fig.add_axes([0.34, 0.125, 0.625, 0.055])

        # Regler exakt so lang wie die Sinusdarstellung, also 0 ... 720 Grad.
        self.ax_slider = self.fig.add_axes([0.34, 0.075, 0.625, 0.03])

        # Beschriftung und Buttons deutlich weiter unten, damit nichts den Regler überlagert.
        self.ax_play = self.fig.add_axes([0.84, 0.012, 0.055, 0.045])
        self.ax_reset = self.fig.add_axes([0.91, 0.012, 0.055, 0.045])

        self._setup_circle_axis()
        self._setup_sine_axis()
        self._setup_scale_axes()
        self._setup_controls()
        self._setup_artists()

        self.timer = self.fig.canvas.new_timer(interval=INTERVAL_MS)
        self.timer.add_callback(self._animation_tick)

        self.update(0.0)

    def _apply_grid_style(self, ax, x_major, x_minor, y_major):
        ax.set_xticks(x_major)
        ax.set_xticks(x_minor, minor=True)
        ax.set_yticks(y_major)
        ax.grid(True, which="major", linewidth=0.8, color="0.72")
        ax.grid(True, which="minor", linewidth=0.55, color="0.82")
        ax.tick_params(which="both", length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)

    def _setup_circle_axis(self):
        ax = self.ax_circle
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(-1.35, 1.35)
        ax.set_ylim(-1.35, 1.35)

        self._apply_grid_style(
            ax,
            np.arange(-1.25, 1.26, 0.5),
            np.arange(-1.25, 1.26, 0.25),
            np.arange(-1.25, 1.26, 0.25),
        )
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.axhline(0, color="black", linewidth=1.2, linestyle=(0, (5, 3)), zorder=2)

        self.circle = Circle((0, 0), RADIUS, fill=False, color="red", linewidth=2.8, zorder=4)
        ax.add_patch(self.circle)

        omega_radius = 1.13
        omega_angles = np.linspace(np.deg2rad(72), np.deg2rad(145), 40)
        omega_vertices = np.column_stack((
            omega_radius * np.cos(omega_angles),
            omega_radius * np.sin(omega_angles)
        ))
        omega_codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(omega_vertices) - 1)
        omega_path = MplPath(omega_vertices, omega_codes)
        omega_arrow = FancyArrowPatch(
            path=omega_path,
            arrowstyle="-|>",
            mutation_scale=14,
            color="black",
            linewidth=1.8,
            zorder=7
        )
        ax.add_patch(omega_arrow)
        ax.text(-0.48, 1.20, r"$\omega$", fontsize=13, ha="center", va="center")

    def _setup_sine_axis(self):
        ax = self.ax_sine
        ax.set_xlim(0, MAX_ALPHA)
        ax.set_ylim(-1.35, 1.35)

        major_x = np.arange(0, MAX_ALPHA + 1e-9, np.pi / 2)
        minor_x = np.arange(0, MAX_ALPHA + 1e-9, np.pi / 8)
        y_ticks = np.arange(-1.25, 1.26, 0.25)
        self._apply_grid_style(ax, major_x, minor_x, y_ticks)

        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.axhline(0, color="black", linewidth=1.9, zorder=3)
        ax.axhline(1, color="blue", linewidth=1.0, linestyle=(0, (6, 3)), zorder=2)
        ax.axhline(-1, color="blue", linewidth=1.0, linestyle=(0, (6, 3)), zorder=2)

        ax.annotate(
            "", xy=(0, 1.12), xytext=(0, -1.0),
            arrowprops=dict(arrowstyle="->", color="black", linewidth=1.9),
            annotation_clip=False, zorder=5
        )
        ax.text(-0.19, 1.04, r"$y$", fontsize=14, ha="right", va="center")

        ax.annotate(
            "", xy=(MAX_ALPHA * 0.94, 0), xytext=(0, 0),
            arrowprops=dict(arrowstyle="->", color="black", linewidth=1.6),
            annotation_clip=False, zorder=5
        )
        ax.text(MAX_ALPHA * 0.935, -0.08, r"$t$", fontsize=13, ha="right", va="top")

    def _setup_scale_axes(self):
        ax = self.ax_rad
        ax.set_xlim(0, MAX_ALPHA)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ticks = np.arange(0, MAX_ALPHA + 1e-9, np.pi / 2)
        labels = [
            r"$0$", r"$\frac{\pi}{2}$", r"$\pi$", r"$\frac{3\pi}{2}$",
            r"$2\pi$", r"$\frac{5\pi}{2}$", r"$3\pi$", r"$\frac{7\pi}{2}$", r"$4\pi$"
        ]
        ax.annotate("", xy=(MAX_ALPHA, 0.54), xytext=(0, 0.54),
                    arrowprops=dict(arrowstyle="->", color="red", linewidth=1.4))
        for x, lab in zip(ticks, labels):
            ax.plot([x, x], [0.46, 0.62], color="0.25", linewidth=0.8)
            ax.text(x, 0.15, lab, fontsize=11, ha="center", va="center")
        ax.text(MAX_ALPHA * 0.995, 0.80, r"$\alpha$ (Bogenmaß)", fontsize=11, ha="right", va="center")

        ax = self.ax_deg
        ax.set_xlim(0, MAX_ALPHA)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.annotate("", xy=(MAX_ALPHA, 0.54), xytext=(0, 0.54),
                    arrowprops=dict(arrowstyle="->", color="red", linewidth=1.4))
        for x, deg in zip(ticks, range(0, 721, 90)):
            ax.plot([x, x], [0.46, 0.62], color="0.25", linewidth=0.8)
            ax.text(x, 0.15, f"{deg}", fontsize=11, ha="center", va="center")
        ax.text(MAX_ALPHA * 0.995, 0.80, r"$\alpha$ (Winkel)", fontsize=11, ha="right", va="center")

    def _setup_controls(self):
        self.slider = Slider(
            self.ax_slider,
            "",
            0,
            MAX_ALPHA,
            valinit=0,
            valstep=np.deg2rad(1),
            color="0.70"
        )
        self.slider.valtext.set_visible(False)
        self.slider.on_changed(self._slider_changed)

        self.btn_play = Button(self.ax_play, "Start")
        self.btn_play.on_clicked(self._toggle_animation)

        self.btn_reset = Button(self.ax_reset, "Zurück")
        self.btn_reset.on_clicked(self._reset)

    def _setup_artists(self):
        self.phasor_arrow = FancyArrowPatch(
            posA=(0, 0), posB=(1.03, 0),
            arrowstyle="-|>", mutation_scale=18,
            color="red", linewidth=2.8, zorder=9,
            shrinkA=0, shrinkB=0
        )
        self.ax_circle.add_patch(self.phasor_arrow)

        (self.projection_to_baseline,) = self.ax_circle.plot(
            [], [], color="black", linestyle=":", linewidth=1.25, zorder=6
        )

        self.alpha_arc = Arc(
            (0, 0), 0.76, 0.76,
            angle=0, theta1=0, theta2=0,
            color="black", linewidth=1.25, zorder=7
        )
        self.ax_circle.add_patch(self.alpha_arc)
        self.alpha_text = self.ax_circle.text(
            0.22, 0.0, r"$\alpha$", fontsize=13,
            ha="center", va="center", zorder=8
        )

        (self.sine_line,) = self.ax_sine.plot([], [], color="blue", linewidth=1.6, zorder=6)
        (self.sine_dot,) = self.ax_sine.plot([], [], "o", color="red", markersize=5.5, zorder=7)

        (self.vertical_marker,) = self.ax_sine.plot(
            [], [], color="black", linestyle=":", linewidth=1.65, alpha=0.85, zorder=5
        )

        self.projection_to_sine = ConnectionPatch(
            xyA=(1, 0), coordsA="data", axesA=self.ax_circle,
            xyB=(0, 0), coordsB="data", axesB=self.ax_sine,
            color="black", linestyle=":", linewidth=1.15,
            zorder=5, clip_on=False
        )
        self.fig.add_artist(self.projection_to_sine)

        # Beschriftung links von den Buttons und unterhalb des Reglers.
        self.angle_text = self.fig.text(0.81, 0.034, "", fontsize=10.5, ha="right", va="center")

    def _slider_changed(self, value):
        self.alpha = float(value)
        self.update(self.alpha)

    def _toggle_animation(self, _event):
        self.running = not self.running
        self.btn_play.label.set_text("Stopp" if self.running else "Start")
        if self.running:
            self.timer.start()
        else:
            self.timer.stop()
        self.fig.canvas.draw_idle()

    def _reset(self, _event):
        self.running = False
        self.timer.stop()
        self.btn_play.label.set_text("Start")
        self.slider.set_val(0)

    def _animation_tick(self):
        if not self.running:
            return
        new_alpha = self.alpha + ANIMATION_STEP
        if new_alpha > MAX_ALPHA:
            new_alpha = 0.0
        self.slider.set_val(new_alpha)

    def update(self, alpha):
        x = np.cos(alpha)
        y = np.sin(alpha)

        arrow_factor = 1.03
        arrow_x = arrow_factor * x
        arrow_y = arrow_factor * y
        self.phasor_arrow.set_positions((0, 0), (arrow_x, arrow_y))

        self.projection_to_baseline.set_data([x, x], [y, 0])
        self.projection_to_sine.xy1 = (x, y)
        self.projection_to_sine.xy2 = (alpha, y)

        angle_deg = np.degrees(alpha) % 360.0
        if np.isclose(angle_deg, 0.0) and alpha > 0:
            angle_deg = 360.0

        self.alpha_arc.theta1 = 0
        self.alpha_arc.theta2 = angle_deg

        middle_deg = angle_deg / 2.0 if angle_deg > 0 else 8.0
        r_text = 0.245
        self.alpha_text.set_position((
            r_text * np.cos(np.deg2rad(middle_deg)),
            r_text * np.sin(np.deg2rad(middle_deg))
        ))

        n = max(2, int(1400 * alpha / MAX_ALPHA))
        xs = np.linspace(0, alpha, n)
        ys = np.sin(xs)
        self.sine_line.set_data(xs, ys)
        self.sine_dot.set_data([alpha], [y])
        self.vertical_marker.set_data([alpha, alpha], [y, 0])

        deg = np.degrees(alpha)
        alpha_2pi = alpha / (2 * np.pi)
        self.angle_text.set_text(
            rf"$\alpha={deg:.0f}^\circ$   |   $\alpha={alpha_2pi:.2f}\cdot 2\pi$"
        )

        self.fig.canvas.draw_idle()

    def show(self):
        plt.show()


if __name__ == "__main__":
    Zeigerdiagramm().show()
