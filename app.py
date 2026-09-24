"""
Cell Site Tower Floor Plan Maker
--------------------------------
Streamlit + Fabric.js (2D editing) + Three.js (3D preview)

Run:
    streamlit run app.py
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
    px_to_m,
    px2_to_m2,
    PIXELS_PER_METER,
)
from three_viewer import build_3d_html


# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Cell Site Floor Plan Maker",
    page_icon="🗼",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .eq-card {
        background:#f8f9fb; border:1px solid #e0e3e8; border-radius:8px;
        padding:6px 10px; margin-bottom:4px; font-size:13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Session state
# ------------------------------------------------------------------
def _init_state():
    defaults = {
        "canvas_json": None,
        "object_names": {},       # object_id -> name
        "object_equip": {},       # object_id -> equipment key
        "canvas_w": 1000,
        "canvas_h": 700,
        "place_queue": [],        # list of equipment keys to inject
        "canvas_key": 0,          # bump to reset canvas
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

_init_state()


# ------------------------------------------------------------------
# Sidebar — equipment picker & settings
# ------------------------------------------------------------------
st.sidebar.title("🗼 Cell Site Planner")

categories = {}
for k, v in EQUIPMENT_LIBRARY.items():
    categories.setdefault(v["category"], []).append(k)

st.sidebar.subheader("1. Add Equipment")
category = st.sidebar.selectbox("Category", sorted(categories.keys()))
equip_keys = categories[category]
equip_labels = [f'{EQUIPMENT_LIBRARY[k]["label"]}' for k in equip_keys]
picked_label = st.sidebar.selectbox("Equipment", equip_labels, key="pick_equip")
picked_key = equip_keys[equip_labels.index(picked_label)]

custom_w = st.sidebar.number_input(
    "Footprint width (px)", 10, 600,
    int(EQUIPMENT_LIBRARY[picked_key]["w"]), 5, key="cw"
)
custom_h = st.sidebar.number_input(
    "Footprint depth (px)", 10, 600,
    int(EQUIPMENT_LIBRARY[picked_key]["h"]), 5, key="ch"
)
custom_height = st.sidebar.number_input(
    "3D height (m)", 0.1, 200.0,
    float(EQUIPMENT_LIBRARY[picked_key]["height_3d"]), 0.1, key="cht"
)

if st.sidebar.button("➕ Add to canvas", use_container_width=True):
    st.session_state.place_queue.append({
        "key": picked_key,
        "w": custom_w,
        "h": custom_h,
        "height_3d": custom_height,
    })
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("2. Editing Tools")
drawing_mode = st.sidebar.selectbox(
    "Mode",
    ["transform", "rect", "circle", "line", "polygon", "freeform", "text"],
    index=0,
    help="Use 'transform' to drag/rotate/scale placed objects.",
)

stroke_width = st.sidebar.slider("Stroke width", 1, 6, 2)
stroke_color = st.sidebar.color_picker("Stroke color", "#222222")
fill_color = st.sidebar.color_picker("Fill color", "#4A90D9")
bg_color = st.sidebar.color_picker("Background", "#ffffff")

st.sidebar.divider()
st.sidebar.subheader("3. Canvas")
st.session_state.canvas_w = st.sidebar.number_input(
    "Canvas width (px)", 400, 3000, st.session_state.canvas_w, 50
)
st.session_state.canvas_h = st.sidebar.number_input(
    "Canvas height (px)", 400, 3000, st.session_state.canvas_h, 50
)

grid_on = st.sidebar.checkbox("Show 20px grid overlay", value=True)

st.sidebar.divider()
st.sidebar.subheader("4. Project")
project_name = st.sidebar.text_input("Project name", "Site-001")
if st.sidebar.button("🧹 Clear canvas", use_container_width=True):
    st.session_state.canvas_json = None
    st.session_state.object_names = {}
    st.session_state.object_equip = {}
    st.session_state.canvas_key += 1
    st.rerun()

# Save / load
st.sidebar.download_button(
    "💾 Export project (JSON)",
    data=json.dumps(
        {
            "project": project_name,
            "saved_at": datetime.utcnow().isoformat(),
            "canvas_json": st.session_state.canvas_json,
            "object_names": st.session_state.object_names,
            "object_equip": st.session_state.object_equip,
            "canvas_w": st.session_state.canvas_w,
            "canvas_h": st.session_state.canvas_h,
        },
        indent=2,
    ),
    file_name=f"{project_name}_floorplan.json",
    mime="application/json",
    use_container_width=True,
)

uploaded = st.sidebar.file_uploader("📂 Import project (JSON)", type=["json"])
if uploaded is not None:
    try:
        data = json.load(uploaded)
        st.session_state.canvas_json = data.get("canvas_json")
        st.session_state.object_names = data.get("object_names", {})
        st.session_state.object_equip = data.get("object_equip", {})
        st.session_state.canvas_w = data.get("canvas_w", 1000)
        st.session_state.canvas_h = data.get("canvas_h", 700)
        st.session_state.canvas_key += 1
        st.sidebar.success("Project loaded.")
    except Exception as e:
        st.sidebar.error(f"Load failed: {e}")


# ------------------------------------------------------------------
# Build initial_drawing from queue + previous state
# ------------------------------------------------------------------
def _build_initial_drawing():
    """Combine persisted canvas JSON with any pending placements."""
    base = st.session_state.canvas_json or {
        "version": "5.3.0",
        "objects": [],
        "background": "#ffffff",
    }
    # copy so we don't mutate session
    base = json.loads(json.dumps(base))
    objects = base.setdefault("objects", [])

    for item in st.session_state.place_queue:
        equip = EQUIPMENT_LIBRARY[item["key"]]
        oid = str(uuid.uuid4())
        st.session_state.object_equip[oid] = item["key"]
        st.session_state.object_names.setdefault(oid, equip["label"])

        # stagger new items so they don't perfectly overlap
        offset = (len(objects) % 6) * 30
        common = {
            "id": oid,
            "left": 60 + offset,
            "top": 60 + offset,
            "fill": equip["color_2d"],
            "stroke": "#333333",
            "strokeWidth": 2,
            "scaleX": 1,
            "scaleY": 1,
            "angle": 0,
            "name": st.session_state.object_names[oid],
            "equipment_type": item["key"],
        }
        if equip["shape"] == "circle":
            common.update({
                "type": "circle",
                "radius": max(item["w"], item["h"]) / 2,
            })
        else:
            common.update({
                "type": "rect",
                "width": item["w"],
                "height": item["h"],
            })
        objects.append(common)

    st.session_state.place_queue = []
    return base


initial_drawing = _build_initial_drawing()


# ------------------------------------------------------------------
# Layout: 2D canvas (left) + info panel (right)
# ------------------------------------------------------------------
left, right = st.columns([3, 1])

with left:
    st.subheader("2D Floor Plan Editor")

    canvas_result = st_canvas(
        fill_color=fill_color + "88" if fill_color.startswith("#") else fill_color,
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

        # refresh name/equip maps from returned objects
        for obj in canvas_result.json_data.get("objects", []):
            oid = obj.get("id") or obj.get("name")
            if not oid:
                continue
            st.session_state.object_names[oid] = obj.get("name", "Unnamed")
            if obj.get("equipment_type"):
                st.session_state.object_equip[oid] = obj["equipment_type"]

    if grid_on:
        st.caption(f"Grid: 20px ≈ 1m  |  Canvas: {st.session_state.canvas_w}×{st.session_state.canvas_h}px")


# ------------------------------------------------------------------
# Right panel — object inspector & measurements
# ------------------------------------------------------------------
with right:
    st.subheader("Objects & Measurements")

    objects = (st.session_state.canvas_json or {}).get("objects", []) or []

    if not objects:
        st.info("No objects yet. Add equipment from the sidebar.")
    else:
        total_area_m2 = 0.0
        for i, obj in enumerate(objects):
            oid = obj.get("id") or obj.get("name") or f"obj_{i}"
            equip_key = st.session_state.object_equip.get(oid)
            equip = EQUIPMENT_LIBRARY.get(equip_key, {})
            label = st.session_state.object_names.get(oid, equip.get("label", "Unnamed"))

            w = (obj.get("width") or (obj.get("radius", 0) * 2)) * obj.get("scaleX", 1)
            h = (obj.get("height") or (obj.get("radius", 0) * 2)) * obj.get("scaleY", 1)

            area_m2 = px2_to_m2(w, h)
            total_area_m2 += area_m2

            with st.expander(f"#{i+1} — {label}", expanded=False):
                st.markdown(
                    f"""
                    <div class="eq-card">
                    <b>Type:</b> {equip.get('label', obj.get('type','?'))}<br>
                    <b>Size:</b> {px_to_m(w)} m × {px_to_m(h)} m<br>
                    <b>Area:</b> {area_m2} m²<br>
                    <b>Rotation:</b> {round(obj.get('angle', 0), 1)}°<br>
                    <b>Position:</b> ({int(obj.get('left',0))}, {int(obj.get('top',0))}) px
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                new_name = st.text_input(
                    "Rename", value=label, key=f"rename_{oid}"
                )
                if new_name != label:
                    st.session_state.object_names[oid] = new_name
                    # also update the canvas object's name field
                    for o in st.session_state.canvas_json.get("objects", []):
                        if (o.get("id") or o.get("name")) == oid:
                            o["name"] = new_name

        st.divider()
        st.metric("Objects", len(objects))
        st.metric("Total footprint", f"{round(total_area_m2, 2)} m²")

        # quick distance measure between two selected objects
        if len(objects) >= 2:
            st.divider()
            st.markdown("**Distance between objects**")
            labels = [f"#{i+1}" for i in range(len(objects))]
            a = st.selectbox("From", labels, index=0, key="dist_a")
            b = st.selectbox("To", labels, index=1, key="dist_b")
            ia, ib = int(a[1:]) - 1, int(b[1:]) - 1
            oa, ob = objects[ia], objects[ib]
            dx = oa.get("left", 0) - ob.get("left", 0)
            dy = oa.get("top", 0) - ob.get("top", 0)
            dist_px = (dx * dx + dy * dy) ** 0.5
            st.success(f"{px_to_m(dist_px)} m apart")


