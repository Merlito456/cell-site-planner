"""
Cell site equipment catalog — v3 (Fabric primitives, no images).
"""

PIXELS_PER_METER = 20.0

EQUIPMENT_LIBRARY = {
    # ---------- TOWERS ----------
    "tower_lattice": {
        "label": "Lattice Tower", "category": "Tower", "shape": "rect",
        "w": 80, "h": 80, "height_3d": 60.0,
        "color_3d": 0xB0B4BA, "detail": "lattice",
    },
    "tower_monopole": {
        "label": "Monopole Tower", "category": "Tower", "shape": "circle",
        "w": 60, "h": 60, "height_3d": 45.0,
        "color_3d": 0xC5C8CC, "detail": "monopole",
    },
    "tower_guyed": {
        "label": "Guyed Tower", "category": "Tower", "shape": "rect",
        "w": 70, "h": 70, "height_3d": 70.0,
        "color_3d": 0xA8ACB2, "detail": "guyed",
    },
    "tower_rtwp": {
        "label": "Rooftop Pole (RTWP)", "category": "Tower", "shape": "circle",
        "w": 30, "h": 30, "height_3d": 6.0,
        "color_3d": 0x8899AA, "detail": "pole",
    },

    # ---------- CABINETS / RACKS ----------
    "cabinet_outdoor": {
        "label": "Outdoor Cabinet", "category": "Cabinet", "shape": "rect",
        "w": 60, "h": 40, "height_3d": 2.0,
        "color_3d": 0xD4A34A, "detail": "cabinet",
    },
    "cabinet_indoor": {
        "label": "Indoor Cabinet", "category": "Cabinet", "shape": "rect",
        "w": 55, "h": 35, "height_3d": 2.0,
        "color_3d": 0xE8C98A, "detail": "cabinet",
    },
    "rack_19inch": {
        "label": 'Equipment Rack (19")', "category": "Rack", "shape": "rect",
        "w": 30, "h": 50, "height_3d": 2.2,
        "color_3d": 0x2D3748, "detail": "rack",
    },
    "rack_23inch": {
        "label": 'Equipment Rack (23")', "category": "Rack", "shape": "rect",
        "w": 36, "h": 55, "height_3d": 2.2,
        "color_3d": 0x1F2937, "detail": "rack",
    },

    # ---------- CABLE LADDERS ----------
    "ladder_indoor": {
        "label": "Cable Ladder (Indoor)", "category": "Cable Ladder", "shape": "rect",
        "w": 120, "h": 12, "height_3d": 0.15,
        "color_3d": 0x9AA6A9, "detail": "ladder",
    },
    "ladder_outdoor": {
        "label": "Cable Ladder (Outdoor)", "category": "Cable Ladder", "shape": "rect",
        "w": 120, "h": 12, "height_3d": 0.15,
        "color_3d": 0x7A8B8D, "detail": "ladder",
    },

    # ---------- FOUNDATIONS ----------
    "basepad": {
        "label": "Basepad", "category": "Foundation", "shape": "rect",
        "w": 140, "h": 140, "height_3d": 0.3,
        "color_3d": 0xB8B8B8, "detail": "basepad",
    },
    "fence": {
        "label": "Site Fence", "category": "Foundation", "shape": "rect",
        "w": 260, "h": 260, "height_3d": 2.0,
        "color_3d": 0xCFCFCF, "detail": "fence",
    },

    # ---------- POWER ----------
    "generator": {
        "label": "Generator", "category": "Power", "shape": "rect",
        "w": 70, "h": 35, "height_3d": 1.6,
        "color_3d": 0xB03A2E, "detail": "generator",
    },
    "fuel_tank": {
        "label": "Fuel Tank", "category": "Power", "shape": "circle",
        "w": 50, "h": 50, "height_3d": 1.8,
        "color_3d": 0xD08A2C, "detail": "fuel_tank",
    },
    "ats_panel": {
        "label": "ATS Panel", "category": "Power", "shape": "rect",
        "w": 30, "h": 20, "height_3d": 1.2,
        "color_3d": 0xB35A15, "detail": "ats",
    },

    # ---------- ANTENNAS ----------
    "antenna_panel": {
        "label": "Panel Antenna", "category": "Antenna", "shape": "rect",
        "w": 10, "h": 30, "height_3d": 1.4,
        "color_3d": 0xE8E8E8, "detail": "antenna",
    },
    "rru": {
        "label": "RRU", "category": "Antenna", "shape": "rect",
        "w": 14, "h": 24, "height_3d": 0.6,
        "color_3d": 0x5B5B5B, "detail": "rru",
    },

    # ---------- MISC ----------
    "custom_box": {
        "label": "Custom Box", "category": "Custom", "shape": "rect",
        "w": 40, "h": 40, "height_3d": 1.0,
        "color_3d": 0x888888, "detail": "box",
    },
}


def get_equipment(key: str) -> dict:
    return EQUIPMENT_LIBRARY.get(key, EQUIPMENT_LIBRARY["custom_box"])


