"""
Cell site equipment catalog.
Each entry defines default 2D footprint (px) and 3D height (scene units).
Scene units: 1 unit = 1 meter (approximate). Canvas px ~ 20 px per meter.
"""

PIXELS_PER_METER = 20.0  # used for measurement conversion

EQUIPMENT_LIBRARY = {
    # ---------- TOWERS ----------
    "tower_lattice": {
        "label": "Lattice Tower",
        "category": "Tower",
        "shape": "rect",
        "w": 80, "h": 80, "height_3d": 60.0,
        "color_2d": "rgba(180, 180, 180, 0.55)",
        "color_3d": 0x9aa0a6,
    },
    "tower_monopole": {
        "label": "Monopole Tower",
        "category": "Tower",
        "shape": "circle",
        "w": 60, "h": 60, "height_3d": 45.0,
        "color_2d": "rgba(200, 200, 200, 0.55)",
        "color_3d": 0xb0b0b0,
    },
    "tower_guyed": {
        "label": "Guyed Tower",
        "category": "Tower",
        "shape": "rect",
        "w": 70, "h": 70, "height_3d": 70.0,
        "color_2d": "rgba(160, 160, 160, 0.55)",
        "color_3d": 0x8d9199,
    },
    "tower_rtwp": {
        "label": "Rooftop Pole (RTWP)",
        "category": "Tower",
        "shape": "circle",
        "w": 30, "h": 30, "height_3d": 6.0,
        "color_2d": "rgba(140, 160, 180, 0.55)",
        "color_3d": 0x6d7f8f,
    },

    # ---------- CABINETS / RACKS ----------
    "cabinet_outdoor": {
        "label": "Outdoor Cabinet",
        "category": "Cabinet",
        "shape": "rect",
        "w": 60, "h": 40, "height_3d": 2.0,
        "color_2d": "rgba(255, 200, 120, 0.55)",
        "color_3d": 0xE8A33D,
    },
    "cabinet_indoor": {
        "label": "Indoor Cabinet",
        "category": "Cabinet",
        "shape": "rect",
        "w": 55, "h": 35, "height_3d": 2.0,
        "color_2d": "rgba(255, 220, 160, 0.55)",
        "color_3d": 0xF2C27A,
    },
    "rack_19inch": {
        "label": "Equipment Rack (19\")",
        "category": "Rack",
        "shape": "rect",
        "w": 30, "h": 50, "height_3d": 2.2,
        "color_2d": "rgba(120, 180, 255, 0.55)",
        "color_3d": 0x4A90D9,
    },
    "rack_23inch": {
        "label": "Equipment Rack (23\")",
        "category": "Rack",
        "shape": "rect",
        "w": 36, "h": 55, "height_3d": 2.2,
        "color_2d": "rgba(100, 160, 240, 0.55)",
        "color_3d": 0x3A7BC8,
    },

    # ---------- CABLE LADDERS ----------
    "ladder_indoor": {
        "label": "Cable Ladder (Indoor)",
        "category": "Cable Ladder",
        "shape": "rect",
        "w": 120, "h": 12, "height_3d": 0.15,
        "color_2d": "rgba(120, 200, 120, 0.55)",
        "color_3d": 0x4CAF50,
    },
    "ladder_outdoor": {
        "label": "Cable Ladder (Outdoor)",
        "category": "Cable Ladder",
        "shape": "rect",
        "w": 120, "h": 12, "height_3d": 0.15,
        "color_2d": "rgba(90, 170, 90, 0.55)",
        "color_3d": 0x2E7D32,
    },

    # ---------- FOUNDATIONS ----------
    "basepad": {
        "label": "Basepad",
        "category": "Foundation",
        "shape": "rect",
        "w": 140, "h": 140, "height_3d": 0.3,
        "color_2d": "rgba(180, 180, 180, 0.35)",
        "color_3d": 0xBDBDBD,
    },
    "fence": {
        "label": "Site Fence",
        "category": "Foundation",
        "shape": "rect",
        "w": 260, "h": 260, "height_3d": 2.0,
        "color_2d": "rgba(150, 150, 150, 0.15)",
        "color_3d": 0xCFCFCF,
    },

    # ---------- POWER ----------
    "generator": {
        "label": "Generator",
        "category": "Power",
        "shape": "rect",
        "w": 70, "h": 35, "height_3d": 1.6,
        "color_2d": "rgba(255, 120, 120, 0.55)",
        "color_3d": 0xE05A5A,
    },
    "fuel_tank": {
        "label": "Fuel Tank",
        "category": "Power",
        "shape": "circle",
        "w": 50, "h": 50, "height_3d": 1.8,
        "color_2d": "rgba(255, 180, 80, 0.55)",
        "color_3d": 0xE69138,
    },
    "ats_panel": {
        "label": "ATS Panel",
        "category": "Power",
        "shape": "rect",
        "w": 30, "h": 20, "height_3d": 1.2,
        "color_2d": "rgba(255, 140, 60, 0.55)",
        "color_3d": 0xD2691E,
    },

    # ---------- ANTENNAS / RRU ----------
    "antenna_panel": {
        "label": "Panel Antenna",
        "category": "Antenna",
        "shape": "rect",
        "w": 10, "h": 30, "height_3d": 1.4,
        "color_2d": "rgba(160, 120, 220, 0.55)",
        "color_3d": 0x8E5DD8,
    },
    "rru": {
        "label": "RRU",
        "category": "Antenna",
        "shape": "rect",
        "w": 14, "h": 24, "height_3d": 0.6,
        "color_2d": "rgba(140, 100, 200, 0.55)",
        "color_3d": 0x6E44B8,
    },

    # ---------- MISC ----------
    "custom_box": {
        "label": "Custom Box",
        "category": "Custom",
        "shape": "rect",
        "w": 40, "h": 40, "height_3d": 1.0,
        "color_2d": "rgba(150, 150, 150, 0.45)",
        "color_3d": 0x888888,
    },
}


def get_equipment(key: str) -> dict:
    return EQUIPMENT_LIBRARY.get(key, EQUIPMENT_LIBRARY["custom_box"])


def px_to_m(px: float) -> float:
    return round(px / PIXELS_PER_METER, 2)


def px2_to_m2(w_px: float, h_px: float) -> float:
    return round((w_px / PIXELS_PER_METER) * (h_px / PIXELS_PER_METER), 3)
