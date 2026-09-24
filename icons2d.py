"""
Top-view SVG icons for 2D floor plan symbols.
Uses base64 data URLs — immune to '#' fragment issues with hex colors.
"""

import base64


def _svg(body: str, w: int = 100, h: int = 100) -> str:
    """
    Wrap an SVG body in a proper <svg> root with explicit width/height,
    then base64-encode it as a data URL.
    Base64 avoids the '#' character problem that silently truncates
    percent-encoded SVGs.
    """
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f'{body}</svg>'
    )
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


# ---------- TOWERS ----------
LATTICE = _svg("""
<rect x="5" y="5" width="90" height="90" fill="#e6e6e6" stroke="#222" stroke-width="2"/>
<line x1="5" y1="5" x2="95" y2="95" stroke="#333" stroke-width="1.5"/>
<line x1="95" y1="5" x2="5" y2="95" stroke="#333" stroke-width="1.5"/>
<line x1="5" y1="50" x2="95" y2="50" stroke="#333" stroke-width="1"/>
<line x1="50" y1="5" x2="50" y2="95" stroke="#333" stroke-width="1"/>
<circle cx="50" cy="50" r="18" fill="none" stroke="#222" stroke-width="2"/>
<circle cx="50" cy="50" r="6" fill="#444"/>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">LATTICE</text>
""")

MONOPOLE = _svg("""
<circle cx="50" cy="50" r="42" fill="#dcdcdc" stroke="#222" stroke-width="2"/>
<circle cx="50" cy="50" r="20" fill="#b8b8b8" stroke="#333" stroke-width="2"/>
<circle cx="50" cy="50" r="6" fill="#333"/>
<circle cx="50" cy="50" r="34" fill="none" stroke="#555" stroke-width="1" stroke-dasharray="3,3"/>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">MONOPOLE</text>
""")

GUYED = _svg("""
<rect x="20" y="20" width="60" height="60" fill="#e6e6e6" stroke="#222" stroke-width="2"/>
<line x1="50" y1="50" x2="5" y2="5" stroke="#444" stroke-width="1.2"/>
<line x1="50" y1="50" x2="95" y2="5" stroke="#444" stroke-width="1.2"/>
<line x1="50" y1="50" x2="5" y2="95" stroke="#444" stroke-width="1.2"/>
<line x1="50" y1="50" x2="95" y2="95" stroke="#444" stroke-width="1.2"/>
<circle cx="50" cy="50" r="8" fill="#444"/>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">GUYED</text>
""")

RTWP = _svg("""
<circle cx="50" cy="50" r="34" fill="#e9e9e9" stroke="#222" stroke-width="2"/>
<circle cx="50" cy="50" r="10" fill="#333"/>
<line x1="16" y1="50" x2="84" y2="50" stroke="#666" stroke-width="1" stroke-dasharray="2,3"/>
<line x1="50" y1="16" x2="50" y2="84" stroke="#666" stroke-width="1" stroke-dasharray="2,3"/>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">RTWP</text>
""")


# ---------- CABINETS / RACKS ----------
def _cabinet(fill: str, label: str) -> str:
    return _svg(f"""
    <rect x="8" y="15" width="84" height="70" fill="{fill}" stroke="#222" stroke-width="2" rx="2"/>
    <rect x="12" y="19" width="76" height="62" fill="none" stroke="#555" stroke-width="1"/>
    <line x1="50" y1="19" x2="50" y2="81" stroke="#444" stroke-width="1.2"/>
    <circle cx="46" cy="50" r="2" fill="#222"/>
    <circle cx="54" cy="50" r="2" fill="#222"/>
    <line x1="16" y1="26" x2="30" y2="26" stroke="#666" stroke-width="1"/>
    <line x1="16" y1="32" x2="30" y2="32" stroke="#666" stroke-width="1"/>
    <line x1="70" y1="26" x2="84" y2="26" stroke="#666" stroke-width="1"/>
    <line x1="70" y1="32" x2="84" y2="32" stroke="#666" stroke-width="1"/>
    <text x="50" y="98" font-size="8" text-anchor="middle" fill="#222">{label}</text>
    """)


CABINET_OUT = _cabinet("#F0C97A", "CAB-OUT")
CABINET_IN = _cabinet("#F5DDA6", "CAB-IN")


