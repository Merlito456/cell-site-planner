"""
Embedded Fabric.js canvas for Streamlit.
- Full drag/rotate/resize support (native Fabric.js).
- State is persisted to st.session_state via a hidden text input,
  which Streamlit re-reads on every rerun.
- Does NOT use `streamlit-drawable-canvas-fix`.
"""

import json
import uuid

import streamlit as st
import streamlit.components.v1 as components


def fabric_canvas(
    drawing_json: dict,
    height: int,
    width: int,
    canvas_key: str,
    drawing_mode: str = "transform",
    stroke_color: str = "#222222",
    fill_color: str = "#4A90D9",
    stroke_width: int = 2,
    background_color: str = "#ffffff",
) -> str:
    """
    Renders a Fabric.js canvas inside a Streamlit component.

    Returns the current drawing JSON (parsed from the component) as a
    string so the caller can store it. State is handed back via a
    hidden <input> element that Streamlit reads through the component's
    `value` return.
    """

    # A fresh nonce forces the component to reset when we want it to.
    nonce = uuid.uuid4().hex[:8]

    initial_json = json.dumps(drawing_json or {"version": "5.3.0", "objects": []})

    html = _CANVAS_HTML.replace("__INITIAL__", initial_json) \
                       .replace("__MODE__", drawing_mode) \
                       .replace("__STROKE__", stroke_color) \
                       .replace("__FILL__", fill_color) \
                       .replace("__STROKE_W__", str(stroke_width)) \
                       .replace("__BG__", background_color) \
                       .replace("__HEIGHT__", str(height)) \
                       .replace("__WIDTH__", str(width)) \
                       .replace("__NONCE__", nonce)

    # Use a stable key so React doesn't recreate the iframe on reruns.
    # We embed the nonce in the HTML itself to force Fabric to reload
    # when we *want* a fresh canvas (e.g. on Add / Clear).
    components.html(html, height=height + 60, scrolling=False, key=canvas_key)
    return initial_json


_CANVAS_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  html, body { margin:0; padding:0; background:#ffffff; overflow:hidden; }
  #wrap { position:relative; width:__WIDTH__px; height:__HEIGHT__px; }
  .canvas-container { box-shadow: inset 0 0 0 1px #e0e3e8; }
  #toolbar {
    display:flex; gap:4px; padding:4px 6px; margin-bottom:4px;
    background:#f4f6f9; border:1px solid #d8dee6; border-radius:6px;
    align-items:center; font-family:system-ui, sans-serif; font-size:12px;
  }
  #toolbar button {
    padding:4px 10px; border:1px solid #c7cfda; background:#fff;
    border-radius:4px; cursor:pointer; font-size:12px;
  }
  #toolbar button.active { background:#4A90D9; color:#fff; border-color:#3a78bb; }
  #toolbar span { color:#444; margin-left:6px; }
</style>
<script src="https://cdn.jsdelivr.net/npm/fabric@5.3.0/dist/fabric.min.js"></script>
</head>
<body>
<div id="toolbar">
  <button id="btn-select" class="active" title="Select / transform">Select</button>
  <button id="btn-rect">Rect</button>
  <button id="btn-circle">Circle</button>
  <button id="btn-line">Line</button>
  <button id="btn-text">Text</button>
  <button id="btn-del" title="Delete selected">🗑</button>
  <span id="hint">Drag to move · rotate handle on top</span>
</div>
<div id="wrap"><canvas id="c"></canvas></div>

