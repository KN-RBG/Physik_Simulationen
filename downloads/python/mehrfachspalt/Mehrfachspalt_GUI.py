import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


# =========================================================
# Hilfsfunktionen
# =========================================================

def komma_float(text):
    """Akzeptiert sowohl Dezimalkomma als auch Dezimalpunkt."""
    return float(text.strip().replace(",", "."))


def formatiere_deutsch(wert, nachkommastellen=2):
    return f"{wert:.{nachkommastellen}f}".replace(".", ",")


# =========================================================
# GUI
# =========================================================

class MehrfachspaltApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interferenz am Mehrfachspalt")
        self.root.geometry("1150x760")
        self.root.minsize(950, 650)

        self.erstelle_gui()
        self.zeichne_diagramm()

    def erstelle_gui(self):
        hauptframe = ttk.Frame(self.root, padding=10)
        hauptframe.pack(fill=tk.BOTH, expand=True)

        eingabe = ttk.LabelFrame(hauptframe, text="Einstellungen", padding=10)
        eingabe.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.anzahl_var = tk.StringVar(value="2")
        self.spaltbreite_var = tk.StringVar(value="0,05")
        self.spaltabstand_var = tk.StringVar(value="0,20")
        self.schirmabstand_var = tk.StringVar(value="2,0")
        self.wellenlaenge_var = tk.StringVar(value="650")
        self.schirm_von_var = tk.StringVar(value="-60")
        self.schirm_bis_var = tk.StringVar(value="60")
        self.einzelspalt_var = tk.BooleanVar(value=False)
        self.huellkurve_var = tk.BooleanVar(value=False)

        self.erzeuge_eingabezeile(
            eingabe, 0, "Anzahl der Spalte:", self.anzahl_var, ""
        )
        self.erzeuge_eingabezeile(
            eingabe, 1, "Spaltbreite b:", self.spaltbreite_var, "mm"
        )
        self.erzeuge_eingabezeile(
            eingabe, 2, "Spaltabstand g:", self.spaltabstand_var, "mm"
        )
        self.erzeuge_eingabezeile(
            eingabe, 3, "Abstand zum Schirm a:", self.schirmabstand_var, "m"
        )
        self.erzeuge_eingabezeile(
            eingabe, 4, "Wellenlänge λ:", self.wellenlaenge_var, "nm"
        )

        ttk.Separator(eingabe, orient=tk.HORIZONTAL).grid(
            row=5, column=0, columnspan=3, sticky="ew", pady=12
        )

        ttk.Label(eingabe, text="Bereich auf dem Schirm:").grid(
            row=6, column=0, columnspan=3, sticky="w", pady=(0, 4)
        )
        self.erzeuge_eingabezeile(
            eingabe, 7, "von:", self.schirm_von_var, "mm"
        )
        self.erzeuge_eingabezeile(
            eingabe, 8, "bis:", self.schirm_bis_var, "mm"
        )

        ttk.Separator(eingabe, orient=tk.HORIZONTAL).grid(
            row=9, column=0, columnspan=3, sticky="ew", pady=12
        )

        ttk.Checkbutton(
            eingabe,
            text="Einzelspalt berücksichtigen",
            variable=self.einzelspalt_var,
            command=self.zeichne_diagramm,
        ).grid(row=10, column=0, columnspan=3, sticky="w", pady=(0, 6))

        ttk.Checkbutton(
            eingabe,
            text="Einzelspalt-Hüllkurve anzeigen",
            variable=self.huellkurve_var,
            command=self.zeichne_diagramm,
        ).grid(row=11, column=0, columnspan=3, sticky="w", pady=(0, 12))

        ttk.Button(
            eingabe,
            text="Interferenzbild zeichnen",
            command=self.zeichne_diagramm,
        ).grid(row=12, column=0, columnspan=3, sticky="ew", pady=5)

        ttk.Button(
            eingabe,
            text="Standardwerte",
            command=self.standardwerte,
        ).grid(row=13, column=0, columnspan=3, sticky="ew", pady=5)

        for child in eingabe.winfo_children():
            if isinstance(child, ttk.Entry):
                child.bind("<Return>", lambda event: self.zeichne_diagramm())

        diagramm_frame = ttk.Frame(hauptframe)
        diagramm_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=diagramm_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, diagramm_frame)
        toolbar.update()

    def erzeuge_eingabezeile(self, parent, zeile, text, variable, einheit):
        ttk.Label(parent, text=text).grid(
            row=zeile, column=0, sticky="w", padx=(0, 8), pady=5
        )

        entry = ttk.Entry(parent, textvariable=variable, width=12)
        entry.grid(row=zeile, column=1, sticky="ew", pady=5)

        ttk.Label(parent, text=einheit).grid(
            row=zeile, column=2, sticky="w", padx=(6, 0), pady=5
        )

    def standardwerte(self):
        self.anzahl_var.set("2")
        self.spaltbreite_var.set("0,05")
        self.spaltabstand_var.set("0,20")
        self.schirmabstand_var.set("2,0")
        self.wellenlaenge_var.set("650")
        self.schirm_von_var.set("-60")
        self.schirm_bis_var.set("60")
        self.einzelspalt_var.set(False)
        self.huellkurve_var.set(False)
        self.zeichne_diagramm()

    # =====================================================
    # Berechnung und Darstellung
    # =====================================================

    def zeichne_diagramm(self):
        try:
            anzahl_spalte = int(self.anzahl_var.get().strip())
            spaltbreite_mm = komma_float(self.spaltbreite_var.get())
            spaltabstand_mm = komma_float(self.spaltabstand_var.get())
            schirmabstand_m = komma_float(self.schirmabstand_var.get())
            wellenlaenge_nm = komma_float(self.wellenlaenge_var.get())
            schirm_von_mm = komma_float(self.schirm_von_var.get())
            schirm_bis_mm = komma_float(self.schirm_bis_var.get())

            if anzahl_spalte < 1:
                raise ValueError("Die Anzahl der Spalte muss mindestens 1 sein.")
            if spaltbreite_mm <= 0:
                raise ValueError("Die Spaltbreite b muss größer als 0 sein.")
            if spaltabstand_mm <= 0:
                raise ValueError("Der Spaltabstand g muss größer als 0 sein.")
            if spaltbreite_mm > spaltabstand_mm:
                raise ValueError(
                    "Die Spaltbreite b darf nicht größer als der Spaltabstand g sein."
                )
            if schirmabstand_m <= 0:
                raise ValueError("Der Abstand zum Schirm a muss größer als 0 sein.")
            if wellenlaenge_nm <= 0:
                raise ValueError("Die Wellenlänge muss größer als 0 sein.")
            if schirm_von_mm >= schirm_bis_mm:
                raise ValueError(
                    "Beim Schirmbereich muss der Wert 'von' kleiner als 'bis' sein."
                )

        except ValueError as fehler:
            messagebox.showerror(
                "Ungültige Eingabe",
                f"Bitte überprüfe die Eingaben.\n\n{fehler}",
            )
            return

        # Umrechnung in SI-Einheiten
        wellenlaenge = wellenlaenge_nm * 1e-9
        spaltbreite = spaltbreite_mm * 1e-3
        spaltabstand = spaltabstand_mm * 1e-3
        schirm_von_m = schirm_von_mm * 1e-3
        schirm_bis_m = schirm_bis_mm * 1e-3

        # Frei wählbarer Bereich auf dem Schirm
        x = np.linspace(schirm_von_m, schirm_bis_m, 5000)
        theta = np.arctan(x / schirmabstand_m)

        # Mehrfachspalt-Interferenz
        alpha = np.pi * spaltabstand * np.sin(theta) / wellenlaenge

        zaehler = np.sin(anzahl_spalte * alpha)
        nenner = np.sin(alpha)

        interferenz = np.empty_like(alpha)
        kleine_werte = np.abs(nenner) < 1e-12

        interferenz[~kleine_werte] = (
            zaehler[~kleine_werte] / nenner[~kleine_werte]
        ) ** 2
        interferenz[kleine_werte] = anzahl_spalte ** 2

        interferenz_norm = interferenz / (anzahl_spalte ** 2)

        # Einzelspalt-Beugung / Hüllkurve
        beta = np.pi * spaltbreite * np.sin(theta) / wellenlaenge
        einzelspalt = np.sinc(beta / np.pi) ** 2

        if self.einzelspalt_var.get():
            intensitaet = interferenz_norm * einzelspalt
        else:
            intensitaet = interferenz_norm

        maximum = np.max(intensitaet)
        if maximum > 0:
            intensitaet = intensitaet / maximum

        # Diagramm
        self.ax.clear()
        self.ax.plot(
            x * 1000,
            intensitaet,
            linewidth=1.5,
            label="Interferenzbild",
        )

        if self.huellkurve_var.get():
            self.ax.plot(
                x * 1000,
                einzelspalt,
                linewidth=2.0,
                color="tab:red",
                label="Einzelspalt-Hüllkurve",
            )
            self.ax.legend(loc="upper right")

        einzelspalt_text = (
            "mit Einzelspalt-Beugung"
            if self.einzelspalt_var.get()
            else "ohne Einzelspalt-Beugung"
        )

        self.ax.set_title(
            f"Interferenzbild eines {anzahl_spalte}-fach-Spalts\n"
            f"λ = {formatiere_deutsch(wellenlaenge_nm, 0)} nm, "
            f"a = {formatiere_deutsch(schirmabstand_m, 2)} m, "
            f"b = {formatiere_deutsch(spaltbreite_mm, 3)} mm, "
            f"g = {formatiere_deutsch(spaltabstand_mm, 3)} mm\n"
            f"{einzelspalt_text}"
        )
        self.ax.set_xlabel("Ort auf dem Schirm x in mm")
        self.ax.set_ylabel("relative Intensität")
        self.ax.set_xlim(schirm_von_mm, schirm_bis_mm)
        self.ax.set_ylim(0, 1.05)
        self.ax.grid(True)

        self.figure.tight_layout()
        self.canvas.draw_idle()


def main():
    root = tk.Tk()
    MehrfachspaltApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
