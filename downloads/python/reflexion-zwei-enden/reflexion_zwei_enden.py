"""Reflexion an zwei Enden – Entdeckermodus (Python-Testversion 3).

Gedämpfte Wellengleichung mit glatter verteilter Anregung, modale Lösung.
Bei jedem Parameterwechsel wird der neue eingeschwungene Zustand gezeigt;
Die Eigenmoden werden bei passenden Wellenlängen grün markiert.
Benötigt: numpy, matplotlib.
"""
import time
from collections import deque

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons, RadioButtons, Slider, TextBox

C = 1.0
NMODES = 35
DAMPING = .045          # gamma = DAMPING*pi*c/L
TARGET_AMPLITUDE = 3.0  # maximale Amplitude bei jeder Eigenfrequenz
BLUE = "#2464c5"
GREEN = "#228b62"
INK = "#27394b"


class Simulation:
    def __init__(self):
        self.L = 8.0
        self.lam = 16.0
        self.case = "fest–fest"
        self.show_trails = True
        self.playing = True
        self.t = 0.0
        self.last_clock = None
        self._internal = False
        self.trails = deque(maxlen=9)
        self.last_trail_t = -1e20
        self.fig = plt.figure(figsize=(13.5, 8.2))
        self.fig.suptitle("Reflexion an zwei Enden – Eigenschwingungen entdecken", fontsize=15)
        self.ax = self.fig.add_axes([.075, .40, .66, .48])
        self.ax.set_xlabel("Ort x")
        self.ax.set_ylabel("Auslenkung (relative Einheiten)")
        self.ax.axhline(0, color=INK, lw=1)
        self.ax.grid(alpha=.14)
        self.wave, = self.ax.plot([], [], lw=2.8, color=BLUE)
        self.trail_lines = [self.ax.plot([], [], color=BLUE, lw=1.2,
                                        alpha=.07+.055*i)[0] for i in range(9)]
        self.left_end = self.ax.axvline(0, color=INK, lw=2.3)
        self.right_end = self.ax.axvline(self.L, color=INK, lw=2.3)
        self.left_label = self.ax.text(0, 3.55, "", ha="center")
        self.right_label = self.ax.text(self.L, 3.55, "", ha="center")
        self.status = self.fig.text(.075, .335, "", fontsize=10)
        self.eigen_hint = self.fig.text(.075, .295, "Hinweis: Grünes Wellenbild und Amplitude 3: Eigenschwingung erreicht.", fontsize=10, color=GREEN)

        self.fig.text(.77, .86, "Randbedingungen", fontsize=11, weight="bold")
        self.radio = RadioButtons(self.fig.add_axes([.765, .66, .22, .19]),
                                  ("fest–fest", "lose–lose", "fest–lose"))
        self.radio.on_clicked(self.change_case)
        self.radio.ax.set_facecolor("white")
        for spine in self.radio.ax.spines.values():
            spine.set_visible(False)
        self.fig.text(.77, .62, "Beobachtung", fontsize=11, weight="bold")
        self.checks = CheckButtons(self.fig.add_axes([.765, .56, .22, .06]),
                                   ["Nachleuchten"], [True])
        self.checks.on_clicked(self.change_check)
        self.checks.ax.set_facecolor("white")
        for spine in self.checks.ax.spines.values():
            spine.set_visible(False)

        self.play_button = Button(self.fig.add_axes([.075, .205, .105, .043]), "Pause")
        self.reset_button = Button(self.fig.add_axes([.195, .205, .12, .043]), "Neu starten")
        self.play_button.on_clicked(self.toggle)
        self.reset_button.on_clicked(self.reset)

        self.lambda_slider = Slider(self.fig.add_axes([.17, .165, .46, .027]),
                                    "Wellenlänge λ", 1.0, 48, valinit=self.lam,
                                    valstep=.01)
        self.length_slider = Slider(self.fig.add_axes([.17, .107, .46, .027]),
                                    "Länge l", 2, 12, valinit=self.L, valstep=.05)
        self.speed_slider = Slider(self.fig.add_axes([.17, .049, .46, .027]),
                                   "Tempo", .25, 12, valinit=3, valstep=.25)
        # Direkte Eingabe neben den Reglern, auch mit Dezimalkomma.
        self.lambda_input = TextBox(self.fig.add_axes([.685, .158, .065, .039]),
                                    "", initial=f"{self.lam:.2f}")
        self.length_input = TextBox(self.fig.add_axes([.685, .100, .065, .039]),
                                    "", initial=f"{self.L:.2f}")
        self.fig.text(.77, .465, "Direkte Eingabe: Werte für l und λ\nrechts neben dem Regler eingeben\nund mit Enter bestätigen.", fontsize=10, va="top")
        self.lambda_input.on_submit(self.enter_lambda)
        self.length_input.on_submit(self.enter_length)
        self.lambda_slider.on_changed(self.change_lambda)
        self.length_slider.on_changed(self.change_length)
        self.speed_slider.on_changed(self.change_speed)
        self.rate = 3.0
        self.fig.text(.77, .26, "Blau: übrige Wellenbilder\n"
                              "Grün: Eigenschwingung\n"
                              "Blass: frühere Wellenbilder\n\n"
                              "Bei Parameteränderung wird\n"
                              "der eingeschwungene Zustand\n"
                              "direkt angezeigt.", fontsize=9.5, va="top")
        self.recompute(settled=True)
        self.timer = self.fig.canvas.new_timer(interval=40)
        self.timer.add_callback(self.tick)
        self.timer.start()

    def eigen_lambda(self, n):
        return (4*self.L/(2*n-1) if self.case == "fest–lose"
                else 2*self.L/n)

    def closest(self):
        target = 2*self.L/self.lam
        n = max(1, round((target+1)/2)) if self.case == "fest–lose" \
            else max(1, round(target))
        return n, self.eigen_lambda(n)

    def recompute(self, settled=True):
        """Modale Antwort auf eine räumlich glatte, idealisierte Anregung.
        Die Modenkräfte werden frequenzabhängig gewichtet, sodass die
        Resonanzmaxima der verschiedenen Eigenmoden ähnlich groß sind.
        Einschwinganteil mit u(x,0)=u_t(x,0)=0.
        """
        L = self.L
        self.x = np.linspace(0, L, 500)
        n = np.arange(1, NMODES+1, dtype=float)
        k = ((n-.5) if self.case == "fest–lose" else n)*np.pi/L
        self.phi = (np.cos(k[:, None]*self.x[None, :])
                    if self.case == "lose–lose" else
                    np.sin(k[:, None]*self.x[None, :]))
        self.omega = 2*np.pi*C/self.lam
        self.gamma = DAMPING*np.pi*C/L
        omega_n = C*k
        self.omega_d = np.sqrt(np.maximum(omega_n**2-self.gamma**2, 1e-12))
        # Glatte räumliche Anregung ohne Punktkraft/Knick. Für die
        # didaktische Vergleichbarkeit wird jeweils die zur aktuellen
        # Frequenz nächstliegende Eigenmode mit ungefähr gleicher
        # Resonanzamplitude angeregt. Andere Moden tragen schwächer bei.
        closest_index = int(np.argmin(abs(omega_n-self.omega)))
        omega_ref = omega_n[closest_index]
        width = .42*np.pi*C/L
        weights = np.exp(-.5*((omega_n-omega_ref)/width)**2)
        force = TARGET_AMPLITUDE*2*self.gamma*omega_ref*weights
        self.Q = force/(omega_n**2-self.omega**2+2j*self.gamma*self.omega)
        # Für jede Eigenmode wird die Anregung so kalibriert, dass
        # die maximale Amplitudenhülle bei Resonanz genau 3 beträgt.
        # Auch zwischen Resonanzen bleibt dieser Faktor erhalten.
        omega_e = omega_n[closest_index]
        reference_Q = force/(omega_n**2-omega_e**2+2j*self.gamma*omega_e)
        reference_peak = np.max(np.abs(reference_Q @ self.phi))
        if reference_peak > 0:
            self.Q *= TARGET_AMPLITUDE/reference_peak
        self.settled_profile = self.Q @ self.phi
        self.A = -self.Q.real
        self.B = (self.omega*self.Q.imag+self.gamma*self.A)/self.omega_d
        self.t = (7/self.gamma if settled else 0.0)
        self.trails.clear()
        self.last_trail_t = -1e20
        self.draw()

    def displacement(self, t):
        # Stationäre erzwungene Antwort plus gedämpfte Einschwinganteile.
        harmonic = np.real(self.Q*np.exp(1j*self.omega*t))
        transient = np.exp(-self.gamma*t)*(
            self.A*np.cos(self.omega_d*t)+self.B*np.sin(self.omega_d*t))
        return np.real(self.settled_profile*np.exp(1j*self.omega*t)) + transient @ self.phi

    def draw(self):
        y = self.displacement(self.t)
        L = self.L
        self.ax.set_xlim(-.045*L, 1.045*L)
        self.ax.set_ylim(-4.2, 4.2) # festes Maß: Resonanz verstärkt sichtbar
        self.wave.set_data(self.x, y)
        n, lam_n = self.closest()
        eigenmode = abs(self.lam-lam_n)/lam_n < .002
        self.wave.set_color(GREEN if eigenmode else BLUE)
        for line in self.trail_lines:
            line.set_color(GREEN if eigenmode else BLUE)
        self.right_end.set_xdata([L, L])
        self.left_label.set_position((0, 3.55))
        self.right_label.set_position((L, 3.55))
        self.left_label.set_text("lose" if self.case == "lose–lose" else "fest")
        self.right_label.set_text("fest" if self.case == "fest–fest" else "lose")

        # Eine Spur pro ungefähr 1/12 Periode; alte Spuren verblassen.
        if self.t-self.last_trail_t >= self.lam/(12*C):
            self.trails.append(y.copy())
            self.last_trail_t = self.t
        traces = list(self.trails)
        for i, line in enumerate(self.trail_lines):
            if self.show_trails and i < len(traces):
                line.set_data(self.x, traces[i])
                line.set_visible(True)
            else:
                line.set_visible(False)

        self.status.set_text(f"l = {L:.2f} m     λ = {self.lam:.2f} m     "
                             f"f = {C/self.lam:.4f} Hz     (c = {C:.1f} m/s)")
        self.fig.canvas.draw_idle()

    def change_case(self, value):
        self.case = value
        self.recompute(settled=True)

    def change_check(self, label):
        self.show_trails = not self.show_trails
        self.draw()

    def change_lambda(self, value):
        if self._internal:
            return
        self.lam = float(value)
        self._internal = True
        self.lambda_input.eventson = False
        self.lambda_input.set_val(f"{self.lam:.2f}")
        self.lambda_input.eventson = True
        self._internal = False
        self.recompute(settled=True)

    def change_length(self, value):
        if self._internal:
            return
        self.L = float(value)
        self._internal = True
        self.length_input.eventson = False
        self.length_input.set_val(f"{self.L:.2f}")
        self.length_input.eventson = True
        self._internal = False
        self.recompute(settled=True)

    def enter_lambda(self, text):
        self.enter_number(text, "lambda")

    def enter_length(self, text):
        self.enter_number(text, "length")

    def enter_number(self, text, which):
        if self._internal:
            return
        slider = self.lambda_slider if which == "lambda" else self.length_slider
        field = self.lambda_input if which == "lambda" else self.length_input
        try:
            number = float(text.strip().replace(",", "."))
            if not np.isfinite(number) or not slider.valmin <= number <= slider.valmax:
                raise ValueError("Wert außerhalb des Reglerbereichs")
        except ValueError:
            self._internal = True
            field.set_val(f"{slider.val:.2f}")
            self._internal = False
            return
        # Der Slider löst die Neuberechnung und die Synchronisierung aus.
        slider.set_val(number)

    def change_speed(self, value):
        self.rate = float(value)

    def toggle(self, event):
        self.playing = not self.playing
        self.play_button.label.set_text("Pause" if self.playing else "Start")
        self.last_clock = None

    def reset(self, event):
        self.recompute(settled=True)

    def tick(self):
        now = time.monotonic()
        if self.playing and self.last_clock is not None:
            self.t += min(.1, now-self.last_clock)*self.rate
            self.draw()
        self.last_clock = now if self.playing else None
        return True


if __name__ == "__main__":
    app = Simulation()
    plt.show()
