import math
import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle, FancyArrowPatch
import numpy as np

AREA_MIN, AREA_MAX = -5.0, 5.0
SOFTENING = 0.09
STEP = 0.035
MAX_STEPS = 4200
HIT_RADIUS = 0.18
SEEDS_PER_Q = 12
CHARGE_RADIUS = 0.20
SELECT_RADIUS = 0.34
PLATE_X_LEFT = -2.2
PLATE_X_RIGHT = 2.2
PLATE_Y_MIN = -3.6
PLATE_Y_MAX = 3.6
PLATE_COUNT = 31
PLATE_CLICK_TOLERANCE = 0.50
PLATE_HIT_TOLERANCE = 0.075


def electric_field(x, y, charges):
    ex = ey = 0.0
    for c in charges:
        dx, dy = x - c["x"], y - c["y"]
        r2 = dx * dx + dy * dy + SOFTENING * SOFTENING
        r = math.sqrt(r2)
        f = c["q"] / (r2 * r)
        ex += f * dx
        ey += f * dy
    return np.array([ex, ey], dtype=float)


def unit_field(x, y, charges, direction=1.0):
    e = electric_field(x, y, charges)
    n = np.linalg.norm(e)
    return np.array([0.0, 0.0]) if n < 1e-12 else direction * e / n


def rk4_step(x, y, charges, direction):
    p = np.array([x, y], dtype=float)
    k1 = unit_field(*p, charges, direction)
    k2 = unit_field(*(p + 0.5 * STEP * k1), charges, direction)
    k3 = unit_field(*(p + 0.5 * STEP * k2), charges, direction)
    k4 = unit_field(*(p + STEP * k3), charges, direction)
    return p + STEP * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0


def near_opposite_point_charge(x, y, point_charges, source_sign):
    return any(
        c["q"] * source_sign < 0
        and math.hypot(x - c["x"], y - c["y"]) <= HIT_RADIUS
        for c in point_charges
    )


def opposite_plate_hit(x0, y0, x1, y1, plates, source_sign):
    for plate in plates:
        if plate["q"] * source_sign >= 0:
            continue
        px = plate["x"]
        if not (PLATE_Y_MIN <= y1 <= PLATE_Y_MAX):
            continue
        crossed = (x0 - px) * (x1 - px) <= 0
        close = abs(x1 - px) <= PLATE_HIT_TOLERANCE
        if crossed or close:
            return px, min(PLATE_Y_MAX, max(PLATE_Y_MIN, y0))
    return None


def trace_from_seed(seed_x, seed_y, charges, direction, source_sign,
                    plates=None, point_charges=None, stop_points=None):
    plates = plates or []
    point_charges = point_charges or []
    stop_points = stop_points or []
    pts = [(seed_x, seed_y)]
    x, y = seed_x, seed_y

    for _ in range(MAX_STEPS):
        nx, ny = rk4_step(x, y, charges, direction)
        nx, ny = float(nx), float(ny)

        if len(pts) > 5:
            hit = opposite_plate_hit(x, y, nx, ny, plates, source_sign)
            if hit is not None:
                px, hy = hit
                pts[-1] = (x, hy)
                pts.append((px, hy))
                break

        x, y = nx, ny

        # Feldnullpunkte (z. B. zwischen zwei gleich großen gleichnamigen
        # Ladungen) dürfen numerisch nicht "durchlaufen" werden. Trifft eine
        # Feldlinie den kleinen Fangbereich um einen solchen Punkt, endet sie
        # exakt im Feldnullpunkt. So entsteht weder ein Knick noch eine
        # sichtbare Lücke zwischen zwei symmetrischen Separatrix-Hälften.
        hit_stop = None
        for sx, sy in stop_points:
            if math.hypot(x - sx, y - sy) <= 0.10:
                hit_stop = (float(sx), float(sy))
                break

        if hit_stop is not None:
            pts.append(hit_stop)
            break

        pts.append((x, y))

        if x <= AREA_MIN or x >= AREA_MAX or y <= AREA_MIN or y >= AREA_MAX:
            break
        if len(pts) > 8 and near_opposite_point_charge(x, y, point_charges, source_sign):
            break
        if np.linalg.norm(electric_field(x, y, charges)) < 1e-9:
            break

    return np.array(pts)


