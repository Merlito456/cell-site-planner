"""
Cell Site Tower Floor Plan Maker — Full App (v3, fixed)
=======================================================
Streamlit + Fabric.js (2D editing with realistic SVG symbols)
         + Three.js  (realistic composed 3D preview)

Run:
    streamlit run app.py

Dependencies (requirements.txt):
    streamlit>=1.36.0
    streamlit-drawable-canvas-fix>=0.9.4
    Pillow>=10.0.0

Companion files (must exist in the same folder):
    icons2d.py             -> 2D SVG top-view symbols (base64 data URLs)
    equipment_library.py   -> equipment catalog + helpers
    three_viewer.py        -> realistic Three.js 3D preview builder

Key fixes in this version
-------------------------
1. Canvas is re-keyed ONLY on explicit actions (add / clear / import /
   reset). Sidebar widget changes do NOT reset the canvas anymore.
2. New objects are written directly into `canvas_json` (not just a
   temporary queue), so they persist across reruns.
3. `crossOrigin` is set BEFORE `src` on image objects.
4. The 3D preview is rendered OUTSIDE of tabs (tabs re-run both panes
   every rerun, which was silently killing the canvas).
5. A debug expander in the sidebar lets you verify icons load.
"""

import json
import uuid
from datetime import datetime

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import streamlit.components.v1 as components

from equipment_library import (
    EQUIPMENT_LIBRARY,
    get_equipment,
    get_icon_for,
    px_to_m,
    px2_to_m2,
    PIXELS_PER_METER,
)
from three_viewer import build_3d_html