# ------------------------------------------------------------------
# 3D Preview tab
# ------------------------------------------------------------------
st.divider()
tab_3d, tab_help = st.tabs(["🌐 3D Preview", "ℹ️ Help"])

with tab_3d:
    objects_2d = (st.session_state.canvas_json or {}).get("objects", []) or []
    # filter out freeform/text — only extrude geometric primitives
    geometry_objs = [
        o for o in objects_2d
        if o.get("type") in ("rect", "circle", "triangle")
    ]

    # apply user-renamed labels + chosen equipment heights before passing to Three
    for o in geometry_objs:
        oid = o.get("id") or o.get("name")
        if oid in st.session_state.object_names:
            o["name"] = st.session_state.object_names[oid]
        if oid in st.session_state.object_equip:
            o["equipment_type"] = st.session_state.object_equip[oid]

    html = build_3d_html(
        geometry_objs,
        canvas_w=st.session_state.canvas_w,
        canvas_h=st.session_state.canvas_h,
    )
    components.html(html, height=560, scrolling=False)

with tab_help:
    st.markdown(
        """
        ### How to use
        1. **Pick equipment** in the sidebar, adjust size & 3D height, click **➕ Add to canvas**.
        2. Use the canvas toolbar to switch to **transform** mode and **drag / rotate / resize** objects.
        3. Use **rect / circle / line / text** tools to draw extra annotations directly.
        4. **Rename objects** in the right panel — names appear in the 3D view and exports.
        5. **Measure distances** between any two placed objects using the "Distance" tool.
        6. Switch to the **3D Preview** tab to see the extruded site model.
        7. **Export / Import** the whole project as JSON.

        ### Scale
        `20 px = 1 m` (2D). All measurements shown in meters.

        ### Mouse controls (3D)
        - **Left drag** – orbit
        - **Right drag** – pan
        - **Scroll** – zoom

        ### Notes
        - 3D preview is **view-only** — all editing happens on the 2D canvas.
        - Freeform and text objects are not extruded (they'd have no volume).
        - Lattice / guyed towers are simplified as solid volumes for clarity.
        """
    )

st.caption(
    f"Cell Site Floor Plan Maker  ·  {project_name}  ·  "
    f"{len((st.session_state.canvas_json or {}).get('objects', []) or [])} object(s)"
)