def reflect_line_at_axis(line, origin, axis_unit):
    """Spiegelt eine Feldlinie an der Achse durch origin mit Richtung axis_unit."""
    u = np.array(axis_unit, dtype=float)
    u = u / np.linalg.norm(u)
    v = np.array([-u[1], u[0]])
    o = np.array(origin, dtype=float)

    reflected = []
    for p in line:
        r = np.array(p, dtype=float) - o
        reflected.append(o + np.dot(r, u) * u - np.dot(r, v) * v)
    return np.array(reflected)


def build_symmetric_dipole_lines(charges):
    """Exakt symmetrische Darstellung für zwei gleich große Gegenladungen."""
    if len(charges) != 2:
        return None

    c1, c2 = charges
    if c1["q"] * c2["q"] >= 0:
        return None
    if not math.isclose(abs(c1["q"]), abs(c2["q"]), rel_tol=1e-9, abs_tol=1e-9):
        return None

    positive = c1 if c1["q"] > 0 else c2
    negative = c2 if c1["q"] > 0 else c1

    dx = negative["x"] - positive["x"]
    dy = negative["y"] - positive["y"]
    d = math.hypot(dx, dy)
    if d < 1e-9:
        return None

    u = np.array([dx / d, dy / d])
    v = np.array([-u[1], u[0]])
    n = max(8, int(SEEDS_PER_Q * abs(positive["q"])))

    # Für eine saubere Paarbildung eine gerade Linienzahl verwenden.
    if n % 2:
        n += 1

    lines = []
    for k in range(n // 2 + 1):
        a = 2 * math.pi * k / n
        seed = (
            np.array([positive["x"], positive["y"]])
            + 0.25 * math.cos(a) * u
            + 0.25 * math.sin(a) * v
        )

        line = trace_from_seed(
            float(seed[0]), float(seed[1]),
            charges, 1.0, 1,
            point_charges=charges,
        )
        if len(line) <= 5:
            continue

        lines.append((line, 1.0))

        # Die beiden Linien auf der Symmetrieachse werden nicht doppelt gezeichnet.
        if k not in (0, n // 2):
            mirrored = reflect_line_at_axis(
                line,
                (positive["x"], positive["y"]),
                u,
            )
            lines.append((mirrored, 1.0))

    return lines


def build_symmetric_equal_like_lines(charges):
    """Exakt symmetrische Feldlinien für zwei gleich große gleichnamige Ladungen."""
    if len(charges) != 2:
        return None

    c1, c2 = charges
    if c1["q"] * c2["q"] <= 0:
        return None
    if not math.isclose(abs(c1["q"]), abs(c2["q"]), rel_tol=1e-9, abs_tol=1e-9):
        return None

    p1 = np.array([c1["x"], c1["y"]], dtype=float)
    p2 = np.array([c2["x"], c2["y"]], dtype=float)
    delta = p2 - p1
    d = np.linalg.norm(delta)
    if d < 1e-9:
        return None

    u = delta / d
    v = np.array([-u[1], u[0]])
    midpoint = 0.5 * (p1 + p2)

    direction = 1.0 if c1["q"] > 0 else -1.0
    source_sign = 1 if c1["q"] > 0 else -1
    n = max(8, int(SEEDS_PER_Q * abs(c1["q"])))
    if n % 2:
        n += 1

    lines = []

    # Nur die obere Hälfte an der ersten Ladung berechnen.
    # Die untere Hälfte und die zweite Ladung entstehen exakt durch Spiegelung.
    first_charge_lines = []
    # Die beiden Startwinkel direkt auf der Verbindungslinie (0 und pi)
    # werden aus didaktischen Gründen ausgelassen. So erscheint keine
    # scheinbar besondere "Mittellinie" zum Feldnullpunkt.
    for k in range(1, n // 2):
        a = math.pi * k / (n // 2)
        seed = p1 + 0.25 * math.cos(a) * u + 0.25 * math.sin(a) * v

        line = trace_from_seed(
            float(seed[0]), float(seed[1]),
            charges, direction, source_sign,
            point_charges=charges,
            stop_points=[(float(midpoint[0]), float(midpoint[1]))],
        )
        if len(line) <= 5:
            continue

        first_charge_lines.append(line)
        lines.append((line, direction))

        # Spiegelung an der Verbindungslinie erzeugt die untere Hälfte.
        mirrored_axis = reflect_line_at_axis(line, p1, u)
        first_charge_lines.append(mirrored_axis)
        lines.append((mirrored_axis, direction))

    # Spiegelung an der Mittelsenkrechten erzeugt das Feld der zweiten Ladung.
    for line in first_charge_lines:
        mirrored_mid = reflect_line_at_axis(line, midpoint, v)
        lines.append((mirrored_mid, direction))

    return lines


def build_point_lines(charges):
    if not charges:
        return []

    symmetric_dipole = build_symmetric_dipole_lines(charges)
    if symmetric_dipole is not None:
        return symmetric_dipole

    symmetric_like = build_symmetric_equal_like_lines(charges)
    if symmetric_like is not None:
        return symmetric_like

    positives = [c for c in charges if c["q"] > 0]
    sources = positives if positives else [c for c in charges if c["q"] < 0]
    direction = 1.0 if positives else -1.0
    source_sign = 1 if positives else -1
    lines = []

    for c in sources:
        n = max(8, int(SEEDS_PER_Q * abs(c["q"])))
        for j in range(n):
            a = 2 * math.pi * j / n
            line = trace_from_seed(
                c["x"] + 0.25 * math.cos(a),
                c["y"] + 0.25 * math.sin(a),
                charges, direction, source_sign,
                point_charges=charges,
            )
            if len(line) > 5:
                lines.append((line, direction))
    return lines


def make_plate_charges(x, q_total):
    ys = np.linspace(PLATE_Y_MIN, PLATE_Y_MAX, PLATE_COUNT)
    q_each = q_total / PLATE_COUNT
    return [{"x": x, "y": float(y), "q": q_each} for y in ys]


def build_plate_system_lines(plates, point_charge=None):
    charges = []
    for plate in plates:
        charges.extend(make_plate_charges(plate["x"], plate["q"]))
    if point_charge is not None:
        charges.append(dict(point_charge))
    if not charges:
        return []

    has_positive = any(c["q"] > 0 for c in charges)
    source_sign = 1 if has_positive else -1
    direction = 1.0 if has_positive else -1.0
    point_targets = [point_charge] if point_charge is not None else []
    lines = []

    core = np.linspace(PLATE_Y_MIN + 0.25, PLATE_Y_MAX - 0.25, 17)
    edges = np.concatenate([
        np.linspace(PLATE_Y_MIN + 0.03, PLATE_Y_MIN + 0.40, 4),
        np.linspace(PLATE_Y_MAX - 0.40, PLATE_Y_MAX - 0.03, 4),
    ])
    seed_ys = np.unique(np.concatenate([core, edges]))

    for plate in plates:
        if plate["q"] * source_sign <= 0:
            continue

        repeats = max(1, int(abs(plate["q"])))
        offsets = np.linspace(-0.035, 0.035, repeats)

        # Beim Plattenkondensator starten die Feldlinien nur auf der
        # Innenseite einer geladenen Platte. Dadurch entstehen keine
        # unphysikalischen, über die ganze Außenfläche verteilten Linien.
        # Startpunkte nahe den Plattenenden erzeugen weiterhin die Randfelder.
        opposite_plates = [
            p for p in plates
            if p is not plate and p["q"] * plate["q"] < 0
        ]
        if len(plates) >= 2 and opposite_plates:
            target = min(opposite_plates, key=lambda p: abs(p["x"] - plate["x"]))
            sides = (1,) if target["x"] > plate["x"] else (-1,)
        else:
            # Einzelplatte bzw. kein entgegengesetzter Plattenpartner:
            # Feldlinien dürfen auf beiden Seiten starten.
            sides = (-1, 1)

        for y in seed_ys:
            for dy in offsets:
                sy = float(min(PLATE_Y_MAX - 0.02, max(PLATE_Y_MIN + 0.02, y + dy)))
                for side in sides:
                    line = trace_from_seed(
                        plate["x"] + side * 0.13, sy,
                        charges, direction, source_sign,
                        plates=plates, point_charges=point_targets,
                    )
                    if len(line) > 5:
                        lines.append((line, direction))

    if point_charge is not None and point_charge["q"] * source_sign > 0:
        n = max(8, int(SEEDS_PER_Q * abs(point_charge["q"])))
        for j in range(n):
            a = 2 * math.pi * j / n
            line = trace_from_seed(
                point_charge["x"] + 0.25 * math.cos(a),
                point_charge["y"] + 0.25 * math.sin(a),
                charges, direction, source_sign,
                plates=plates, point_charges=point_targets,
            )
            if len(line) > 5:
                lines.append((line, direction))
    return lines


class FieldLineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Elektrische Feldlinien")
        self.root.geometry("1140x790")

        self.charges = []
        self.cap_plates = [
            {"x": PLATE_X_LEFT, "q": 1},
            {"x": PLATE_X_RIGHT, "q": -1},
        ]
        self.single_plate = {"x": PLATE_X_LEFT, "q": 1}
        self.mixed_charge = {"x": 2.0, "y": 0.0, "q": -1}
        self.selected_index = None
        self.selected_kind = None
        self.selected_plate_index = None
        self.dragging = False
        self.syncing_controls = False
        self.field_lines_cache = []

        self.field_type = tk.StringVar(value="point")
        self.polarity = tk.IntVar(value=1)
        self.amount = tk.IntVar(value=1)
        self.show_lines = tk.BooleanVar(value=False)
        self.selection_text = tk.StringVar(value="Keine Ladung ausgewählt")
        self.info_text = tk.StringVar()

        self.polarity.trace_add("write", self.on_charge_settings_changed)
        self.amount.trace_add("write", self.on_charge_settings_changed)
        self._build_ui()
        self.on_field_type_changed()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        controls = ttk.Frame(main)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        ttk.Label(controls, text="Elektrische Felder", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))
        mode_box = ttk.LabelFrame(controls, text="Feldtyp", padding=8)
        mode_box.pack(fill=tk.X, pady=(0, 10))
        for text, value in [
            ("Punktladungen", "point"),
            ("Plattenkondensator", "capacitor"),
            ("Kondensatorplatte + Punktladung", "plate_point"),
        ]:
            ttk.Radiobutton(mode_box, text=text, variable=self.field_type, value=value,
                            command=self.on_field_type_changed).pack(anchor="w")

        ttk.Label(controls, textvariable=self.info_text, justify="left", wraplength=250).pack(anchor="w", pady=(0, 10))
        self.selection_box = ttk.LabelFrame(controls, text="Auswahl", padding=8)
        self.selection_box.pack(fill=tk.X, pady=5)
        ttk.Label(self.selection_box, textvariable=self.selection_text, justify="left").pack(anchor="w")

        self.polarity_box = ttk.LabelFrame(controls, text="Polarität", padding=8)
        self.polarity_box.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(self.polarity_box, text="positiv (+)", variable=self.polarity, value=1).pack(anchor="w")
        ttk.Radiobutton(self.polarity_box, text="negativ (−)", variable=self.polarity, value=-1).pack(anchor="w")

        self.amount_box = ttk.LabelFrame(controls, text="Ladungsmenge", padding=8)
        self.amount_box.pack(fill=tk.X, pady=5)
        for value, label in [(1, "Q"), (2, "2 · Q"), (3, "3 · Q")]:
            ttk.Radiobutton(self.amount_box, text=label, variable=self.amount, value=value).pack(anchor="w")

        ttk.Checkbutton(controls, text="Feldlinien anzeigen", variable=self.show_lines,
                        command=self.on_show_lines_changed).pack(anchor="w", pady=(16, 8))
        self.delete_selected_btn = ttk.Button(controls, text="Ausgewählte Ladung löschen", command=self.remove_selected)
        self.delete_selected_btn.pack(fill=tk.X, pady=4)
        self.delete_last_btn = ttk.Button(controls, text="Letzte Ladung entfernen", command=self.remove_last)
        self.delete_last_btn.pack(fill=tk.X, pady=4)
        self.clear_btn = ttk.Button(controls, text="Alle Ladungen löschen", command=self.clear_all)
        self.clear_btn.pack(fill=tk.X, pady=4)

        ttk.Separator(controls).pack(fill=tk.X, pady=14)
        ttk.Label(controls,
                  text="Feldlinien verlaufen von + nach −.\nAn Leiteroberflächen stehen sie senkrecht.\nBei endlichen Platten werden Randfelder sichtbar.",
                  justify="left").pack(anchor="w")

        plot_frame = ttk.Frame(main)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.fig, self.ax = plt.subplots(figsize=(7, 7))
        self.fig.subplots_adjust(left=0.03, right=0.97, bottom=0.03, top=0.97)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)

    def set_controls_from_q(self, q):
        self.syncing_controls = True
        self.polarity.set(1 if q > 0 else -1)
        self.amount.set(max(1, min(3, int(round(abs(q))))))
        self.syncing_controls = False

    def select_plate(self, index):
        self.selected_kind = "plate"
        self.selected_plate_index = index
        self.selected_index = None
        if self.field_type.get() == "capacitor":
            plate = self.cap_plates[index]
            name = "linke Platte" if index == 0 else "rechte Platte"
        else:
            plate = self.single_plate
            name = "Kondensatorplatte"
        self.selection_text.set(f"Ausgewählt: {name} ({self.charge_label(plate['q'])})")
        self.set_controls_from_q(plate["q"])

    def select_mixed_point(self):
        self.selected_kind = "mixed_point"
        self.selected_plate_index = None
        self.selection_text.set(f"Ausgewählt: Punktladung ({self.charge_label(self.mixed_charge['q'])})")
        self.set_controls_from_q(self.mixed_charge["q"])

    def select_point_charge(self, index):
        self.selected_index = index
        self.selected_kind = "point"
        self.selected_plate_index = None
        q = self.charges[index]["q"]
        self.selection_text.set(f"Ausgewählt: {self.charge_label(q)}")
        self.set_controls_from_q(q)

    def on_field_type_changed(self):
        self.dragging = False
        self.selected_index = None
        self.selected_kind = None
        self.selected_plate_index = None
        mode = self.field_type.get()
        if mode == "point":
            self.info_text.set("Freie Fläche anklicken: neue Ladung setzen. Ladung anklicken und ziehen: verschieben.")
            self.selection_text.set("Keine Ladung ausgewählt")
            self.set_delete_controls_enabled(True)
        elif mode == "capacitor":
            self.info_text.set("Direkt auf eine der beiden Platten klicken. Die markierte Platte kann anschließend auf +/− und Q, 2Q oder 3Q eingestellt werden.")
            self.select_plate(0)
            self.set_delete_controls_enabled(False)
        else:
            self.info_text.set("Platte oder Punktladung anklicken. Die Regler ändern immer das ausgewählte Objekt.")
            self.select_mixed_point()
            self.set_delete_controls_enabled(False)
        self.recompute_field_lines()
        self.redraw()

    def set_delete_controls_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.delete_selected_btn.configure(state=state)
        self.delete_last_btn.configure(state=state)
        self.clear_btn.configure(state=state)

    def recompute_field_lines(self):
        if not self.show_lines.get():
            self.field_lines_cache = []
            return
        mode = self.field_type.get()
        if mode == "point":
            self.field_lines_cache = build_point_lines(self.charges)
        elif mode == "capacitor":
            self.field_lines_cache = build_plate_system_lines(self.cap_plates)
        else:
            self.field_lines_cache = build_plate_system_lines([self.single_plate], self.mixed_charge)

    def on_show_lines_changed(self):
        self.recompute_field_lines()
        self.redraw()

    def find_charge_at(self, x, y):
        best, d0 = None, SELECT_RADIUS
        for i, c in enumerate(self.charges):
            d = math.hypot(x - c["x"], y - c["y"])
            if d <= d0:
                best, d0 = i, d
        return best

    def plate_at(self, x, y):
        if not (PLATE_Y_MIN - 0.35 <= y <= PLATE_Y_MAX + 0.35):
            return None
        mode = self.field_type.get()
        if mode == "capacitor":
            distances = [abs(x - p["x"]) for p in self.cap_plates]
            index = int(np.argmin(distances))
            return index if distances[index] <= PLATE_CLICK_TOLERANCE else None
        if mode == "plate_point" and abs(x - self.single_plate["x"]) <= PLATE_CLICK_TOLERANCE:
            return 0
        return None

    def on_charge_settings_changed(self, *_):
        if self.syncing_controls:
            return
        q = self.polarity.get() * self.amount.get()
        mode = self.field_type.get()
        if mode == "point" and self.selected_kind == "point" and self.selected_index is not None:
            self.charges[self.selected_index]["q"] = q
            self.selection_text.set(f"Ausgewählt: {self.charge_label(q)}")
        elif mode == "capacitor" and self.selected_kind == "plate" and self.selected_plate_index is not None:
            self.cap_plates[self.selected_plate_index]["q"] = q
            self.select_plate(self.selected_plate_index)
        elif mode == "plate_point" and self.selected_kind == "plate":
            self.single_plate["q"] = q
            self.select_plate(0)
        elif mode == "plate_point" and self.selected_kind == "mixed_point":
            self.mixed_charge["q"] = q
            self.select_mixed_point()
        else:
            return
        self.recompute_field_lines()
        self.redraw()

    def on_mouse_press(self, event):
        if event.button != 1 or event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        x, y = float(event.xdata), float(event.ydata)
        mode = self.field_type.get()

        if mode in ("capacitor", "plate_point"):
            p = self.plate_at(x, y)
            if p is not None:
                self.select_plate(p)
                self.redraw()
                return

        if mode == "plate_point":
            if math.hypot(x - self.mixed_charge["x"], y - self.mixed_charge["y"]) <= SELECT_RADIUS:
                self.select_mixed_point()
                self.dragging = True
                self.redraw()
            return

        if mode == "capacitor":
            return

        index = self.find_charge_at(x, y)
        if index is not None:
            self.select_point_charge(index)
            self.dragging = True
            self.redraw()
            return

        q = self.polarity.get() * self.amount.get()
        self.charges.append({"x": x, "y": y, "q": q})
        self.select_point_charge(len(self.charges) - 1)
        self.dragging = True
        self.recompute_field_lines()
        self.redraw()

    def on_mouse_move(self, event):
        if not self.dragging or event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        x = min(AREA_MAX - 0.05, max(AREA_MIN + 0.05, float(event.xdata)))
        y = min(AREA_MAX - 0.05, max(AREA_MIN + 0.05, float(event.ydata)))

        if self.field_type.get() == "plate_point" and self.selected_kind == "mixed_point":
            x = max(self.single_plate["x"] + 0.45, x)
            self.mixed_charge["x"], self.mixed_charge["y"] = x, y
            self.redraw()
            return

        if self.field_type.get() == "point" and self.selected_index is not None:
            for i, c in enumerate(self.charges):
                if i != self.selected_index and math.hypot(x - c["x"], y - c["y"]) < 2 * CHARGE_RADIUS:
                    return
            self.charges[self.selected_index]["x"] = x
            self.charges[self.selected_index]["y"] = y
            self.redraw()

    def on_mouse_release(self, event):
        if self.dragging:
            self.dragging = False
            self.recompute_field_lines()
            self.redraw()

    def remove_selected(self):
        if self.field_type.get() != "point" or self.selected_index is None:
            return
        self.charges.pop(self.selected_index)
        self.selected_index = None
        self.selected_kind = None
        self.selection_text.set("Keine Ladung ausgewählt")
        self.recompute_field_lines()
        self.redraw()

    def remove_last(self):
        if self.field_type.get() != "point" or not self.charges:
            return
        self.charges.pop()
        self.selected_index = None
        self.selected_kind = None
        self.selection_text.set("Keine Ladung ausgewählt")
        self.recompute_field_lines()
        self.redraw()

    def clear_all(self):
        if self.field_type.get() != "point":
            return
        self.charges.clear()
        self.selected_index = None
        self.selected_kind = None
        self.field_lines_cache = []
        self.selection_text.set("Keine Ladung ausgewählt")
        self.redraw()

    @staticmethod
    def charge_label(q):
        sign = "+" if q > 0 else "−"
        mag = abs(q)
        return f"{sign}Q" if mag == 1 else f"{sign}{mag:g}Q"

    def draw_charge(self, charge, selected=False):
        face = "#d62728" if charge["q"] > 0 else "#1f77b4"
        symbol = "+" if charge["q"] > 0 else "−"
        if selected:
            self.ax.add_patch(Circle((charge["x"], charge["y"]), CHARGE_RADIUS + 0.08,
                                     facecolor="none", edgecolor="black", linewidth=2.0, zorder=7))
        self.ax.add_patch(Circle((charge["x"], charge["y"]), CHARGE_RADIUS,
                                 facecolor=face, edgecolor="black", linewidth=1.0, zorder=8))
        self.ax.text(charge["x"], charge["y"], symbol, color="white", fontsize=15, fontweight="bold",
                     ha="center", va="center", zorder=9)
        self.ax.text(charge["x"], charge["y"] - 0.34, self.charge_label(charge["q"]),
                     fontsize=10, ha="center", va="top", zorder=9)

    def draw_plate(self, plate, selected=False):
        x, q = plate["x"], plate["q"]
        color = "#d62728" if q > 0 else "#1f77b4"
        if selected:
            self.ax.plot([x, x], [PLATE_Y_MIN - 0.10, PLATE_Y_MAX + 0.10], color="black",
                         linewidth=13, solid_capstyle="round", zorder=6)
            self.ax.plot([x, x], [PLATE_Y_MIN - 0.08, PLATE_Y_MAX + 0.08], color="white",
                         linewidth=10, solid_capstyle="round", zorder=6.5)
        self.ax.plot([x, x], [PLATE_Y_MIN, PLATE_Y_MAX], color=color, linewidth=7,
                     solid_capstyle="round", zorder=7)
        symbol = "+" if q > 0 else "−"
        for y in np.linspace(PLATE_Y_MIN + 0.35, PLATE_Y_MAX - 0.35, 7):
            self.ax.text(x, y, symbol, color="white", fontsize=11, fontweight="bold",
                         ha="center", va="center", zorder=8)
        self.ax.text(x, PLATE_Y_MAX + 0.28, self.charge_label(q), fontsize=10,
                     ha="center", va="bottom", zorder=9)

    def draw_arrow_on_line(self, line, direction):
        if len(line) < 15:
            return
        i = max(3, min(len(line) - 5, int(len(line) * 0.52)))
        p1, p2 = line[i - 2], line[i + 2]
        if direction < 0:
            p1, p2 = p2, p1
        self.ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=10,
                                          linewidth=1.0, color="black", zorder=4))

    def redraw(self):
        self.ax.clear()
        self.ax.set_xlim(AREA_MIN, AREA_MAX)
        self.ax.set_ylim(AREA_MIN, AREA_MAX)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.grid(False)
        for spine in self.ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1.2)
            spine.set_color("black")

        if self.show_lines.get():
            for line, direction in self.field_lines_cache:
                self.ax.plot(line[:, 0], line[:, 1], color="black", linewidth=0.9, zorder=2)
                self.draw_arrow_on_line(line, direction)

        mode = self.field_type.get()
        if mode == "point":
            for i, c in enumerate(self.charges):
                self.draw_charge(c, selected=(self.selected_kind == "point" and i == self.selected_index))
        elif mode == "capacitor":
            for i, plate in enumerate(self.cap_plates):
                self.draw_plate(plate, selected=(self.selected_kind == "plate" and i == self.selected_plate_index))
        else:
            self.draw_plate(self.single_plate, selected=(self.selected_kind == "plate"))
            self.draw_charge(self.mixed_charge, selected=(self.selected_kind == "mixed_point"))

        self.canvas.draw_idle()


def main():
    root = tk.Tk()
    FieldLineApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
