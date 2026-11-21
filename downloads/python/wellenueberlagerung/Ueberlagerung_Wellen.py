import tkinter as tk
import time
from tkinter import ttk, messagebox

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter


class WellenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Überlagerung sinusförmiger Wellen")
        # Fenster an die nutzbare Bildschirmgroesse anpassen.
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        win_w = min(1260, max(760, screen_w - 80))
        win_h = min(840, max(500, screen_h - 120))
        root.geometry(f"{win_w}x{win_h}")
        root.minsize(700, 450)

        # Eingabewerte als Strings, damit ein Dezimalkomma möglich ist.
        self.abstand = tk.StringVar(value="16,0")

        self.A1 = tk.StringVar(value="1,0")
        self.lambda1 = tk.StringVar(value="4,0")
        self.f1 = tk.StringVar(value="0,32")

        self.A2 = tk.StringVar(value="1,0")
        self.lambda2 = tk.StringVar(value="4,0")
        self.f2 = tk.StringVar(value="0,32")

        # +1: von links nach rechts, -1: von rechts nach links
        self.richtung1 = tk.IntVar(value=1)
        self.richtung2 = tk.IntVar(value=-1)

        # +1: +sin, -1: -sin
        self.vorzeichen1 = tk.IntVar(value=1)
        self.vorzeichen2 = tk.IntVar(value=1)

        self.zeige_welle1 = tk.BooleanVar(value=True)
        self.zeige_welle2 = tk.BooleanVar(value=True)
        self.zeige_summe = tk.BooleanVar(value=False)

        # Slider 0 ... 200 %
        self.fortschritt = tk.DoubleVar(value=0.0)

        self.t = 0.0
        self.t_basis = 1.0
        self.spielt = False
        self.letzter_zeitpunkt = None
        self.animation_job = None

        # -----------------------------
        # Linker Bedienbereich
        # -----------------------------
        # Scrollbarer Bedienbereich links (auch auf kleinen Laptops).
        left = ttk.Frame(root)
        left.pack(side=tk.LEFT, fill=tk.Y)

        controls_canvas = tk.Canvas(left, width=310, highlightthickness=0)
        controls_scroll = ttk.Scrollbar(
            left, orient=tk.VERTICAL, command=controls_canvas.yview
        )
        controls_canvas.configure(yscrollcommand=controls_scroll.set)
        controls_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        controls_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        controls = ttk.Frame(controls_canvas, padding=10)
        controls_window = controls_canvas.create_window(
            (0, 0), window=controls, anchor="nw"
        )

        def update_scroll_region(event=None):
            controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))

        def update_controls_width(event):
            controls_canvas.itemconfigure(controls_window, width=event.width)

        controls.bind("<Configure>", update_scroll_region)
        controls_canvas.bind("<Configure>", update_controls_width)

        def scroll_controls(event):
            delta = -1 if event.delta > 0 else 1
            if event.delta:
                controls_canvas.yview_scroll(delta, "units")

        # Rad nur im linken Bedienbereich nutzen; Plot bleibt unbeeinflusst.
        def bind_wheel(event):
            event.widget.bind_all("<MouseWheel>", scroll_controls)

        def unbind_wheel(event):
            event.widget.unbind_all("<MouseWheel>")

        left.bind("<Enter>", bind_wheel)
        left.bind("<Leave>", unbind_wheel)
        controls_canvas.bind("<Enter>", bind_wheel)
        controls_canvas.bind("<Leave>", unbind_wheel)

        ttk.Label(
            controls,
            text="Überlagerung von Wellen",
            font=("Arial", 16, "bold"),
        ).pack(pady=(0, 12))

        allgemein = ttk.LabelFrame(
            controls,
            text="Versuchsaufbau",
            padding=10,
        )
        allgemein.pack(fill=tk.X, pady=5)

        self.eingabefeld(
            allgemein,
            "Abstand der Enden",
            self.abstand,
            "m",
        )

        ttk.Label(
            allgemein,
            text="Der Abstand legt den dargestellten\nOrtsbereich von x = 0 bis x = L fest.",
        ).pack(anchor="w", pady=(6, 0))

        # Welle 1
        frame1 = ttk.LabelFrame(controls, text="Welle 1", padding=10)
        frame1.pack(fill=tk.X, pady=5)

        self.eingabefeld(frame1, "Amplitude A₁", self.A1, "m")
        self.eingabefeld(frame1, "Wellenlänge λ₁", self.lambda1, "m")
        self.eingabefeld(frame1, "Frequenz f₁", self.f1, "Hz")

        ttk.Label(frame1, text="Ausbreitung:").pack(anchor="w", pady=(8, 2))
        ttk.Radiobutton(
            frame1,
            text="von links nach rechts →",
            variable=self.richtung1,
            value=1,
            command=self.neustart,
        ).pack(anchor="w")
        ttk.Radiobutton(
            frame1,
            text="von rechts nach links ←",
            variable=self.richtung1,
            value=-1,
            command=self.neustart,
        ).pack(anchor="w")

        ttk.Label(frame1, text="Startform:").pack(anchor="w", pady=(8, 2))
        ttk.Radiobutton(
            frame1,
            text="+ sin",
            variable=self.vorzeichen1,
            value=1,
            command=self.zeichnen,
        ).pack(anchor="w")
        ttk.Radiobutton(
            frame1,
            text="− sin",
            variable=self.vorzeichen1,
            value=-1,
            command=self.zeichnen,
        ).pack(anchor="w")

        ttk.Checkbutton(
            frame1,
            text="Welle 1 anzeigen",
            variable=self.zeige_welle1,
            command=self.zeichnen,
        ).pack(anchor="w", pady=(8, 0))

        # Welle 2
        frame2 = ttk.LabelFrame(controls, text="Welle 2", padding=10)
        frame2.pack(fill=tk.X, pady=5)

        self.eingabefeld(frame2, "Amplitude A₂", self.A2, "m")
        self.eingabefeld(frame2, "Wellenlänge λ₂", self.lambda2, "m")
        self.eingabefeld(frame2, "Frequenz f₂", self.f2, "Hz")

        ttk.Label(frame2, text="Ausbreitung:").pack(anchor="w", pady=(8, 2))
        ttk.Radiobutton(
            frame2,
            text="von links nach rechts →",
            variable=self.richtung2,
            value=1,
            command=self.neustart,
        ).pack(anchor="w")
        ttk.Radiobutton(
            frame2,
            text="von rechts nach links ←",
            variable=self.richtung2,
            value=-1,
            command=self.neustart,
        ).pack(anchor="w")

        ttk.Label(frame2, text="Startform:").pack(anchor="w", pady=(8, 2))
        ttk.Radiobutton(
            frame2,
            text="+ sin",
            variable=self.vorzeichen2,
            value=1,
            command=self.zeichnen,
        ).pack(anchor="w")
        ttk.Radiobutton(
            frame2,
            text="− sin",
            variable=self.vorzeichen2,
            value=-1,
            command=self.zeichnen,
        ).pack(anchor="w")

        ttk.Checkbutton(
            frame2,
            text="Welle 2 anzeigen",
            variable=self.zeige_welle2,
            command=self.zeichnen,
        ).pack(anchor="w", pady=(8, 0))

        # Überlagerung
        sum_frame = ttk.LabelFrame(
            controls,
            text="Überlagerung",
            padding=10,
        )
        sum_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(
            sum_frame,
            text="Überlagerung y₁ + y₂ anzeigen",
            variable=self.zeige_summe,
            command=self.zeichnen,
        ).pack(anchor="w")

        ttk.Label(
            sum_frame,
            text="Die Summe wird nur dort gezeichnet,\nwo beide Wellen angekommen sind.",
        ).pack(anchor="w", pady=(6, 0))

        ttk.Button(
            controls,
            text="Werte übernehmen / neu starten",
            command=self.neustart,
        ).pack(fill=tk.X, pady=(10, 4))

        ttk.Label(
            controls,
            text=(
                "Zusammenhänge:\n"
                "ω = 2πf\n"
                "v = f·λ"
            ),
            justify=tk.LEFT,
        ).pack(anchor="w", pady=8)

        # -----------------------------
        # Rechter Bereich
        # -----------------------------
        right = ttk.Frame(root, padding=(0, 8, 10, 8))
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        plot_frame = ttk.Frame(right)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7.0, 4.5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # -----------------------------
        # Zeit-Schieberegler
        # -----------------------------
        slider_frame = ttk.LabelFrame(
            right,
            text="Wellenausbreitung",
            padding=10,
        )
        slider_frame.pack(fill=tk.X, pady=(8, 0))

        self.zeit_label = ttk.Label(
            slider_frame,
            text="t = 0,00 s   |   0 %",
            font=("Arial", 12, "bold"),
        )
        self.zeit_label.pack()

        self.slider = ttk.Scale(
            slider_frame,
            from_=0,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.fortschritt,
            command=self.slider_bewegt,
        )
        self.slider.pack(fill=tk.X, padx=5, pady=8)
        # Bei manueller Bedienung die Animation anhalten.
        self.slider.bind("<ButtonPress-1>", self.pause)
        self.slider.bind("<KeyPress>", self.pause)

        labels = ttk.Frame(slider_frame)
        labels.pack(fill=tk.X)
        ttk.Label(labels, text="0 %").pack(side=tk.LEFT)
        ttk.Label(labels, text="100 %").pack(side=tk.LEFT, expand=True)
        ttk.Label(labels, text="200 %").pack(side=tk.RIGHT)

        steuerung = ttk.Frame(slider_frame)
        steuerung.pack(pady=(8, 0))

        self.play_button = ttk.Button(
            steuerung,
            text="▶ Play",
            command=self.play_pause,
        )
        self.play_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            steuerung,
            text="Zurück zum Start",
            command=self.reset,
        ).pack(side=tk.LEFT, padx=5)

        self.neustart()

    @staticmethod
    def zahl_einlesen(variable):
        """Liest sowohl deutsches Dezimalkomma als auch Dezimalpunkt ein."""
        text = variable.get().strip().replace(" ", "").replace(",", ".")
        return float(text)

    @staticmethod
    def de_zahl(wert, stellen=2):
        """Formatiert eine Zahl mit deutschem Dezimalkomma."""
        return f"{wert:.{stellen}f}".replace(".", ",")

    @staticmethod
    def achsenformat(wert, position=None):
        """Matplotlib-Ticks mit Dezimalkomma und ohne unnötige Nullen."""
        if abs(wert) < 1e-12:
            wert = 0.0
        return f"{wert:g}".replace(".", ",")

    def eingabefeld(self, parent, text, variable, einheit):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        ttk.Label(frame, text=text).pack(side=tk.LEFT)
        ttk.Label(
            frame,
            text=einheit,
            width=4,
            anchor="w",
        ).pack(side=tk.RIGHT)

        entry = ttk.Entry(
            frame,
            textvariable=variable,
            width=10,
        )
        entry.pack(side=tk.RIGHT, padx=(6, 2))
        entry.bind("<Return>", lambda event: self.neustart())

    def get_parameter(self):
        try:
            L = self.zahl_einlesen(self.abstand)
            A1 = self.zahl_einlesen(self.A1)
            l1 = self.zahl_einlesen(self.lambda1)
            f1 = self.zahl_einlesen(self.f1)
            A2 = self.zahl_einlesen(self.A2)
            l2 = self.zahl_einlesen(self.lambda2)
            f2 = self.zahl_einlesen(self.f2)
        except ValueError as exc:
            raise ValueError(
                "Bitte gültige Zahlen eingeben, z. B. 1,5."
            ) from exc

        if L <= 0:
            raise ValueError("Der Abstand der beiden Enden muss größer als 0 sein.")
        if l1 <= 0 or l2 <= 0:
            raise ValueError("Die Wellenlänge muss größer als 0 sein.")
        if f1 <= 0 or f2 <= 0:
            raise ValueError("Die Frequenz muss größer als 0 sein.")

        return L, A1, l1, f1, A2, l2, f2

    def berechne_t_basis(self):
        """
        100 % entsprechen dem Zeitpunkt, an dem die langsamere
        der beiden Wellen den gesamten Abstand L durchlaufen hat.
        200 % entsprechen der doppelten Zeit.
        """
        L, A1, l1, f1, A2, l2, f2 = self.get_parameter()
        v1 = f1 * l1
        v2 = f2 * l2
        self.t_basis = L / min(v1, v2)

    def berechne_welle(
        self,
        x,
        A,
        wellenlaenge,
        frequenz,
        richtung,
        vorzeichen,
        L,
    ):
        k = 2 * np.pi / wellenlaenge
        omega = 2 * np.pi * frequenz
        v = frequenz * wellenlaenge

        y_phys = np.zeros_like(x)
        y_plot = np.full_like(x, np.nan, dtype=float)
        aktiv = np.zeros_like(x, dtype=bool)

        if self.t <= 0:
            return y_phys, y_plot, aktiv, v

        strecke = v * self.t

        if richtung == 1:
            aktiv = x <= strecke
            phase = k * x - omega * self.t
        else:
            s = L - x
            aktiv = s <= strecke
            phase = k * s - omega * self.t

        werte = vorzeichen * A * np.sin(phase)
        y_phys[aktiv] = werte[aktiv]
        y_plot[aktiv] = werte[aktiv]

        return y_phys, y_plot, aktiv, v

    def slider_bewegt(self, wert=None):
        try:
            prozent = self.fortschritt.get()
            self.t = (prozent / 100.0) * self.t_basis
            self.zeichnen()
        except (tk.TclError, ValueError):
            pass

    def zeichnen(self):
        try:
            L, A1, l1, f1, A2, l2, f2 = self.get_parameter()
            x = np.linspace(0, L, 2200)

            y1_phys, y1_plot, aktiv1, v1 = self.berechne_welle(
                x,
                A1,
                l1,
                f1,
                self.richtung1.get(),
                self.vorzeichen1.get(),
                L,
            )
            y2_phys, y2_plot, aktiv2, v2 = self.berechne_welle(
                x,
                A2,
                l2,
                f2,
                self.richtung2.get(),
                self.vorzeichen2.get(),
                L,
            )

            ueberlagerungsbereich = aktiv1 & aktiv2
            y_sum_plot = np.full_like(x, np.nan, dtype=float)
            y_sum_plot[ueberlagerungsbereich] = (
                y1_phys[ueberlagerungsbereich]
                + y2_phys[ueberlagerungsbereich]
            )

            self.ax.clear()

            if self.zeige_welle1.get():
                self.ax.plot(
                    x,
                    y1_plot,
                    linewidth=2,
                    label=(
                        "Welle 1   "
                        f"f={self.de_zahl(f1)} Hz, "
                        f"v={self.de_zahl(v1)} m/s"
                    ),
                )

            if self.zeige_welle2.get():
                self.ax.plot(
                    x,
                    y2_plot,
                    linewidth=2,
                    label=(
                        "Welle 2   "
                        f"f={self.de_zahl(f2)} Hz, "
                        f"v={self.de_zahl(v2)} m/s"
                    ),
                )

            if self.zeige_summe.get():
                self.ax.plot(
                    x,
                    y_sum_plot,
                    linewidth=3,
                    color="green",
                    label="Überlagerung",
                )

            max_amp = abs(A1) + abs(A2)
            if max_amp == 0:
                max_amp = 1

            self.ax.set_xlim(0, L)
            self.ax.set_ylim(-1.2 * max_amp, 1.2 * max_amp)

            self.ax.axhline(0, color="gray", linewidth=0.8)
            self.ax.axvline(0, color="gray", linewidth=0.8)
            self.ax.axvline(L, color="gray", linewidth=0.8)

            # Wellenfronten markieren
            if self.t > 0:
                front1 = v1 * self.t
                if self.richtung1.get() == -1:
                    front1 = L - front1
                if 0 <= front1 <= L:
                    self.ax.axvline(front1, linestyle=":", alpha=0.5)

                front2 = v2 * self.t
                if self.richtung2.get() == -1:
                    front2 = L - front2
                if 0 <= front2 <= L:
                    self.ax.axvline(front2, linestyle=":", alpha=0.5)

            self.ax.grid(True, alpha=0.3)

            # Achsenticks mit deutschem Dezimalkomma
            formatter = FuncFormatter(self.achsenformat)
            self.ax.xaxis.set_major_formatter(formatter)
            self.ax.yaxis.set_major_formatter(formatter)

            self.ax.set_xlabel("Ort x in m")
            self.ax.set_ylabel("Auslenkung y in m")
            self.ax.set_title(
                "Ausbreitung und Überlagerung – "
                f"t = {self.de_zahl(self.t)} s"
            )

            if (
                self.zeige_welle1.get()
                or self.zeige_welle2.get()
                or self.zeige_summe.get()
            ):
                self.ax.legend(loc="upper right")

            self.zeit_label.config(
                text=(
                    f"t = {self.de_zahl(self.t)} s   |   "
                    f"{self.fortschritt.get():.0f} %"
                )
            )

            self.fig.tight_layout()
            self.canvas.draw_idle()

        except (tk.TclError, ValueError) as e:
            messagebox.showerror("Ungültige Eingabe", str(e))

    def pause(self, event=None):
        """Hält die Animation an, ohne den Zeitregler zurückzusetzen."""
        self.spielt = False
        self.letzter_zeitpunkt = None
        if self.animation_job is not None:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.play_button.configure(text="▶ Play")

    def play_pause(self):
        """Startet oder pausiert die zeitkontinuierliche Ausbreitung."""
        if self.spielt:
            self.pause()
            return
        try:
            self.berechne_t_basis()
        except (tk.TclError, ValueError) as e:
            messagebox.showerror("Ungültige Eingabe", str(e))
            return
        if self.fortschritt.get() >= 200:
            self.fortschritt.set(0)
            self.slider_bewegt()
        self.spielt = True
        self.letzter_zeitpunkt = time.monotonic()
        self.play_button.configure(text="⏸ Pause")
        self.animation_job = self.root.after(33, self.animationsschritt)

    def animationsschritt(self):
        """Zeitfortschritt in Echtzeit; UI bleibt dank Tk-after bedienbar."""
        self.animation_job = None
        if not self.spielt:
            return
        jetzt = time.monotonic()
        dt = max(0.0, jetzt - self.letzter_zeitpunkt)
        self.letzter_zeitpunkt = jetzt
        # 100 % entsprechen t_basis; 200 % der doppelten Laufzeit.
        fortschritt = min(200.0, self.fortschritt.get() + 100.0 * dt / self.t_basis)
        self.fortschritt.set(fortschritt)
        self.slider_bewegt()
        if fortschritt >= 200:
            self.pause()
        else:
            self.animation_job = self.root.after(33, self.animationsschritt)

    def reset(self):
        self.pause()
        self.fortschritt.set(0)
        self.t = 0.0
        self.zeichnen()

    def neustart(self):
        self.pause()
        try:
            self.berechne_t_basis()
            self.fortschritt.set(0)
            self.t = 0.0
            self.zeichnen()
        except (tk.TclError, ValueError) as e:
            messagebox.showerror("Ungültige Eingabe", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = WellenApp(root)
    root.mainloop()
