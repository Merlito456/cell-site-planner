"""
Cell Site Tower Floor Plan Maker — Full App (v6, live 2D↔3D sync)
==================================================================
Uses a Custom Streamlit Component (CCv2) wrapping Fabric.js.
- Live two-way sync: every edit inside the canvas reruns Streamlit
  and updates st.session_state.canvas_json.
- The 3D preview always reflects the current 2D canvas — including
  deletions, drags, rotates, and resizes.

Run:
    streamlit run app.py

Companion files:
    components/fabric_editor/__init__.py       -> CCv2 wrapper
    components/fabric_editor/frontend/index.html -> Fabric.js editor
    equipment_library.py                        -> catalog + fabric_group_objects()
    three_viewer.py                             -> Three.js 3D preview
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from equipment_library import (
    EQUIPMENT_LIBRARY,
    get_equipment,
    fabric_group_objects,
    px_to_m,
    px2_to_m2,
    PIXELS_PER_METER,
)
from three_viewer import build_3d_html

from components.fabric_editor import fabric_editor


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
    .metric-chip {
        background:#eef2f7; border:1px solid #d6dde7; border-radius:8px;
        padding:6px 10px; font-size:12px; color:#1f2937;
        display:inline-block; margin-right:6px;
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
# Session state helpers — MUST be defined before sidebar uses them
# ==================================================================
def _init_state():
    defaults = {
        "canvas_json": {"version": "5.3.0", "objects": []},
        "object_names": {},
        "object_equip": {},
        "object_heights": {},
        "canvas_w": 1000,
        "canvas_h": 700,
        "place_queue": [],
        "canvas_key": 0,
        "project_name": "Site-001",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def _bump_canvas():
    """Force a fresh canvas (new reset_nonce → component reloads the drawing)."""
    st.session_state.canvas_key += 1


def _apply_place_queue():
    """Convert queued equipment into Fabric group objects and append to canvas_json."""
    if not st.session_state.place_queue:
        return

    base = st.session_state.canvas_json or {"version": "5.3.0", "objects": []}
    base = json.loads(json.dumps(base))
    objects = base.setdefault("objects", [])

    for item in st.session_state.place_queue:
        equip = EQUIPMENT_LIBRARY[item["key"]]
        oid = str(uuid.uuid4())
        st.session_state.object_equip[oid] = item["key"]
        st.session_state.object_names.setdefault(oid, equip["label"])
        st.session_state.object_heights.setdefault(oid, item["height_3d"])

        w, h = item["w"], item["h"]
        offset = (len(objects) % 8) * 25
        left, top = 80 + offset, 80 + offset

        inner = fabric_group_objects(item["key"], w, h)

        shifted = []
        for sub in inner:
            sub = dict(sub)
            if sub["type"] == "line":
                sub["x1"] = sub.get("x1", 0) - w / 2
                sub["y1"] = sub.get("y1", 0) - h / 2
                sub["x2"] = sub.get("x2", 0) - w / 2
                sub["y2"] = sub.get("y2", 0) - h / 2
                sub.pop("left", None)
                sub.pop("top", None)
            else:
                sub["left"] = sub.get("left", 0) - w / 2
                sub["top"] = sub.get("top", 0) - h / 2
            shifted.append(sub)

        group_obj = {
            "type": "group",
            "id": oid,
            "left": left,
            "top": top,
            "width": w,
            "height": h,
            "scaleX": 1,
            "scaleY": 1,
            "angle": 0,
            "originX": "left",
            "originY": "top",
            "objects": shifted,
            "name": st.session_state.object_names[oid],
            "equipment_type": item["key"],
            "equip_height_3d": item["height_3d"],
        }
        objects.append(group_obj)

    st.session_state.canvas_json = base
    st.session_state.place_queue = []


def _ingest_live_state(live):
    """Merge the CCv2 component's returned value into session state."""
    if not live or not isinstance(live, dict):
        return
    if "objects" not in live:
        return
    st.session_state.canvas_json = live
    for obj in live.get("objects", []):
        oid = obj.get("id") or obj.get("name")
        if not oid:
            continue
        if obj.get("name"):
            st.session_state.object_names[oid] = obj["name"]
        if obj.get("equipment_type"):
            st.session_state.object_equip[oid] = obj["equipment_type"]
        if obj.get("equip_height_3d") is not None:
            st.session_state.object_heights[oid] = obj["equip_height_3d"]


# ==================================================================
# Init + apply anything pending from a previous run
# ==================================================================
_init_state()
_apply_place_queue()


# ==================================================================
# Sidebar
# ==================================================================
st.sidebar.title("🗼 Cell Site Planner")

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

st.sidebar.caption(f"**{picked_equip['label']}** — {picked_equip['category']}")

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
    _apply_place_queue()
    _bump_canvas()
    st.rerun()

st.sidebar.divider()

st.sidebar.subheader("2. Editing Tools")
st.sidebar.caption("Toolbar inside the canvas (below) handles Select / Rect / Circle / Line / Text / Delete / Undo.")
stroke_width = st.sidebar.slider("Default stroke width", 1, 6, 2, key="sw")
stroke_color = st.sidebar.color_picker("Stroke color", "#222222", key="sc")
fill_color = st.sidebar.color_picker("Fill color", "#4A90D9", key="fc")
bg_color = st.sidebar.color_picker("Background", "#ffffff", key="bgc")

st.sidebar.divider()

st.sidebar.subheader("3. Canvas")
st.session_state.canvas_w = st.sidebar.number_input(
    "Canvas width (px)", min_value=400, max_value=3000,
    value=st.session_state.canvas_w, step=50, key="csw",
)
st.session_state.canvas_h = st.sidebar.number_input(
    "Canvas height (px)", min_value=400, max_value=3000,
    value=st.session_state.canvas_h, step=50, key="csh",
)