# ==================================================================
# Page config
# ==================================================================
st.set_page_config(
    page_title="Cell Site Floor Plan Maker",
    page_icon="🗼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .eq-card {
        background:#f8f9fb; border:1px solid #e0e3e8; border-radius:8px;
        padding:6px 10px; margin-bottom:6px; font-size:13px; line-height:1.5;
    }
    .eq-card b { color:#1f2937; }
    .metric-strip {
        display:flex; gap:8px; flex-wrap:wrap; margin-bottom:8px;
    }
    .metric-chip {
        background:#eef2f7; border:1px solid #d6dde7; border-radius:8px;
        padding:6px 10px; font-size:12px; color:#1f2937;
    }
    .metric-chip b { font-size:14px; }
    .cat-badge {
        display:inline-block; padding:2px 8px; border-radius:10px;
        background:#e8eef7; color:#2a4a76; font-size:11px;
        margin-bottom:4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================================
# Session state
# ==================================================================
def _init_state():
    defaults = {
        "canvas_json": None,
        "object_names": {},        # object_id -> display name
        "object_equip": {},        # object_id -> equipment key
        "object_heights": {},      # object_id -> 3D height override (m)
        "canvas_w": 1000,
        "canvas_h": 700,
        "place_queue": [],         # pending equipment placements
        "canvas_key": 0,           # bump to force canvas reset
        "project_name": "Site-001",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

_init_state()


def _bump_canvas():
    """Force the Fabric canvas to be rebuilt with a fresh key."""
    st.session_state.canvas_key += 1


# ==================================================================
# Sidebar — equipment picker & canvas settings
# ==================================================================
st.sidebar.title("🗼 Cell Site Planner")

# ---- Build category index -----------------------------------------
categories: dict[str, list[str]] = {}
for k, v in EQUIPMENT_LIBRARY.items():
    categories.setdefault(v["category"], []).append(k)

st.sidebar.subheader("1. Add Equipment")
category = st.sidebar.selectbox(
    "Category", sorted(categories.keys()), key="sel_category"
)
equip_keys = categories[category]
equip_labels = [EQUIPMENT_LIBRARY[k]["label"] for k in equip_keys]
picked_label = st.sidebar.selectbox(
    "Equipment", equip_labels, key="sel_equipment"
)
picked_key = equip_keys[equip_labels.index(picked_label)]
picked_equip = EQUIPMENT_LIBRARY[picked_key]

st.sidebar.caption(
    f"**{picked_equip['label']}** — {picked_equip['category']}"
)

custom_w = st.sidebar.number_input(
    "Footprint width (px)",
    min_value=10, max_value=800,
    value=int(picked_equip["w"]), step=5,
    key=f"cw_{picked_key}",
)
custom_h = st.sidebar.number_input(
    "Footprint depth (px)",
    min_value=10, max_value=800,
    value=int(picked_equip["h"]), step=5,
    key=f"ch_{picked_key}",
)
custom_height = st.sidebar.number_input(
    "3D height (m)",
    min_value=0.1, max_value=300.0,
    value=float(picked_equip["height_3d"]), step=0.1,
    key=f"ch3d_{picked_key}",
)

if st.sidebar.button("➕ Add to canvas", use_container_width=True, type="primary"):
    st.session_state.place_queue.append({
        "key": picked_key,
        "w": custom_w,
        "h": custom_h,
        "height_3d": custom_height,
    })
    # CRITICAL: bump the canvas key so a fresh canvas is built with the
    # new object baked into initial_drawing.
    _bump_canvas()
    st.rerun()

st.sidebar.divider()

# ---- Editing tools (these do NOT bump the canvas) ----------------
st.sidebar.subheader("2. Editing Tools")
drawing_mode = st.sidebar.selectbox(
    "Mode",
    ["transform", "rect", "circle", "line", "polygon", "freeform", "text"],
    index=0,
    help="Use 'transform' to drag/rotate/scale placed objects.",
    key="mode_select",
)
stroke_width = st.sidebar.slider("Stroke width", 1, 6, 2, key="sw")
stroke_color = st.sidebar.color_picker("Stroke color", "#222222", key="sc")
fill_color = st.sidebar.color_picker("Fill color", "#4A90D9", key="fc")
bg_color = st.sidebar.color_picker("Background", "#ffffff", key="bgc")

st.sidebar.divider()

# ---- Canvas settings ---------------------------------------------
st.sidebar.subheader("3. Canvas")
st.session_state.canvas_w = st.sidebar.number_input(
    "Canvas width (px)",
    min_value=400, max_value=3000,
    value=st.session_state.canvas_w, step=50,
    key="csw",
)
st.session_state.canvas_h = st.sidebar.number_input(
    "Canvas height (px)",
    min_value=400, max_value=3000,
    value=st.session_state.canvas_h, step=50,
    key="csh",
)

st.sidebar.divider()

# ---- Project ------------------------------------------------------
st.sidebar.subheader("4. Project")
st.session_state.project_name = st.sidebar.text_input(
    "Project name", value=st.session_state.project_name, key="pn"
)

col_clear, col_reset = st.sidebar.columns(2)
with col_clear:
    if st.button("🧹 Clear", use_container_width=True):
        st.session_state.canvas_json = None
        st.session_state.object_names = {}
        st.session_state.object_equip = {}
        st.session_state.object_heights = {}
        _bump_canvas()
        st.rerun()
with col_reset:
    if st.button("🔄 Reset view", use_container_width=True):
        _bump_canvas()
        st.rerun()

# Export
export_payload = {
    "project": st.session_state.project_name,
    "saved_at": datetime.utcnow().isoformat() + "Z",
    "canvas_json": st.session_state.canvas_json,
    "object_names": st.session_state.object_names,
    "object_equip": st.session_state.object_equip,
    "object_heights": st.session_state.object_heights,
    "canvas_w": st.session_state.canvas_w,
    "canvas_h": st.session_state.canvas_h,
}
st.sidebar.download_button(
    "💾 Export project (JSON)",
    data=json.dumps(export_payload, indent=2),
    file_name=f"{st.session_state.project_name}_floorplan.json",
    mime="application/json",
    use_container_width=True,
)

# Import
uploaded = st.sidebar.file_uploader(
    "📂 Import project (JSON)", type=["json"], key="import_file"
)
if uploaded is not None:
    try:
        data = json.load(uploaded)
        st.session_state.canvas_json = data.get("canvas_json")
        st.session_state.object_names = data.get("object_names", {})
        st.session_state.object_equip = data.get("object_equip", {})
        st.session_state.object_heights = data.get("object_heights", {})
        st.session_state.canvas_w = data.get("canvas_w", 1000)
        st.session_state.canvas_h = data.get("canvas_h", 700)
        st.session_state.project_name = data.get("project", "Site-001")
        _bump_canvas()
        st.sidebar.success("Project loaded.")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Load failed: {e}")

# ---- Debug expander ----------------------------------------------
with st.sidebar.expander("🔍 Debug: icon preview"):
    st.caption("Verifies that SVG icons are generated correctly.")
    for k in ["tower_lattice", "cabinet_outdoor", "generator", "fuel_tank"]:
        url = get_icon_for(k)
        st.caption(f"{k} · len={len(url)} · has#={'#' in url}")
        st.image(url, width=70)


# ==================================================================
# Build `initial_drawing` (persisted canvas + pending placements)
# ==================================================================
def _build_initial_drawing() -> dict:
    """
    Merge the last-known canvas JSON with any newly queued equipment.
    New items are written directly into the returned dict AND into
    st.session_state.canvas_json so they persist across reruns.
    """
    # If there is nothing new to add, just hand back the stored canvas.
    if not st.session_state.place_queue and st.session_state.canvas_json:
        return st.session_state.canvas_json

    base = st.session_state.canvas_json or {
        "version": "5.3.0",
        "objects": [],
        "background": "#ffffff",
    }
    # Deep copy so we don't mutate the session dict while iterating
    base = json.loads(json.dumps(base))
    objects = base.setdefault("objects", [])

    for item in st.session_state.place_queue:
        equip = EQUIPMENT_LIBRARY[item["key"]]
        oid = str(uuid.uuid4())
        st.session_state.object_equip[oid] = item["key"]
        st.session_state.object_names.setdefault(oid, equip["label"])
        st.session_state.object_heights.setdefault(oid, item["height_3d"])

        # Stagger new items so they don't stack perfectly.
        offset = (len(objects) % 8) * 25
        icon_url = get_icon_for(item["key"])

        obj = {
            "id": oid,
            "type": "image",
            # crossOrigin MUST be before src for Fabric.js to load data URLs
            "crossOrigin": "anonymous",
            "src": icon_url,
            "left": 80 + offset,
            "top": 80 + offset,
            "width": item["w"],
            "height": item["h"],
            "scaleX": 1,
            "scaleY": 1,
            "angle": 0,
            "opacity": 1,
            "name": st.session_state.object_names[oid],
            "equipment_type": item["key"],
            "equip_height_3d": item["height_3d"],
        }
        objects.append(obj)

    # Persist back so the next rerun keeps everything.
    st.session_state.canvas_json = base
    st.session_state.place_queue = []
    return base


initial_drawing = _build_initial_drawing()


# ==================================================================
# Helper — sync object metadata from canvas back into session
# ==================================================================
def _sync_from_canvas(canvas_json: dict) -> None:
    if not canvas_json:
        return
    for obj in canvas_json.get("objects", []):
        oid = obj.get("id") or obj.get("name")
        if not oid:
            continue
        if obj.get("name"):
            st.session_state.object_names[oid] = obj["name"]
        if obj.get("equipment_type"):
            st.session_state.object_equip[oid] = obj["equipment_type"]


# ==================================================================
# Layout: 2D canvas + right-hand inspector
# ==================================================================
left, right = st.columns([3, 1], gap="medium")

with left:
    st.subheader("2D Floor Plan Editor")

    canvas_result = st_canvas(
        fill_color=fill_color + "55" if fill_color.startswith("#") else fill_color,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=None,
        update_streamlit=True,
        height=st.session_state.canvas_h,
        width=st.session_state.canvas_w,
        drawing_mode=drawing_mode,
        initial_drawing=initial_drawing,
        display_toolbar=True,
        key=f"canvas_{st.session_state.canvas_key}",
    )

    if canvas_result.json_data is not None:
        st.session_state.canvas_json = canvas_result.json_data
        _sync_from_canvas(canvas_result.json_data)

    st.caption(
        f"Scale: 20 px = 1 m  ·  "
        f"Canvas: {st.session_state.canvas_w}×{st.session_state.canvas_h}px  ·  "
        f"≈ {px_to_m(st.session_state.canvas_w)} × {px_to_m(st.session_state.canvas_h)} m"
    )


# ==================================================================
# Right panel — object inspector, measurements, distances
# ==================================================================
with right:
    st.subheader("Objects & Measurements")

    objects = (st.session_state.canvas_json or {}).get("objects", []) or []

    if not objects:
        st.info("No objects yet. Add equipment from the sidebar.")
    else:
        total_area_m2 = 0.0

        st.markdown(
            f"""
            <div class="metric-strip">
              <div class="metric-chip"><b>{len(objects)}</b><br>objects</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for i, obj in enumerate(objects):
            oid = obj.get("id") or obj.get("name") or f"obj_{i}"
            equip_key = (
                st.session_state.object_equip.get(oid)
                or obj.get("equipment_type")
                or "custom_box"
            )
            equip = EQUIPMENT_LIBRARY.get(equip_key, EQUIPMENT_LIBRARY["custom_box"])
            label = st.session_state.object_names.get(oid, equip["label"])

            w = (obj.get("width") or (obj.get("radius", 0) * 2) or 40) * obj.get("scaleX", 1)
            h = (obj.get("height") or (obj.get("radius", 0) * 2) or 40) * obj.get("scaleY", 1)
            area_m2 = px2_to_m2(w, h)
            total_area_m2 += area_m2

            with st.expander(f"#{i+1} — {label}", expanded=False):
                st.markdown(
                    f"""
                    <div class="eq-card">
                    <span class="cat-badge">{equip.get('category','—')}</span><br>
                    <b>Type:</b> {equip.get('label', obj.get('type','?'))}<br>
                    <b>Size:</b> {px_to_m(w)} × {px_to_m(h)} m<br>
                    <b>Area:</b> {area_m2} m²<br>
                    <b>Rotation:</b> {round(obj.get('angle', 0), 1)}°<br>
                    <b>Position:</b> ({int(obj.get('left',0))}, {int(obj.get('top',0))}) px
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # rename (does not re-key the canvas — just updates metadata)
                new_name = st.text_input(
                    "Rename", value=label, key=f"rename_{oid}"
                )
                if new_name != label:
                    st.session_state.object_names[oid] = new_name
                    for o in st.session_state.canvas_json.get("objects", []):
                        if (o.get("id") or o.get("name")) == oid:
                            o["name"] = new_name

                # 3D height override
                default_h = st.session_state.object_heights.get(
                    oid, equip.get("height_3d", 1.0)
                )
                new_h = st.number_input(
                    "3D height (m)",
                    min_value=0.1, max_value=300.0,
                    value=float(default_h), step=0.1,
                    key=f"h3d_{oid}",
                )
                if new_h != default_h:
                    st.session_state.object_heights[oid] = new_h
                    for o in st.session_state.canvas_json.get("objects", []):
                        if (o.get("id") or o.get("name")) == oid:
                            o["equip_height_3d"] = new_h

        st.divider()
        st.metric("Total footprint", f"{round(total_area_m2, 2)} m²")

        # ---- Distance tool ----
        if len(objects) >= 2:
            st.divider()
            st.markdown("**Distance between objects**")
            labels = [
                f"#{i+1} — "
                f"{st.session_state.object_names.get(o.get('id') or o.get('name'), 'obj')}"
                for i, o in enumerate(objects)
            ]
            a = st.selectbox("From", labels, index=0, key="dist_a")
            b = st.selectbox("To", labels, index=min(1, len(labels) - 1), key="dist_b")
            ia = labels.index(a)
            ib = labels.index(b)
            oa, ob = objects[ia], objects[ib]
            dx = oa.get("left", 0) - ob.get("left", 0)
            dy = oa.get("top", 0) - ob.get("top", 0)
            dist_px = (dx * dx + dy * dy) ** 0.5
            st.success(f"{px_to_m(dist_px)} m apart")


# ==================================================================
# 3D Preview (rendered OUTSIDE tabs to avoid canvas reset)
# ==================================================================
st.divider()
st.subheader("🌐 3D Preview")

objects_2d = (st.session_state.canvas_json or {}).get("objects", []) or []

geometry_objs = []
for o in objects_2d:
    if o.get("type") not in ("rect", "circle", "triangle", "image"):
        continue
    oid = o.get("id") or o.get("name")
    equip_key = st.session_state.object_equip.get(oid) or o.get("equipment_type")
    if not equip_key:
        continue
    enriched = dict(o)
    enriched["equipment_type"] = equip_key
    enriched["name"] = st.session_state.object_names.get(
        oid, EQUIPMENT_LIBRARY[equip_key]["label"]
    )
    h_override = st.session_state.object_heights.get(oid)
    if h_override is not None:
        enriched["equip_height_3d"] = h_override
    geometry_objs.append(enriched)

html = build_3d_html(
    geometry_objs,
    canvas_w=st.session_state.canvas_w,
    canvas_h=st.session_state.canvas_h,
)
components.html(html, height=580, scrolling=False)

# Quick stats under the 3D view
if geometry_objs:
    by_cat: dict[str, int] = {}
    for o in geometry_objs:
        eq = EQUIPMENT_LIBRARY.get(o["equipment_type"], {})
        cat = eq.get("category", "Other")
        by_cat[cat] = by_cat.get(cat, 0) + 1
    cols = st.columns(max(1, len(by_cat)))
    for c, (cat, n) in zip(cols, sorted(by_cat.items())):
        c.metric(cat, n)


# ==================================================================
# Help (in an expander, not a tab)
# ==================================================================
with st.expander("ℹ️ How to use", expanded=False):
    st.markdown(
        """
        ### How to use

        1. **Pick equipment** from the sidebar (categorized: Tower, Cabinet,
           Rack, Cable Ladder, Foundation, Power, Antenna, Custom).
        2. Adjust the **2D footprint** and **3D height** if needed.
        3. Click **➕ Add to canvas** — the canvas refreshes and the object
           appears with a real top-view symbol.
        4. Switch the canvas **Mode** to **transform** and use the toolbar to
           **drag, rotate, resize**. Use the trash icon to delete.
        5. Use **rect / circle / line / polygon / text** modes to add
           annotations directly on the plan.
        6. **Rename objects** and set per-object **3D heights** in the right
           panel — names appear on the 3D labels.
        7. Use the **Distance tool** to measure between any two objects.
        8. The **3D preview** below updates automatically.
        9. **Export / Import** the project as JSON.

        ### Scale
        `20 px = 1 m` on the 2D canvas. All measurements shown in meters.
        Adjust `PIXELS_PER_METER` in `equipment_library.py` if you need a
        different scale.

        ### 3D mouse controls
        - **Left drag** – orbit
        - **Right drag** – pan
        - **Scroll** – zoom

        ### Notes & limitations
        - The 3D preview is **view-only** — all editing is done on the 2D
          canvas. This is by design (matches most browser floor planners).
        - Lattice / guyed towers are **visually represented** (truss legs,
          braces, guy wires) but not structurally simulated.
        - Freeform and text objects are not extruded (no volume).
        - **Canvas reset behavior:** the canvas only resets when you click
          Add / Clear / Reset / Import. Changing sliders, colors, or drawing
          mode will not blank your work.

        ### Deploying to Streamlit Cloud
        1. Push the project folder to GitHub.
        2. Go to https://share.streamlit.io → **New app**.
        3. Select the repo, branch, and `app.py`.
        4. Click **Deploy**.
        """
    )

st.caption(
    f"Cell Site Floor Plan Maker · {st.session_state.project_name} · "
    f"{len((st.session_state.canvas_json or {}).get('objects', []) or [])} object(s) · "
    f"scale 20 px = 1 m"
)