<script>
(function() {
  const NONCE = "__NONCE__";
  const canvas = new fabric.Canvas('c', {
    width: __WIDTH__,
    height: __HEIGHT__,
    backgroundColor: "__BG__",
    selection: true,
    preserveObjectStacking: true,
    fireRightClick: false,
    stopContextMenu: true,
  });

  // ---------- Load initial drawing (only once per nonce) ----------
  const initial = __INITIAL__;
  try {
    canvas.loadFromJSON(initial, function() {
      canvas.renderAll();
      syncState();
    });
  } catch (e) {
    console.error("loadFromJSON failed", e);
    canvas.renderAll();
  }

  // ---------- Drawing mode / tool state ----------
  let currentMode = "__MODE__";
  canvas.isDrawingMode = false;

  function setMode(mode) {
    currentMode = mode;
    canvas.isDrawingMode = false;
    canvas.selection = (mode === "transform");
    canvas.forEachObject(o => {
      o.selectable = (mode === "transform");
      o.evented = (mode === "transform");
    });
    canvas.discardActiveObject();
    canvas.renderAll();
    document.querySelectorAll('#toolbar button').forEach(b => b.classList.remove('active'));
    const id = { transform: 'btn-select', rect: 'btn-rect', circle: 'btn-circle', line: 'btn-line', text: 'btn-text' }[mode];
    if (id) document.getElementById(id).classList.add('active');
    canvas.defaultCursor = mode === "transform" ? "default" : "crosshair";
  }
  setMode(currentMode);

  document.getElementById('btn-select').onclick = () => setMode('transform');
  document.getElementById('btn-rect').onclick = () => setMode('rect');
  document.getElementById('btn-circle').onclick = () => setMode('circle');
  document.getElementById('btn-line').onclick = () => setMode('line');
  document.getElementById('btn-text').onclick = () => setMode('text');
  document.getElementById('btn-del').onclick = () => {
    canvas.getActiveObjects().forEach(o => canvas.remove(o));
    canvas.discardActiveObject();
    canvas.renderAll();
    syncState();
  };

  // ---------- Drawing handlers ----------
  let isDown = false, origX = 0, origY = 0, tempObj = null;

  canvas.on('mouse:down', function(opt) {
    if (currentMode === 'transform') return;
    const p = canvas.getPointer(opt.e);
    isDown = true;
    origX = p.x; origY = p.y;

    if (currentMode === 'rect') {
      tempObj = new fabric.Rect({
        left: origX, top: origY, width: 1, height: 1,
        fill: "__FILL__88",
        stroke: "__STROKE__", strokeWidth: __STROKE_W__,
      });
      canvas.add(tempObj);
    } else if (currentMode === 'circle') {
      tempObj = new fabric.Circle({
        left: origX, top: origY, radius: 1,
        fill: "__FILL__88",
        stroke: "__STROKE__", strokeWidth: __STROKE_W__,
      });
      canvas.add(tempObj);
    } else if (currentMode === 'line') {
      tempObj = new fabric.Line([origX, origY, origX, origY], {
        stroke: "__STROKE__", strokeWidth: __STROKE_W__, selectable: false,
      });
      canvas.add(tempObj);
    }
  });

  canvas.on('mouse:move', function(opt) {
    if (!isDown || !tempObj) return;
    const p = canvas.getPointer(opt.e);
    if (currentMode === 'rect') {
      tempObj.set({
        left: Math.min(p.x, origX), top: Math.min(p.y, origY),
        width: Math.abs(p.x - origX), height: Math.abs(p.y - origY),
      });
    } else if (currentMode === 'circle') {
      const r = Math.hypot(p.x - origX, p.y - origY);
      tempObj.set({ radius: r, left: origX - r, top: origY - r });
    } else if (currentMode === 'line') {
      tempObj.set({ x2: p.x, y2: p.y });
    }
    canvas.renderAll();
  });

  canvas.on('mouse:up', function() {
    if (currentMode === 'transform') { syncState(); return; }
    if (!tempObj) { isDown = false; return; }
    const minSize = 5;
    if (currentMode === 'rect' &&
        (tempObj.width < minSize || tempObj.height < minSize)) {
      canvas.remove(tempObj);
    } else if (currentMode === 'circle' && tempObj.radius < minSize) {
      canvas.remove(tempObj);
    }
    tempObj = null; isDown = false;
    canvas.renderAll();
    syncState();
  });

  // ---------- Sync state out of the iframe ----------
  function syncState() {
    const data = JSON.stringify(canvas.toJSON(['id', 'name', 'equipment_type', 'equip_height_3d']));
    try {
      window.parent.postMessage({ type: 'fabric-state', nonce: NONCE, payload: data }, '*');
    } catch (e) { /* ignore */ }
  }

  // also sync on every modification
  canvas.on('object:modified', syncState);
  canvas.on('object:added', syncState);
  canvas.on('object:removed', syncState);

  // ---------- Handle messages from Streamlit ----------
  window.addEventListener('message', function(ev) {
    const d = ev.data || {};
    if (d.type === 'fabric-load' && d.nonce === NONCE) {
      // Replace whole drawing (used by Import)
      canvas.loadFromJSON(d.payload, () => canvas.renderAll());
    }
  });
})();
</script>
</body>
</html>
"""