st.sidebar.divider()

st.sidebar.subheader("4. Project")
st.session_state.project_name = st.sidebar.text_input(
    "Project name", value=st.session_state.project_name, key="pn"
)

col_clear, col_reset = st.sidebar.columns(2)
with col_clear:
    if st.button("🧹 Clear", use_container_width=True):
        st.session_state.canvas_json = {"version": "5.3.0", "objects": []}
        st.session_state.object_names = {}
        st.session_state.object_equip = {}
        st.session_state.object_heights = {}
        _bump_canvas()
        st.rerun()
with col_reset:
    if st.button("🔄 Reset view", use_container_width=True):
        _bump_canvas()
        st.rerun()

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

uploaded = st.sidebar.file_uploader(
    "📂 Import project (JSON)", type=["json"], key="import_file"
)
if uploaded is not None:
    try:
        data = json.load(uploaded)
        st.session_state.canvas_json = data.get("canvas_json") or {"objects": []}
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


# ==================================================================
# Layout: canvas + inspector
# ==================================================================
left, right = st.columns([3, 1], gap="medium")

with left:
    st.subheader("2D Floor Plan Editor")

    live_state = fabric_editor(
        initial_drawing=st.session_state.canvas_json or {"objects": []},
        reset_nonce=str(st.session_state.canvas_key),
        width=st.session_state.canvas_w,
        height=st.session_state.canvas_h,
        background=bg_color,
        key="fabric_editor_main",
    )

    # The component returns the live canvas JSON on every edit
    # (added / removed / modified). Merging it here keeps Python in sync
    # so the 3D preview and measurements update immediately.
    _ingest_live_state(live_state)

    st.caption(
        f"Scale: 20 px = 1 m  ·  "
        f"Canvas: {st.session_state.canvas_w}×{st.session_state.canvas_h}px  ·  "
        f"≈ {px_to_m(st.session_state.canvas_w)} × {px_to_m(st.session_state.canvas_h)} m  ·  "
        f"Live sync ✅"
    )


with right:
    st.subheader("Objects & Measurements")

    objects = (st.session_state.canvas_json or {}).get("objects", []) or []

    if not objects:
        st.info("No objects yet. Add equipment from the sidebar.")
    else:
        total_area_m2 = 0.0
        st.markdown(
            f'<div class="metric-chip"><b>{len(objects)}</b><br>objects</div>',
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

            w = (obj.get("width") or 40) * obj.get("scaleX", 1)
            h = (obj.get("height") or 40) * obj.get("scaleY", 1)
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

                new_name = st.text_input(
                    "Rename", value=label, key=f"rename_{oid}"
                )
                if new_name != label:
                    st.session_state.object_names[oid] = new_name
                    for o in st.session_state.canvas_json.get("objects", []):
                        if (o.get("id") or o.get("name")) == oid:
                            o["name"] = new_name

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
# 3D preview — always reflects the CURRENT canvas state
# ==================================================================
st.divider()
st.subheader("🌐 3D Preview")

objects_2d = (st.session_state.canvas_json or {}).get("objects", []) or []

geometry_objs = []
for o in objects_2d:
    if o.get("type") not in ("rect", "circle", "triangle", "image", "group"):
        continue
    oid = o.get("id") or o.get("name")
    equip_key = st.session_state.object_equip.get(oid) or o.get("equipment_type")
    if not equip_key:
        # Unknown object (e.g. user-drawn annotation) — skip silently
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

html3d = build_3d_html(
    geometry_objs,
    canvas_w=st.session_state.canvas_w,
    canvas_h=st.session_state.canvas_h,
)
components.html(html3d, height=580, scrolling=False)

if geometry_objs:
    by_cat: dict[str, int] = {}
    for o in geometry_objs:
        eq = EQUIPMENT_LIBRARY.get(o["equipment_type"], {})
        cat = eq.get("category", "Other")
        by_cat[cat] = by_cat.get(cat, 0) + 1
    cols = st.columns(max(1, len(by_cat)))
    for c, (cat, n) in zip(cols, sorted(by_cat.items())):
        c.metric(cat, n)
else:
    st.info("Add objects to the canvas to see them here in 3D.")


# ==================================================================
# Help
# ==================================================================
with st.expander("ℹ️ How to use", expanded=False):
    st.markdown(
        """
        ### How to use

        1. **Pick equipment** in the sidebar, adjust size, click **➕ Add to canvas**.
        2. Use the **toolbar above the canvas** to switch tools:
           - **Select** — drag, rotate (top handle), resize (corner handles)
           - **Rect / Circle / Line / Text** — draw annotations
           - **Delete** — remove selected objects
           - **Undo** — remove last object
        3. **Rename** objects and change **3D heights** on the right panel.
        4. The **3D preview below** updates automatically — including when
           you delete, drag, or rotate objects inside the canvas.
        5. **Export / Import** projects as JSON.

        ### Scale
        `20 px = 1 m`. All measurements in meters.

        ### Live sync
        The 2D canvas is a Custom Streamlit Component (CCv2). Every edit
        inside it pushes the updated drawing JSON back to Python, which
        reruns the app and refreshes the 3D preview. There is a short
        debounce (~250ms) so dragging doesn't spam reruns.

        ### Notes
        - The canvas only resets when you click **Add**, **Clear**,
          **Reset view**, or **Import**.
        - Lattice / guyed towers are visually represented (truss legs,
          braces, guy wires) but not structurally simulated.
        - Freeform and text objects are not extruded to 3D (no volume).
        """
    )

st.caption(
    f"Cell Site Floor Plan Maker · {st.session_state.project_name} · "
    f"{len((st.session_state.canvas_json or {}).get('objects', []) or [])} object(s)"
)
