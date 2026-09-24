"""
Cell site equipment catalog — v2 (realistic).
"""

from icons2d import get_icon_url

PIXELS_PER_METER = 20.0

EQUIPMENT_LIBRARY = {
    # ---------- TOWERS ----------
    "tower_lattice": {
        "label": "Lattice Tower", "category": "Tower", "shape": "rect",
        "w": 80, "h": 80, "height_3d": 60.0,
        "color_2d": "rgba(200,200,200,0.05)",
        "color_3d": 0xB0B4BA,
        "detail": "lattice",
    },
    "tower_monopole": {
        "label": "Monopole Tower", "category": "Tower", "shape": "circle",
        "w": 60, "h": 60, "height_3d": 45.0,
        "color_2d": "rgba(200,200,200,0.05)",
        "color_3d": 0xC5C8CC,
        "detail": "monopole",
    },
    "tower_guyed": {
        "label": "Guyed Tower", "category": "Tower", "shape": "rect",
        "w": 70, "h": 70, "height_3d": 70.0,
        "color_2d": "rgba(200,200,200,0.05)",
        "color_3d": 0xA8ACB2,
        "detail": "guyed",
    },
    "tower_rtwp": {
        "label": "Rooftop Pole (RTWP)", "category": "Tower", "shape": "circle",
        "w": 30, "h": 30, "height_3d": 6.0,
        "color_2d": "rgba(200,200,200,0.05)",
        "color_3d": 0x8899AA,
        "detail": "pole",
    },

    # ---------- CABINETS / RACKS ----------
    "cabinet_outdoor": {
        "label": "Outdoor Cabinet", "category": "Cabinet", "shape": "rect",
        "w": 60, "h": 40, "height_3d": 2.0,
        "color_2d": "rgba(240,201,122,0.05)",
        "color_3d": 0xD4A34A,
        "detail": "cabinet",
    },
    "cabinet_indoor": {
        "label": "Indoor Cabinet", "category": "Cabinet", "shape": "rect",
        "w": 55, "h": 35, "height_3d": 2.0,
        "color_2d": "rgba(245,221,166,0.05)",
        "color_3d": 0xE8C98A,
        "detail": "cabinet",
    },
    "rack_19inch": {
        "label": "Equipment Rack (19\")", "category": "Rack", "shape": "rect",
        "w": 30, "h": 50, "height_3d": 2.2,
        "color_2d": "rgba(120,180,255,0.05)",
        "color_3d": 0x2D3748,
        "detail": "rack",
    },
    "rack_23inch": {
        "label": "Equipment Rack (23\")", "category": "Rack", "shape": "rect",
        "w": 36, "h": 55, "height_3d": 2.2,
        "color_2d": "rgba(100,160,240,0.05)",
        "color_3d": 0x1F2937,
        "detail": "rack",
    },

    # ---------- CABLE LADDERS ----------
    "ladder_indoor": {
        "label": "Cable Ladder (Indoor)", "category": "Cable Ladder", "shape": "rect",
        "w": 120, "h": 12, "height_3d": 0.15,
        "color_2d": "rgba(127,183,126,0.05)",
        "color_3d": 0x9AA6A9,
        "detail": "ladder",
    },
    "ladder_outdoor": {
        "label": "Cable Ladder (Outdoor)", "category": "Cable Ladder", "shape": "rect",
        "w": 120, "h": 12, "height_3d": 0.15,
        "color_2d": "rgba(79,122,79,0.05)",
        "color_3d": 0x7A8B8D,
        "detail": "ladder",
    },

    # ---------- FOUNDATIONS ----------
    "basepad": {
        "label": "Basepad", "category": "Foundation", "shape": "rect",
        "w": 140, "h": 140, "height_3d": 0.3,
        "color_2d": "rgba(180,180,180,0.05)",
        "color_3d": 0xB8B8B8,
        "detail": "basepad",
    },
    "fence": {
        "label": "Site Fence", "category": "Foundation", "shape": "rect",
        "w": 260, "h": 260, "height_3d": 2.0,
        "color_2d": "rgba(150,150,150,0.05)",
        "color_3d": 0xCFCFCF,
        "detail": "fence",
    },

    # ---------- POWER ----------
    "generator": {
        "label": "Generator", "category": "Power", "shape": "rect",
        "w": 70, "h": 35, "height_3d": 1.6,
        "color_2d": "rgba(255,120,120,0.05)",
        "color_3d": 0xB03A2E,
        "detail": "generator",
    },
    "fuel_tank": {
        "label": "Fuel Tank", "category": "Power", "shape": "circle",
        "w": 50, "h": 50, "height_3d": 1.8,
        "color_2d": "rgba(255,180,80,0.05)",
        "color_3d": 0xD08A2C,
        "detail": "fuel_tank",
    },
    "ats_panel": {
        "label": "ATS Panel", "category": "Power", "shape": "rect",
        "w": 30, "h": 20, "height_3d": 1.2,
        "color_2d": "rgba(255,140,60,0.05)",
        "color_3d": 0xB35A15,
        "detail": "ats",
    },

    # ---------- ANTENNAS ----------
    "antenna_panel": {
        "label": "Panel Antenna", "category": "Antenna", "shape": "rect",
        "w": 10, "h": 30, "height_3d": 1.4,
        "color_2d": "rgba(160,120,220,0.05)",
        "color_3d": 0xE8E8E8,
        "detail": "antenna",
    },
    "rru": {
        "label": "RRU", "category": "Antenna", "shape": "rect",
        "w": 14, "h": 24, "height_3d": 0.6,
        "color_2d": "rgba(140,100,200,0.05)",
        "color_3d": 0x5B5B5B,
        "detail": "rru",
    },

    # ---------- MISC ----------
    "custom_box": {
        "label": "Custom Box", "category": "Custom", "shape": "rect",
        "w": 40, "h": 40, "height_3d": 1.0,
        "color_2d": "rgba(150,150,150,0.05)",
        "color_3d": 0x888888,
        "detail": "box",
    },
}


def get_equipment(key: str) -> dict:
    return EQUIPMENT_LIBRARY.get(key, EQUIPMENT_LIBRARY["custom_box"])


def get_icon_for(key: str) -> str:
    return get_icon_url(key)


def px_to_m(px: float) -> float:
    return round(px / PIXELS_PER_METER, 2)


def px2_to_m2(w_px: float, h_px: float) -> float:
    return round((w_px / PIXELS_PER_METER) * (h_px / PIXELS_PER_METER), 3)