def px_to_m(px: float) -> float:
    return round(px / PIXELS_PER_METER, 2)


def px2_to_m2(w_px: float, h_px: float) -> float:
    return round((w_px / PIXELS_PER_METER) * (h_px / PIXELS_PER_METER), 3)


# ==================================================================
# Fabric primitive generator — replaces the SVG image approach
# ==================================================================
def fabric_group_objects(equip_key: str, w: float, h: float) -> list:
    """
    Return a list of Fabric.js primitive object dicts that draw a
    top-view symbol of the equipment at position (0,0) and size (w,h).

    Everything here is a plain Fabric primitive (rect, circle, line,
    text) — no `image` type, no async loading, no `src` round-trip.
    This is what eliminates the blinking.

    Coordinates are relative to the group's top-left; the caller is
    responsible for wrapping them in a Fabric group and setting the
    group's left/top.
    """
    cx, cy = w / 2, h / 2
    objs = []

    def rect(x, y, ww, hh, fill, stroke="#222222", sw=2, rx=0):
        objs.append({
            "type": "rect",
            "left": x, "top": y,
            "width": ww, "height": hh,
            "fill": fill, "stroke": stroke, "strokeWidth": sw,
            "rx": rx, "ry": rx,
            "selectable": False,
        })

    def circle(x, y, r, fill, stroke="#222222", sw=2):
        objs.append({
            "type": "circle",
            "left": x - r, "top": y - r,
            "radius": r,
            "fill": fill, "stroke": stroke, "strokeWidth": sw,
            "selectable": False,
        })

    def line(x1, y1, x2, y2, stroke="#333333", sw=1.5, dash=None):
        o = {
            "type": "line",
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "stroke": stroke, "strokeWidth": sw,
            "selectable": False,
            "originX": "left", "originY": "top",
        }
        if dash:
            o["strokeDashArray"] = dash
        objs.append(o)

    def text(x, y, s, size=10, fill="#222222", weight="normal"):
        objs.append({
            "type": "textbox",
            "left": x, "top": y,
            "width": w,
            "text": s,
            "fontSize": size,
            "fontFamily": "system-ui, sans-serif",
            "fontWeight": weight,
            "fill": fill,
            "textAlign": "center",
            "selectable": False,
            "editable": False,
        })

    d = EQUIPMENT_LIBRARY[equip_key].get("detail", "box")

    # ---------------- TOWERS ----------------
    if d == "lattice":
        rect(0, 0, w, h, "#e6e6e6", "#222222", 2)
        line(0, 0, w, h, "#333333", 1.5)
        line(w, 0, 0, h, "#333333", 1.5)
        line(0, cy, w, cy, "#333333", 1)
        line(cx, 0, cx, h, "#333333", 1)
        circle(cx, cy, min(w, h) * 0.18, "transparent", "#222222", 2)
        circle(cx, cy, min(w, h) * 0.06, "#444444", "#444444", 1)

    elif d == "monopole":
        circle(cx, cy, min(w, h) * 0.45, "#dcdcdc", "#222222", 2)
        circle(cx, cy, min(w, h) * 0.22, "#b8b8b8", "#333333", 2)
        circle(cx, cy, min(w, h) * 0.06, "#333333", "#333333", 1)
        circle(cx, cy, min(w, h) * 0.36, "transparent", "#555555", 1)

    elif d == "guyed":
        rect(w * 0.2, h * 0.2, w * 0.6, h * 0.6, "#e6e6e6", "#222222", 2)
        line(cx, cy, 0, 0, "#444444", 1.2)
        line(cx, cy, w, 0, "#444444", 1.2)
        line(cx, cy, 0, h, "#444444", 1.2)
        line(cx, cy, w, h, "#444444", 1.2)
        circle(cx, cy, min(w, h) * 0.09, "#444444", "#444444", 1)

    elif d == "pole":
        circle(cx, cy, min(w, h) * 0.42, "#e9e9e9", "#222222", 2)
        circle(cx, cy, min(w, h) * 0.12, "#333333", "#333333", 1)
        line(cx - w * 0.4, cy, cx + w * 0.4, cy, "#666666", 1, [3, 3])
        line(cx, cy - h * 0.4, cx, cy + h * 0.4, "#666666", 1, [3, 3])

    # ---------------- CABINETS ----------------
    elif d == "cabinet":
        body_fill = "#F0C97A" if "outdoor" in equip_key else "#F5DDA6"
        rect(w * 0.08, h * 0.15, w * 0.84, h * 0.7, body_fill, "#222222", 2, rx=3)
        rect(w * 0.12, h * 0.19, w * 0.76, h * 0.62, "transparent", "#555555", 1)
        line(cx, h * 0.19, cx, h * 0.81, "#444444", 1.2)
        circle(cx - w * 0.05, cy, 2, "#222222", "#222222", 1)
        circle(cx + w * 0.05, cy, 2, "#222222", "#222222", 1)
        for i in range(2):
            line(w * 0.16, h * 0.26 + i * h * 0.06,
                 w * 0.30, h * 0.26 + i * h * 0.06, "#666666", 1)
            line(w * 0.70, h * 0.26 + i * h * 0.06,
                 w * 0.84, h * 0.26 + i * h * 0.06, "#666666", 1)

    elif d == "rack":
        rect(w * 0.22, h * 0.1, w * 0.56, h * 0.8, "#4A5568", "#1a1a1a", 2, rx=2)
        rect(w * 0.26, h * 0.14, w * 0.48, h * 0.72, "#2D3748", "#000000", 1)
        for i in range(7):
            y = h * (0.20 + i * 0.08)
            line(w * 0.30, y, w * 0.70, y, "#7f8fa4", 1)
        circle(w * 0.34, h * 0.82, 2, "#4ade80", "#4ade80", 1)
        circle(w * 0.42, h * 0.82, 2, "#fbbf24", "#fbbf24", 1)

    # ---------------- CABLE LADDER ----------------
    elif d == "ladder":
        rail_fill = "#7FB77E" if "indoor" in equip_key else "#4F7A4F"
        rect(0, h * 0.35, w, h * 0.14, rail_fill, "#222222", 1.5)
        rect(0, h * 0.55, w, h * 0.14, rail_fill, "#222222", 1.5)
        n = max(4, int(w / 12))
        for i in range(1, n):
            x = (i / n) * w
            line(x, h * 0.35, x, h * 0.69, "#333333", 1.2)

    # ---------------- BASEPAD ----------------
    elif d == "basepad":
        rect(0, 0, w, h, "#d9d9d9", "#333333", 2)
        line(0, 0, w, 0, "#888888", 1, [3, 3])
        line(0, h, w, h, "#888888", 1, [3, 3])
        line(0, 0, 0, h, "#888888", 1, [3, 3])
        line(w, 0, w, h, "#888888", 1, [3, 3])
        line(0, cy, w, cy, "#999999", 0.8)
        line(cx, 0, cx, h, "#999999", 0.8)

    # ---------------- FENCE ----------------
    elif d == "fence":
        rect(0, 0, w, h, "transparent", "#222222", 2)
        # corner posts
        for (px_, py_) in [(0, 0), (w - 6, 0), (0, h - 6), (w - 6, h - 6)]:
            rect(px_, py_, 6, 6, "#333333", "#333333", 1)

    # ---------------- GENERATOR ----------------
    elif d == "generator":
        rect(w * 0.08, h * 0.18, w * 0.84, h * 0.64, "#C0392B", "#222222", 2, rx=4)
        rect(w * 0.12, h * 0.22, w * 0.76, h * 0.56, "#A93226", "#111111", 1)
        for xf in [0.20, 0.30, 0.70, 0.80]:
            line(w * xf, h * 0.22, w * xf, h * 0.78, "#6c1910", 1)
        circle(cx, cy, min(w, h) * 0.14, "transparent", "#ffffff", 1.5)

    # ---------------- FUEL TANK ----------------
    elif d == "fuel_tank":
        circle(cx, cy, min(w, h) * 0.45, "#E8A33D", "#222222", 2)
        circle(cx, cy, min(w, h) * 0.35, "#F0B45A", "#333333", 1)
        circle(cx, cy, min(w, h) * 0.23, "transparent", "#8a5a15", 1)
        circle(cx, cy, min(w, h) * 0.06, "#5a3d10", "#5a3d10", 1)

    # ---------------- ATS ----------------
    elif d == "ats":
        rect(w * 0.15, h * 0.25, w * 0.70, h * 0.50, "#D2691E", "#222222", 2, rx=2)
        rect(w * 0.20, h * 0.30, w * 0.60, h * 0.40, "#E67E22", "#111111", 1)
        circle(w * 0.35, cy, 4, "#ffffff", "#333333", 1)
        circle(w * 0.50, cy, 4, "transparent", "#ffffff", 1.5)
        circle(w * 0.65, cy, 4, "transparent", "#ffffff", 1.5)

    # ---------------- ANTENNA ----------------
    elif d == "antenna":
        rect(w * 0.38, h * 0.15, w * 0.24, h * 0.60, "#8E5DD8", "#222222", 1.5, rx=2)
        for i in range(6):
            y = h * (0.22 + i * 0.08)
            line(w * 0.42, y, w * 0.58, y, "#4a2880", 0.8)

    # ---------------- RRU ----------------
    elif d == "rru":
        rect(w * 0.30, h * 0.20, w * 0.40, h * 0.55, "#6E44B8", "#222222", 1.5, rx=2)
        rect(w * 0.35, h * 0.26, w * 0.30, h * 0.43, "#5a369c", "#111111", 1)
        circle(cx, h * 0.70, 2, "#4ade80", "#4ade80", 1)

    # ---------------- CUSTOM / FALLBACK ----------------
    else:
        rect(w * 0.1, h * 0.15, w * 0.8, h * 0.7, "#cfcfcf", "#333333", 2)

    return objs
