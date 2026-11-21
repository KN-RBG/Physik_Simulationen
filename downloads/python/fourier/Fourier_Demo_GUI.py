import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties


ANZAHL_PUNKTE = 2200
MAX_KOMPONENTEN = 250
INTERVALL_MS = 15
SCHRITTWEITE_ANIMATION = 16
MAX_SICHTBARE_KREISE = 40


# Bewusst getrennte Farben:
# Gesamtkurve oben links = violett, x(t) = blau, y(t) = grün.
FARBE_GESAMTKURVE = "tab:purple"
FARBE_X = "tab:blue"
FARBE_Y = "tab:green"
FARBE_AKTUELL = "tab:red"


def text_zu_punkten(text, size=1.0, n=ANZAHL_PUNKTE):
    text = text.strip()
    if not text:
        raise ValueError("Bitte ein Wort eingeben.")

    prop = FontProperties(family="DejaVu Sans")
    tp = TextPath((0, 0), text, size=size, prop=prop)
    polys = tp.to_polygons()
    if len(polys) == 0:
        raise ValueError("Aus diesem Text konnte keine Kontur erzeugt werden.")

    punkte = []
    for poly in polys:
        if len(poly) < 2:
            continue
        if not np.allclose(poly[0], poly[-1]):
            poly = np.vstack([poly, poly[0]])
        if punkte:
            p_start = np.asarray(punkte[-1])
            p_ziel = poly[0]
            punkte.extend(np.linspace(p_start, p_ziel, 15, endpoint=False).tolist())
        punkte.extend(poly.tolist())

    punkte = np.asarray(punkte, dtype=float)
    if len(punkte) < 2:
        raise ValueError("Die erzeugte Kontur enthält zu wenige Punkte.")

    punkte[:, 0] -= np.mean(punkte[:, 0])
    punkte[:, 1] -= np.mean(punkte[:, 1])

    diff = np.diff(punkte, axis=0)
    seglaengen = np.hypot(diff[:, 0], diff[:, 1])
    s = np.concatenate(([0.0], np.cumsum(seglaengen)))
    if s[-1] <= 0:
        raise ValueError("Die Kontur hat keine messbare Länge.")

    keep = np.concatenate(([True], np.diff(s) > 1e-12))
    s = s[keep]
    punkte = punkte[keep]

    s_neu = np.linspace(0, s[-1], n, endpoint=False)
    x_neu = np.interp(s_neu, s, punkte[:, 0])
    y_neu = np.interp(s_neu, s, punkte[:, 1])
    return x_neu + 1j * y_neu


class FourierDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Fourier-Transformation – interaktive Demo")
        self.root.geometry("1450x900")
        self.root.minsize(1100, 760)

        self.z = None
        self.koeff = None
        self.freq = None
        self.sort_idx = None
        self.idx_verwendet = None
        self.z_rek = None
        self.t = None
        self.frame = 0
        self.running = False
        self.after_id = None

        self._baue_gui()
        self.neu_berechnen()

    def _baue_gui(self):
        steuer = ttk.Frame(self.root, padding=10)
        steuer.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(steuer, text="Wort:").grid(row=0, column=0, sticky="w")
        self.wort_var = tk.StringVar(value="Physik")
        self.wort_entry = ttk.Entry(steuer, textvariable=self.wort_var, width=22)
        self.wort_entry.grid(row=0, column=1, padx=(6, 12), sticky="w")
        self.wort_entry.bind("<Return>", lambda event: self.neu_berechnen())

        ttk.Button(steuer, text="Neu berechnen", command=self.neu_berechnen).grid(
            row=0, column=2, padx=(0, 18)
        )

        ttk.Label(steuer, text="Fourier-Komponenten:").grid(row=0, column=3, sticky="w")
        self.k_var = tk.IntVar(value=25)
        self.k_scale = ttk.Scale(
            steuer,
            from_=1,
            to=MAX_KOMPONENTEN,
            orient=tk.HORIZONTAL,
            command=self._slider_geaendert,
            length=300,
        )
        self.k_scale.set(25)
        self.k_scale.grid(row=0, column=4, padx=(8, 6), sticky="ew")

        self.k_label = ttk.Label(steuer, text="25", width=5)
        self.k_label.grid(row=0, column=5, sticky="w")

        self.start_button = ttk.Button(
            steuer, text="Animation starten", command=self.toggle_animation
        )
        self.start_button.grid(row=0, column=6, padx=(18, 6))

        ttk.Button(steuer, text="Zurücksetzen", command=self.reset_animation).grid(
            row=0, column=7, padx=6
        )

        self.kreise_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            steuer,
            text="Epizykel anzeigen",
            variable=self.kreise_var,
            command=self.zeichne_frame,
        ).grid(row=1, column=0, columnspan=2, pady=(8, 0), sticky="w")

        self.ziel_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            steuer,
            text="Zielkontur anzeigen",
            variable=self.ziel_var,
            command=self.zeichne_frame,
        ).grid(row=1, column=2, columnspan=2, pady=(8, 0), sticky="w")

        self.info_var = tk.StringVar()
        ttk.Label(steuer, textvariable=self.info_var).grid(
            row=1, column=4, columnspan=4, pady=(8, 0), sticky="e"
        )
        steuer.columnconfigure(4, weight=1)

        self.fig = Figure(figsize=(13.4, 7.7), dpi=100)
        gs = self.fig.add_gridspec(
            2, 2, height_ratios=[1.15, 0.85], hspace=0.34, wspace=0.25
        )
        self.ax_kurve = self.fig.add_subplot(gs[0, 0])
        self.ax_spektrum = self.fig.add_subplot(gs[0, 1])
        self.ax_funktion = self.fig.add_subplot(gs[1, :])
        self.fig.subplots_adjust(left=0.065, right=0.98, bottom=0.08, top=0.94)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        merksatz = (
            "Fourier-Idee: Eine komplizierte Kurve lässt sich als Überlagerung vieler einfacher "
            "Schwingungen beschreiben. Radius = Amplitude, Drehgeschwindigkeit = Frequenz, "
            "Startwinkel = Phase. Die Funktionen x(t) und y(t) ergeben zusammen die gezeichnete Bahn."
        )
        ttk.Label(
            self.root,
            text=merksatz,
            padding=(12, 8),
            anchor="center",
            wraplength=1350,
        ).pack(side=tk.BOTTOM, fill=tk.X)

    def neu_berechnen(self):
        self._stop_animation()
        try:
            self.z = text_zu_punkten(self.wort_var.get(), n=ANZAHL_PUNKTE)
        except Exception as exc:
            messagebox.showerror("Fehler", str(exc))
            return

        n = len(self.z)
        self.koeff = np.fft.fft(self.z) / n
        self.freq = np.fft.fftfreq(n, d=1 / n)
        self.sort_idx = np.argsort(np.abs(self.koeff))[::-1]
        self.t = np.linspace(0, 1, n, endpoint=False)
        self.frame = 0
        self._rekonstruktion_berechnen()
        self.zeichne_frame()

    def _slider_geaendert(self, wert):
        k = max(1, min(MAX_KOMPONENTEN, int(round(float(wert)))))
        self.k_var.set(k)
        self.k_label.config(text=str(k))
        if self.koeff is not None:
            self._rekonstruktion_berechnen()
            self.frame = min(self.frame, len(self.z) - 1)
            self.zeichne_frame()

    def _rekonstruktion_berechnen(self):
        k = self.k_var.get()
        self.idx_verwendet = self.sort_idx[:k]
        koeff_v = self.koeff[self.idx_verwendet]
        freq_v = self.freq[self.idx_verwendet]
        e = np.exp(2j * np.pi * freq_v[:, None] * self.t[None, :])
        self.z_rek = np.sum(koeff_v[:, None] * e, axis=0)

        fehler = np.sqrt(np.mean(np.abs(self.z - self.z_rek) ** 2))
        groesse = max(np.ptp(self.z.real), np.ptp(self.z.imag), 1e-12)
        fehler_rel = 100 * fehler / groesse
        self.info_var.set(
            f"Komponenten: {k}   |   relativer RMS-Fehler: {fehler_rel:.1f} %"
        )

    def zeichne_frame(self):
        if self.z is None:
            return

        self.ax_kurve.clear()
        self.ax_spektrum.clear()
        self.ax_funktion.clear()

        k = self.k_var.get()
        wort = self.wort_var.get().strip()
        frame = max(0, min(self.frame, len(self.z) - 1))
        zeit = self.t[frame]

        # 1. Rekonstruktion und Epizykel
        if self.ziel_var.get():
            self.ax_kurve.plot(
                self.z.real,
                self.z.imag,
                linewidth=1.2,
                alpha=0.45,
                color="gray",
                label="Zielkontur",
            )

        if frame > 0:
            self.ax_kurve.plot(
                self.z_rek.real[:frame + 1],
                self.z_rek.imag[:frame + 1],
                linewidth=2.2,
                color=FARBE_GESAMTKURVE,
                label="rekonstruierte Gesamtkurve",
            )

        endpunkt = self._epizykel_zeichnen(frame)
        self.ax_kurve.plot(
            [endpunkt.real], [endpunkt.imag], "o",
            color=FARBE_AKTUELL, markersize=5, label="aktueller Punkt"
        )
        self.ax_kurve.set_aspect("equal", adjustable="box")
        self.ax_kurve.grid(True, alpha=0.25)
        self.ax_kurve.set_title(f'1. Rekonstruktion: "{wort}" mit {k} Fourier-Komponenten')
        self.ax_kurve.set_xlabel("x")
        self.ax_kurve.set_ylabel("y")

        rand = 0.8
        self.ax_kurve.set_xlim(np.min(self.z.real) - rand, np.max(self.z.real) + rand)
        self.ax_kurve.set_ylim(np.min(self.z.imag) - rand, np.max(self.z.imag) + rand)
        self.ax_kurve.legend(loc="best", fontsize=8)

        # 2. Frequenzspektrum
        betrag = np.abs(self.koeff)
        n_show = min(80, len(self.sort_idx))
        idx_show = self.sort_idx[:n_show]
        idx_show = idx_show[np.argsort(self.freq[idx_show])]
        markerline, stemlines, _ = self.ax_spektrum.stem(
            self.freq[idx_show], betrag[idx_show], basefmt=" "
        )
        plt.setp(stemlines, linewidth=0.8, alpha=0.18, color="gray")
        plt.setp(markerline, markersize=2, alpha=0.18, color="gray")

        idx_sel = self.idx_verwendet[np.argsort(self.freq[self.idx_verwendet])]
        marker_sel, stems_sel, _ = self.ax_spektrum.stem(
            self.freq[idx_sel], betrag[idx_sel], basefmt=" "
        )
        plt.setp(stems_sel, linewidth=1.8, alpha=0.9, color="tab:purple")
        plt.setp(marker_sel, markersize=5, color="tab:purple")
        self.ax_spektrum.set_title(f"2. Frequenzspektrum – {k} verwendete Komponenten")
        self.ax_spektrum.set_xlabel("Frequenzindex k")
        self.ax_spektrum.set_ylabel("Amplitude |cₖ|")
        self.ax_spektrum.grid(True, alpha=0.25)

        # 3. x(t) und y(t)
        self.ax_funktion.plot(
            self.t, self.z_rek.real, linewidth=1.7,
            color=FARBE_X, label="x(t) – Fourier-Rekonstruktion"
        )
        self.ax_funktion.plot(
            self.t, self.z_rek.imag, linewidth=1.7,
            color=FARBE_Y, label="y(t) – Fourier-Rekonstruktion"
        )

        if self.ziel_var.get():
            self.ax_funktion.plot(
                self.t, self.z.real, linewidth=0.8, alpha=0.3,
                linestyle="--", color="gray", label="x(t) Ziel"
            )
            self.ax_funktion.plot(
                self.t, self.z.imag, linewidth=0.8, alpha=0.3,
                linestyle=":", color="black", label="y(t) Ziel"
            )

        self.ax_funktion.axvline(
            zeit, linewidth=1.4, linestyle="--", color=FARBE_AKTUELL,
            label=f"aktueller Zeitpunkt t = {zeit:.3f}"
        )
        self.ax_funktion.scatter(
            [zeit], [self.z_rek.real[frame]], s=30, color=FARBE_X, zorder=4
        )
        self.ax_funktion.scatter(
            [zeit], [self.z_rek.imag[frame]], s=30, color=FARBE_Y, zorder=4
        )
        self.ax_funktion.set_title("3. Vollständige Fourier-Funktion: x(t) und y(t)")
        self.ax_funktion.set_xlabel("Parameter t")
        self.ax_funktion.set_ylabel("Funktionswert")
        self.ax_funktion.set_xlim(0, 1)
        self.ax_funktion.grid(True, alpha=0.25)
        self.ax_funktion.legend(loc="upper right", ncol=3, fontsize=8)

        self.canvas.draw_idle()

    def _epizykel_zeichnen(self, frame):
        zeit = self.t[frame]
        pos = 0.0 + 0.0j
        koeff_v = self.koeff[self.idx_verwendet]
        freq_v = self.freq[self.idx_verwendet]
        sichtbare = min(len(koeff_v), MAX_SICHTBARE_KREISE)

        for i, (c, f) in enumerate(zip(koeff_v, freq_v)):
            start = pos
            pos += c * np.exp(2j * np.pi * f * zeit)
            if self.kreise_var.get() and i < sichtbare:
                kreis = Circle(
                    (start.real, start.imag), abs(c), fill=False,
                    linewidth=0.8, alpha=0.45
                )
                self.ax_kurve.add_patch(kreis)
                self.ax_kurve.plot(
                    [start.real, pos.real], [start.imag, pos.imag],
                    linewidth=0.8, alpha=0.75
                )
        return pos

    def toggle_animation(self):
        if self.running:
            self._stop_animation()
        else:
            self.running = True
            self.start_button.config(text="Animation stoppen")
            self._animationsschritt()

    def _stop_animation(self):
        self.running = False
        self.start_button.config(text="Animation starten")
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def reset_animation(self):
        self._stop_animation()
        self.frame = 0
        self.zeichne_frame()

    def _animationsschritt(self):
        if not self.running:
            return
        self.frame += SCHRITTWEITE_ANIMATION
        if self.frame >= len(self.z):
            self.frame = 0
        self.zeichne_frame()
        self.after_id = self.root.after(INTERVALL_MS, self._animationsschritt)


if __name__ == "__main__":
    root = tk.Tk()
    app = FourierDemo(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app._stop_animation(), root.destroy()))
    root.mainloop()