def _rack(label: str) -> str:
    return _svg(f"""
    <rect x="22" y="10" width="56" height="80" fill="#4A5568" stroke="#1a1a1a" stroke-width="2" rx="2"/>
    <rect x="26" y="14" width="48" height="72" fill="#2D3748" stroke="#000" stroke-width="1"/>
    <line x1="30" y1="22" x2="70" y2="22" stroke="#7f8fa4" stroke-width="1"/>
    <line x1="30" y1="30" x2="70" y2="30" stroke="#7f8fa4" stroke-width="1"/>
    <line x1="30" y1="38" x2="70" y2="38" stroke="#7f8fa4" stroke-width="1"/>
    <line x1="30" y1="46" x2="70" y2="46" stroke="#7f8fa4" stroke-width="1"/>
    <line x1="30" y1="54" x2="70" y2="54" stroke="#7f8fa4" stroke-width="1"/>
    <line x1="30" y1="62" x2="70" y2="62" stroke="#7f8fa4" stroke-width="1"/>
    <line x1="30" y1="70" x2="70" y2="70" stroke="#7f8fa4" stroke-width="1"/>
    <circle cx="34" cy="82" r="2" fill="#4ade80"/>
    <circle cx="42" cy="82" r="2" fill="#fbbf24"/>
    <text x="50" y="98" font-size="8" text-anchor="middle" fill="#222">{label}</text>
    """)


RACK_19 = _rack('RACK 19"')
RACK_23 = _rack('RACK 23"')


# ---------- CABLE LADDERS ----------
def _ladder(fill: str, label: str) -> str:
    rungs = "".join(
        f'<line x1="{x}" y1="40" x2="{x}" y2="60" stroke="#333" stroke-width="1.2"/>'
        for x in range(10, 95, 8)
    )
    return _svg(f"""
    <rect x="5" y="42" width="90" height="6" fill="{fill}" stroke="#222" stroke-width="1.2"/>
    <rect x="5" y="52" width="90" height="6" fill="{fill}" stroke="#222" stroke-width="1.2"/>
    {rungs}
    <text x="50" y="98" font-size="8" text-anchor="middle" fill="#222">{label}</text>
    """)


LADDER_IN = _ladder("#7FB77E", "LAD-IN")
LADDER_OUT = _ladder("#4F7A4F", "LAD-OUT")


# ---------- FOUNDATION ----------
BASEPAD = _svg("""
<rect x="5" y="5" width="90" height="90" fill="#d9d9d9" stroke="#333" stroke-width="2"/>
<line x1="5" y1="5" x2="95" y2="5" stroke="#888" stroke-width="1" stroke-dasharray="2,2"/>
<line x1="5" y1="95" x2="95" y2="95" stroke="#888" stroke-width="1" stroke-dasharray="2,2"/>
<line x1="5" y1="5" x2="5" y2="95" stroke="#888" stroke-width="1" stroke-dasharray="2,2"/>
<line x1="95" y1="5" x2="95" y2="95" stroke="#888" stroke-width="1" stroke-dasharray="2,2"/>
<line x1="5" y1="50" x2="95" y2="50" stroke="#999" stroke-width="0.5"/>
<line x1="50" y1="5" x2="50" y2="95" stroke="#999" stroke-width="0.5"/>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">BASEPAD</text>
""")

FENCE = _svg("""
<rect x="5" y="5" width="90" height="90" fill="rgba(0,0,0,0)" stroke="#222" stroke-width="2" stroke-dasharray="6,4"/>
<line x1="5" y1="5" x2="20" y2="5" stroke="#333" stroke-width="3"/>
<line x1="80" y1="5" x2="95" y2="5" stroke="#333" stroke-width="3"/>
<line x1="5" y1="95" x2="20" y2="95" stroke="#333" stroke-width="3"/>
<line x1="80" y1="95" x2="95" y2="95" stroke="#333" stroke-width="3"/>
<line x1="5" y1="5" x2="5" y2="20" stroke="#333" stroke-width="3"/>
<line x1="95" y1="5" x2="95" y2="20" stroke="#333" stroke-width="3"/>
<line x1="5" y1="80" x2="5" y2="95" stroke="#333" stroke-width="3"/>
<line x1="95" y1="80" x2="95" y2="95" stroke="#333" stroke-width="3"/>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">FENCE</text>
""")


