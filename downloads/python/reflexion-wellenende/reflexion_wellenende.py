"""Reflexion einer sinusförmigen Welle am festen oder losen Ende.

Python 3, benötigt numpy und matplotlib.
Die Darstellung orientiert sich an 'AB Konstruktion von reflektierten Wellen'.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons, Slider

BLUE = '#2456df'
RED = '#e04444'
GREEN = '#258d55'
WALL = 8.0
C = 1.0  # Ausbreitungsgeschwindigkeit in willkürlichen Längeneinheiten / s


class Reflexion:
    def __init__(self):
        self.wavelength = 4.0
        self.tau = 0.0  # Zeit in Perioden; die Wellenfront erreicht das Ende bei tau=0.5
        self.playing = False
        self.speed = 1.0
        self.fixed = True
        self.waveform = 'Sinus'
        self.visible = [True, True, True, True]
        self._sync = False
        self.fig, self.ax = plt.subplots(figsize=(12.5, 7.0))
        self.fig.subplots_adjust(left=.075, right=.765, bottom=.35, top=.87)
        self.fig.suptitle('Reflexion einer Welle am Ende', fontsize=16)
        self.ax.set_xlim(0, 16)
        self.ax.set_ylim(-2.35, 2.35)
        self.ax.set_xlabel('Ort x (Ende bei x = 8)')
        self.ax.set_ylabel('Auslenkung s / A')
        self.ax.axhline(0, color='#333333', lw=1.2)
        self.ax.axvline(WALL, color='#333333', lw=2.0)
        self.ax.grid(alpha=.16)
        self.ax.text(.03, .95, 'Einlaufende Welle  →', color=BLUE, transform=self.ax.transAxes, va='top')
        self.ax.text(.98, .95, 'Virtuelle Fortsetzung  →', color=BLUE, transform=self.ax.transAxes, va='top', ha='right')

        self.x_left = np.linspace(0, WALL, 1100)
        self.x_right = np.linspace(WALL, 16, 1100)
        (self.incident,) = self.ax.plot([], [], color=BLUE, lw=2.0, label='Einlaufende Welle')
        (self.virtual,) = self.ax.plot([], [], color=BLUE, ls='--', lw=1.8, alpha=.8, label='Virtuelle Fortsetzung')
        (self.reflected,) = self.ax.plot([], [], color=RED, lw=2.0, label='Reflektierte Welle')
        (self.total,) = self.ax.plot([], [], color=GREEN, lw=2.8, label='Überlagerung')
        self.front = self.ax.axvline(0, ls=':', color=RED, lw=1.1, alpha=.6)
        self.info = self.ax.text(.02, .02, '', transform=self.ax.transAxes, va='bottom', fontsize=10)

        self.slider_t = Slider(self.fig.add_axes([.14, .16, .47, .025]),
                               'Zeit t / T', 0, 2, valinit=0, valstep=1/80)
        self.slider_l = Slider(self.fig.add_axes([.14, .105, .47, .025]),
                               'Wellenlänge λ', 2, 8, valinit=self.wavelength, valstep=.1)
        self.slider_v = Slider(self.fig.add_axes([.14, .05, .47, .025]),
                               'Tempo', .1, 3, valinit=1, valstep=.1)
        self.slider_t.on_changed(self.seek)
        self.slider_l.on_changed(self.change_wavelength)
        self.slider_v.on_changed(self.change_speed)

        self.button_play = Button(self.fig.add_axes([.08, .245, .12, .045]), 'Start')
        self.button_prev = Button(self.fig.add_axes([.22, .245, .13, .045]), '− T/8')
        self.button_next = Button(self.fig.add_axes([.37, .245, .13, .045]), '+ T/8')
        self.button_reset = Button(self.fig.add_axes([.52, .245, .13, .045]), 'Zurücksetzen')
        self.button_play.on_clicked(self.toggle)
        self.button_prev.on_clicked(lambda event: self.step(-1))
        self.button_next.on_clicked(lambda event: self.step(1))
        self.button_reset.on_clicked(self.reset)

        # Einheitliche, großzügig angeordnete Bedienelemente rechts.
        self.fig.text(.79, .87, 'Randbedingung', fontsize=11, weight='bold')
        self._changing_end = False
        self.end_check = CheckButtons(
            self.fig.add_axes([.79, .745, .20, .105]),
            ['Festes Ende', 'Loses Ende'], [True, False]
        )
        self.end_check.on_clicked(self.change_end)

        self.fig.text(.79, .71, 'Wellenform', fontsize=11, weight='bold')
        self._changing_waveform = False
        self.wave_choice = CheckButtons(
            self.fig.add_axes([.79, .585, .20, .105]),
            ['Sinus', 'Minus Sinus'], [True, False]
        )
        self.wave_choice.on_clicked(self.change_waveform)

        self.fig.text(.79, .55, 'Darstellung', fontsize=11, weight='bold')
        self.visibility = CheckButtons(
            self.fig.add_axes([.79, .33, .20, .20]),
            ['Einlaufende Welle', 'Virtuelle Welle',
             'Reflektierte Welle', 'Überlagerung'], self.visible
        )
        self.visibility.on_clicked(self.change_visibility)

        for widget in (self.end_check, self.wave_choice, self.visibility):
            widget.ax.set_facecolor('white')
            for spine in widget.ax.spines.values():
                spine.set_visible(False)
            widget.ax.tick_params(left=False, bottom=False,
                                  labelleft=False, labelbottom=False)
        for widget in (self.end_check, self.wave_choice, self.visibility):
            for rect in getattr(widget, 'rectangles', []):
                rect.set_edgecolor('#547a98')
                rect.set_linewidth(1.3)
        self.last_time = None
        self.timer = self.fig.canvas.new_timer(interval=35)
        self.timer.add_callback(self.tick)
        self.timer.start()
        self.draw()

    def period(self):
        return self.wavelength / C

    def wave(self, x, front):
        """Rechtslaufende Sinus- oder Minus-Sinuswelle mit begrenzter Front."""
        phase = 2 * np.pi * (x - front) / self.wavelength
        return -np.sin(phase) if self.waveform == 'Sinus' else np.sin(phase)

    def draw(self):
        # Die Front beginnt eine halbe Wellenlänge vor dem Ende.
        # Vor dem Auftreffen existieren weder virtuelle noch reflektierte Welle.
        front = WALL + self.wavelength * (self.tau - .5)
        xi, xv = self.x_left, self.x_right
        incoming_full = self.wave(xi, front)
        incoming = np.where(xi <= front + 1e-10, incoming_full, np.nan)

        # Die virtuelle Welle läuft nur rechts des Endes weiter, soweit
        # ihre Front bereits vorgedrungen wäre.
        virtual = np.where((front >= WALL) & (xv <= front + 1e-10),
                           self.wave(xv, front), np.nan)

        # Reflektierter Anteil: Spiegelbild der virtuellen Welle.
        # fest: Punktspiegelung; lose: Achsenspiegelung.
        reached = (front >= WALL) & (xi >= 2 * WALL - front - 1e-10)
        reflected_full = (-1 if self.fixed else 1) * self.wave(2 * WALL - xi, front)
        reflected = np.where(reached, reflected_full, np.nan)
        total = np.where(reached, incoming_full + reflected_full, np.nan)

        self.incident.set_data(xi, incoming)
        self.virtual.set_data(xv, virtual)
        self.reflected.set_data(xi, reflected)
        self.total.set_data(xi, total)
        for artist, visible in zip(
                (self.incident, self.virtual, self.reflected, self.total), self.visible):
            artist.set_visible(visible)
        reflection_front = max(0, 2 * WALL - front)
        self.front.set_xdata([reflection_front, reflection_front])
        self.front.set_visible(front > WALL and front < 2 * WALL and self.visible[2])
        kind = 'fest (Phasensprung π)' if self.fixed else 'lose (kein Phasensprung)'
        stage = 'Welle läuft zum Ende' if front < WALL else 'Reflexion und Überlagerung'
        self.info.set_text(
            f'{self.waveform}     Ende: {kind}     λ = {self.wavelength:.1f}     '
            f't = {self.tau:.3f} T     {stage}'
        )
        self.fig.canvas.draw_idle()

    def seek(self, value):
        if self._sync:
            return
        self.playing = False
        self.button_play.label.set_text('Start')
        self.tau = float(value)
        self.draw()

    def change_wavelength(self, value):
        self.wavelength = float(value)
        self.draw()

    def change_speed(self, value):
        self.speed = float(value)

    def change_end(self, label):
        if self._changing_end:
            return
        # Zwei Checkboxen, aber immer genau eine Auswahl aktiv.
        wanted_fixed = label == 'Festes Ende'
        self._changing_end = True
        try:
            desired = (wanted_fixed, not wanted_fixed)
            for index, (actual, target) in enumerate(
                    zip(self.end_check.get_status(), desired)):
                if actual != target:
                    self.end_check.set_active(index)
        finally:
            self._changing_end = False
        self.fixed = wanted_fixed
        self.draw()

    def change_waveform(self, label):
        if self._changing_waveform:
            return
        self._changing_waveform = True
        try:
            desired = (label == 'Sinus', label == 'Minus Sinus')
            for index, (actual, target) in enumerate(
                    zip(self.wave_choice.get_status(), desired)):
                if actual != target:
                    self.wave_choice.set_active(index)
        finally:
            self._changing_waveform = False
        self.waveform = label
        self.draw()

    def change_visibility(self, label):
        labels = ['Einlaufende Welle', 'Virtuelle Welle', 'Reflektierte Welle', 'Überlagerung']
        self.visible[labels.index(label)] = not self.visible[labels.index(label)]
        self.draw()

    def toggle(self, event):
        self.playing = not self.playing
        self.button_play.label.set_text('Pause' if self.playing else 'Start')
        self.last_time = None
        self.fig.canvas.draw_idle()

    def step(self, direction):
        self.playing = False
        self.button_play.label.set_text('Start')
        self.set_tau(np.clip(self.tau + direction / 8, 0, 2))

    def reset(self, event):
        self.playing = False
        self.button_play.label.set_text('Start')
        self.set_tau(0)

    def set_tau(self, value):
        self.tau = float(value)
        self._sync = True
        self.slider_t.set_val(self.tau)
        self._sync = False
        self.draw()

    def tick(self):
        import time
        now = time.monotonic()
        if self.playing and self.last_time is not None:
            dt = min(now - self.last_time, .1)
            next_tau = self.tau + dt * self.speed / self.period()
            if next_tau >= 2:
                next_tau = 2
                self.playing = False
                self.button_play.label.set_text('Start')
            self.set_tau(next_tau)
        self.last_time = now if self.playing else None
        return True


if __name__ == '__main__':
    app = Reflexion()
    plt.show()
