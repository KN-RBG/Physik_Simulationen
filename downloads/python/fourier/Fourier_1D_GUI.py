import tkinter as tk
from tkinter import ttk

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# =========================================================
# Eindimensionale Fourier-Demo für den Unterricht
# =========================================================
N = 1600
MAX_KOMPONENTEN = 50
MAX_EINZELKURVEN = 12


class Fourier1DDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Fourier-Transformation – 1D-Demo")
        self.root.geometry("1450x900")
        self.root.minsize(1100, 760)

        self.x = np.linspace(0, 2 * np.pi, N, endpoint=False)
        self.signal = None
        self.koeff = None
        self.freq = None
        self.rekonstruktion = None
        self.aktive_idx = np.array([], dtype=int)

        self._baue_gui()
        self.neu_berechnen()

    def _baue_gui(self):
        steuer = ttk.Frame(self.root, padding=10)
        steuer.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(steuer, text="Signal:").grid(row=0, column=0, sticky="w")
        self.signal_var = tk.StringVar(value="Sinus")
        self.signal_box = ttk.Combobox(
            steuer,
            textvariable=self.signal_var,
            values=["Sinus", "Rechteck", "Dreieck", "Sägezahn"],
            state="readonly",
            width=14,
        )
        self.signal_box.grid(row=0, column=1, padx=(6, 16), sticky="w")
        self.signal_box.bind("<<ComboboxSelected>>", lambda event: self.neu_berechnen())

        ttk.Label(steuer, text="Fourier-Komponenten:").grid(row=0, column=2, sticky="w")
        self.k_var = tk.IntVar(value=1)
        self.k_scale = ttk.Scale(
            steuer,
            from_=1,
            to=MAX_KOMPONENTEN,
            orient=tk.HORIZONTAL,
            length=320,
            command=self._slider_geaendert,
        )
        self.k_scale.set(1)
        self.k_scale.grid(row=0, column=3, padx=(8, 6), sticky="ew")
        self.k_label = ttk.Label(steuer, text="1", width=4)
        self.k_label.grid(row=0, column=4, sticky="w")

        ttk.Button(steuer, text="− 1", command=lambda: self._k_aendern(-1)).grid(
            row=0, column=5, padx=(12, 4)
        )
        ttk.Button(steuer, text="+ 1", command=lambda: self._k_aendern(1)).grid(
            row=0, column=6, padx=4
        )

        self.original_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            steuer, text="Originalsignal", variable=self.original_var, command=self.zeichne
        ).grid(row=1, column=0, columnspan=2, pady=(8, 0), sticky="w")

        self.summe_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            steuer, text="Fourier-Summe", variable=self.summe_var, command=self.zeichne
        ).grid(row=1, column=2, pady=(8, 0), sticky="w")

        self.einzel_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            steuer,
            text="Einzelne Komponenten",
            variable=self.einzel_var,
            command=self.zeichne,
        ).grid(row=1, column=3, pady=(8, 0), sticky="w")

        ttk.Label(steuer, text="Filter:").grid(row=2, column=0, pady=(10, 0), sticky="w")
        self.filter_var = tk.StringVar(value="Alle")
        self.filter_box = ttk.Combobox(
            steuer,
            textvariable=self.filter_var,
            values=["Alle", "Tiefpass", "Hochpass"],
            state="readonly",
            width=12,
        )
        self.filter_box.grid(row=2, column=1, pady=(10, 0), sticky="w")
        self.filter_box.bind("<<ComboboxSelected>>", lambda event: self._filter_geaendert())

        self.grenze_text = ttk.Label(steuer, text="Grenzfrequenz:")
        self.grenze_text.grid(row=2, column=2, pady=(10, 0), sticky="w")
        self.grenze_var = tk.IntVar(value=8)
        self.grenze_scale = ttk.Scale(
            steuer,
            from_=1,
            to=MAX_KOMPONENTEN,
            orient=tk.HORIZONTAL,
            length=260,
            command=self._grenze_geaendert,
        )
        self.grenze_scale.set(8)
        self.grenze_scale.grid(row=2, column=3, pady=(10, 0), padx=(8, 6), sticky="ew")
        self.grenze_label = ttk.Label(steuer, text="8", width=4)
        self.grenze_label.grid(row=2, column=4, pady=(10, 0), sticky="w")

        self.info_var = tk.StringVar()
        ttk.Label(steuer, textvariable=self.info_var).grid(
            row=2, column=5, columnspan=2, pady=(10, 0), sticky="e"
        )
        steuer.columnconfigure(3, weight=1)

        self.fig = Figure(figsize=(13.4, 7.6), dpi=100)
        gs = self.fig.add_gridspec(2, 2, height_ratios=[1.05, 0.95], hspace=0.34, wspace=0.25)
        self.ax_signal = self.fig.add_subplot(gs[0, 0])
        self.ax_spektrum = self.fig.add_subplot(gs[0, 1])
        self.ax_komponenten = self.fig.add_subplot(gs[1, :])
        self.fig.subplots_adjust(left=0.065, right=0.98, bottom=0.09, top=0.94)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        merksatz = (
            "Fourier-Idee: Ein kompliziertes periodisches Signal kann als Summe einfacher "
            "Sinus- und Kosinusschwingungen beschrieben werden. Niedrige Frequenzen bestimmen "
            "vor allem die grobe Form, hohe Frequenzen feine Details und scharfe Kanten."
        )
        ttk.Label(
            self.root, text=merksatz, padding=(12, 8), anchor="center", wraplength=1350
        ).pack(side=tk.BOTTOM, fill=tk.X)

        self._filter_bedienung_aktualisieren()

    def _signal_erzeugen(self):
        art = self.signal_var.get()
        if art == "Sinus":
            return np.sin(self.x)
        if art == "Rechteck":
            y = np.sign(np.sin(self.x))
            y[y == 0] = 1
            return y
        if art == "Dreieck":
            return (2 / np.pi) * np.arcsin(np.sin(self.x))
        if art == "Sägezahn":
            return 2 * ((self.x / (2 * np.pi)) - np.floor(0.5 + self.x / (2 * np.pi)))
        return np.sin(self.x)

    def neu_berechnen(self):
        self.signal = self._signal_erzeugen()
        self.koeff = np.fft.rfft(self.signal) / N
        self.freq = np.fft.rfftfreq(N, d=1 / N)
        self._rekonstruktion_berechnen()
        self.zeichne()

    def _slider_geaendert(self, wert):
        k = max(1, min(MAX_KOMPONENTEN, int(round(float(wert)))))
        self.k_var.set(k)
        self.k_label.config(text=str(k))
        if self.koeff is not None:
            self._rekonstruktion_berechnen()
            self.zeichne()

    def _k_aendern(self, delta):
        k = max(1, min(MAX_KOMPONENTEN, self.k_var.get() + delta))
        self.k_scale.set(k)
        self._slider_geaendert(k)

    def _grenze_geaendert(self, wert):
        g = max(1, min(MAX_KOMPONENTEN, int(round(float(wert)))))
        self.grenze_var.set(g)
        self.grenze_label.config(text=str(g))
        if self.koeff is not None and self.filter_var.get() != "Alle":
            self._rekonstruktion_berechnen()
            self.zeichne()

    def _filter_geaendert(self):
        self._filter_bedienung_aktualisieren()
        self._rekonstruktion_berechnen()
        self.zeichne()

    def _filter_bedienung_aktualisieren(self):
        status = "disabled" if self.filter_var.get() == "Alle" else "normal"
        self.grenze_scale.configure(state=status)

    def _relevante_harmonische(self):
        idx = np.arange(1, len(self.koeff))
        reihenfolge = np.argsort(np.abs(self.koeff[idx]))[::-1]
        return idx[reihenfolge]

    def _rekonstruktion_berechnen(self):
        k = self.k_var.get()
        relevante = self._relevante_harmonische()
        ausgewaehlt = relevante[:k]

        filterart = self.filter_var.get()
        grenze = self.grenze_var.get()
        if filterart == "Tiefpass":
            ausgewaehlt = ausgewaehlt[self.freq[ausgewaehlt] <= grenze]
        elif filterart == "Hochpass":
            ausgewaehlt = ausgewaehlt[self.freq[ausgewaehlt] >= grenze]

        self.aktive_idx = ausgewaehlt
        spektrum = np.zeros_like(self.koeff)
        spektrum[0] = self.koeff[0]
        spektrum[ausgewaehlt] = self.koeff[ausgewaehlt]
        self.rekonstruktion = np.fft.irfft(spektrum * N, n=N)

        fehler = np.sqrt(np.mean((self.signal - self.rekonstruktion) ** 2))
        self.info_var.set(
            f"aktive Komponenten: {len(ausgewaehlt)}   |   RMS-Abweichung: {fehler:.3f}"
        )

    def zeichne(self):
        if self.signal is None:
            return

        self.ax_signal.clear()
        self.ax_spektrum.clear()
        self.ax_komponenten.clear()
        art = self.signal_var.get()
        k = self.k_var.get()

        if self.original_var.get():
            self.ax_signal.plot(
                self.x, self.signal, color="gray", linestyle="--", linewidth=1.4,
                label="Originalsignal"
            )
        if self.summe_var.get():
            self.ax_signal.plot(
                self.x, self.rekonstruktion, color="tab:purple", linewidth=2.2,
                label="Fourier-Summe"
            )

        self.ax_signal.set_title(f"1. {art}: Original und Fourier-Näherung")
        self.ax_signal.set_xlabel("x")
        self.ax_signal.set_ylabel("y")
        self.ax_signal.set_xlim(0, 2 * np.pi)
        self.ax_signal.set_xticks(
            [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi],
            ["0", "π/2", "π", "3π/2", "2π"]
        )
        self.ax_signal.grid(True, alpha=0.25)
        self.ax_signal.legend(loc="best", fontsize=8)

        relevante = self._relevante_harmonische()
        n_show = min(40, len(relevante))
        idx_show = relevante[:n_show]
        idx_show = idx_show[np.argsort(self.freq[idx_show])]
        amp = 2 * np.abs(self.koeff)

        marker_bg, stems_bg, _ = self.ax_spektrum.stem(
            self.freq[idx_show], amp[idx_show], basefmt=" "
        )
        plt.setp(stems_bg, color="gray", alpha=0.2, linewidth=0.8)
        plt.setp(marker_bg, color="gray", alpha=0.2, markersize=3)

        if len(self.aktive_idx) > 0:
            idx_aktiv = self.aktive_idx[np.argsort(self.freq[self.aktive_idx])]
            marker_a, stems_a, _ = self.ax_spektrum.stem(
                self.freq[idx_aktiv], amp[idx_aktiv], basefmt=" "
            )
            plt.setp(stems_a, color="tab:purple", linewidth=1.8)
            plt.setp(marker_a, color="tab:purple", markersize=5)

        if self.filter_var.get() != "Alle":
            grenze = self.grenze_var.get()
            self.ax_spektrum.axvline(
                grenze, color="tab:red", linestyle="--", linewidth=1.4,
                label=f"Grenzfrequenz = {grenze}"
            )
            self.ax_spektrum.legend(loc="best", fontsize=8)

        self.ax_spektrum.set_title(
            f"2. Frequenzspektrum – {len(self.aktive_idx)} aktive Komponenten"
        )
        self.ax_spektrum.set_xlabel("Frequenz / Harmonische")
        self.ax_spektrum.set_ylabel("Amplitude")
        self.ax_spektrum.grid(True, alpha=0.25)

        if self.einzel_var.get() and len(self.aktive_idx) > 0:
            n_einzel = min(MAX_EINZELKURVEN, len(self.aktive_idx))
            for i, idx in enumerate(self.aktive_idx[:n_einzel], start=1):
                c = self.koeff[idx]
                f = self.freq[idx]
                beitrag = 2 * np.real(
                    c * np.exp(1j * 2 * np.pi * f * np.arange(N) / N)
                )
                self.ax_komponenten.plot(
                    self.x, beitrag, linewidth=1.0, alpha=0.8,
                    label=f"Komponente {i}: f={int(f)}"
                )

        if self.summe_var.get():
            self.ax_komponenten.plot(
                self.x, self.rekonstruktion, color="tab:purple", linewidth=2.4,
                label="Summe"
            )

        self.ax_komponenten.set_title("3. Einzelne Fourier-Komponenten und ihre Summe")
        self.ax_komponenten.set_xlabel("x")
        self.ax_komponenten.set_ylabel("Beitrag")
        self.ax_komponenten.set_xlim(0, 2 * np.pi)
        self.ax_komponenten.set_xticks(
            [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi],
            ["0", "π/2", "π", "3π/2", "2π"]
        )
        self.ax_komponenten.grid(True, alpha=0.25)
        if self.einzel_var.get() or self.summe_var.get():
            self.ax_komponenten.legend(loc="upper right", ncol=4, fontsize=7)

        if art == "Rechteck" and k >= 5:
            self.ax_signal.text(
                0.02, 0.04,
                "Hinweis: Das Überschwingen an den Sprungstellen ist das Gibbs-Phänomen.",
                transform=self.ax_signal.transAxes,
                fontsize=9,
                bbox=dict(boxstyle="round", alpha=0.12),
            )

        self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    app = Fourier1DDemo(root)
    root.mainloop()