# ---------- POWER ----------
GENERATOR = _svg("""
<rect x="8" y="18" width="84" height="64" fill="#C0392B" stroke="#222" stroke-width="2" rx="3"/>
<rect x="12" y="22" width="76" height="56" fill="#A93226" stroke="#111" stroke-width="1"/>
<line x1="20" y1="22" x2="20" y2="78" stroke="#6c1910" stroke-width="1"/>
<line x1="30" y1="22" x2="30" y2="78" stroke="#6c1910" stroke-width="1"/>
<line x1="70" y1="22" x2="70" y2="78" stroke="#6c1910" stroke-width="1"/>
<line x1="80" y1="22" x2="80" y2="78" stroke="#6c1910" stroke-width="1"/>
<circle cx="50" cy="50" r="10" fill="none" stroke="#fff" stroke-width="1.5"/>
<text x="50" y="54" font-size="9" text-anchor="middle" fill="#fff">G</text>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">GENERATOR</text>
""")

FUEL_TANK = _svg("""
<circle cx="50" cy="50" r="42" fill="#E8A33D" stroke="#222" stroke-width="2"/>
<circle cx="50" cy="50" r="34" fill="#F0B45A" stroke="#333" stroke-width="1"/>
<circle cx="50" cy="50" r="22" fill="none" stroke="#8a5a15" stroke-width="1" stroke-dasharray="3,2"/>
<circle cx="50" cy="50" r="6" fill="#5a3d10"/>
<line x1="50" y1="8" x2="50" y2="16" stroke="#222" stroke-width="2"/>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">FUEL</text>
""")

ATS = _svg("""
<rect x="15" y="25" width="70" height="50" fill="#D2691E" stroke="#222" stroke-width="2" rx="2"/>
<rect x="20" y="30" width="60" height="40" fill="#E67E22" stroke="#111" stroke-width="1"/>
<circle cx="35" cy="50" r="6" fill="#fff" stroke="#333" stroke-width="1"/>
<circle cx="50" cy="50" r="6" fill="none" stroke="#fff" stroke-width="1.5"/>
<circle cx="65" cy="50" r="6" fill="none" stroke="#fff" stroke-width="1.5"/>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">ATS</text>
""")

# ---------- ANTENNAS ----------
ANTENNA = _svg("""
<rect x="38" y="15" width="24" height="60" fill="#8E5DD8" stroke="#222" stroke-width="1.5" rx="2"/>
<line x1="42" y1="22" x2="58" y2="22" stroke="#4a2880" stroke-width="0.8"/>
<line x1="42" y1="30" x2="58" y2="30" stroke="#4a2880" stroke-width="0.8"/>
<line x1="42" y1="38" x2="58" y2="38" stroke="#4a2880" stroke-width="0.8"/>
<line x1="42" y1="46" x2="58" y2="46" stroke="#4a2880" stroke-width="0.8"/>
<line x1="42" y1="54" x2="58" y2="54" stroke="#4a2880" stroke-width="0.8"/>
<line x1="42" y1="62" x2="58" y2="62" stroke="#4a2880" stroke-width="0.8"/>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">ANT</text>
""")

RRU = _svg("""
<rect x="30" y="20" width="40" height="55" fill="#6E44B8" stroke="#222" stroke-width="1.5" rx="2"/>
<rect x="35" y="26" width="30" height="43" fill="#5a369c" stroke="#111" stroke-width="1"/>
<circle cx="50" cy="70" r="2" fill="#4ade80"/>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">RRU</text>
""")

CUSTOM = _svg("""
<rect x="10" y="15" width="80" height="70" fill="#cfcfcf" stroke="#333" stroke-width="2"/>
<text x="50" y="55" font-size="11" text-anchor="middle" fill="#333">CUSTOM</text>
<text x="50" y="98" font-size="9" text-anchor="middle" fill="#222">CUSTOM</text>
""")


# ---------- MAP ----------
ICON_MAP = {
    "tower_lattice": LATTICE,
    "tower_monopole": MONOPOLE,
    "tower_guyed": GUYED,
    "tower_rtwp": RTWP,
    "cabinet_outdoor": CABINET_OUT,
    "cabinet_indoor": CABINET_IN,
    "rack_19inch": RACK_19,
    "rack_23inch": RACK_23,
    "ladder_indoor": LADDER_IN,
    "ladder_outdoor": LADDER_OUT,
    "basepad": BASEPAD,
    "fence": FENCE,
    "generator": GENERATOR,
    "fuel_tank": FUEL_TANK,
    "ats_panel": ATS,
    "antenna_panel": ANTENNA,
    "rru": RRU,
    "custom_box": CUSTOM,
}


def get_icon_url(key: str) -> str:
    return ICON_MAP.get(key, CUSTOM)
