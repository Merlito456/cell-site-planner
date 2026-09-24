"""
Generates a self-contained Three.js HTML string for the 3D preview.
Extrudes every 2D canvas object into a 3D box (or cylinder for circles).
"""

import json
from equipment_library import EQUIPMENT_LIBRARY


def build_3d_html(objects_2d: list, canvas_w: int, canvas_h: int) -> str:
    scene_data = []

    for obj in objects_2d or []:
        equip_key = obj.get("equipment_type", "custom_box")
        equip = EQUIPMENT_LIBRARY.get(equip_key, EQUIPMENT_LIBRARY["custom_box"])

        w = (obj.get("width") or equip["w"]) * obj.get("scaleX", 1)
        h = (obj.get("height") or equip["h"]) * obj.get("scaleY", 1)
        left = obj.get("left", 0)
        top = obj.get("top", 0)

        # Convert canvas coords (origin = top-left of object bounding box)
        # to a centered coordinate system for Three.js
        cx = left + w / 2 - canvas_w / 2
        cz = top + h / 2 - canvas_h / 2

        scene_data.append({
            "kind": obj.get("type", "rect"),
            "name": obj.get("name") or equip["label"],
            "equipment_type": equip_key,
            "width": w,
            "depth": h,
            "height": equip["height_3d"],
            "x": cx,
            "z": cz,
            "angle": obj.get("angle", 0),
            "color": equip["color_3d"],
        })

    data_json = json.dumps(scene_data)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
    html, body {{ margin:0; padding:0; overflow:hidden; background:#1e1e24; }}
    #c {{ width:100%; height:520px; display:block; }}
    .hint {{
        position:absolute; top:8px; left:8px; color:#ddd;
        font-family: system-ui, sans-serif; font-size:12px;
        background:rgba(0,0,0,0.4); padding:6px 10px; border-radius:6px;
        pointer-events:none;
    }}
</style>
<script type="importmap">
{{
  "imports": {{
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }}
}}
</script>
</head>
<body>
<div class="hint">Left-drag: rotate &nbsp;|&nbsp; Right-drag: pan &nbsp;|&nbsp; Scroll: zoom</div>
<canvas id="c"></canvas>
<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

const container = document.getElementById('c');
const W = container.clientWidth;
const H = 520;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1e1e24);

const camera = new THREE.PerspectiveCamera(55, W/H, 0.1, 5000);
camera.position.set(400, 350, 500);

const renderer = new THREE.WebGLRenderer({{ canvas: container, antialias: true }});
renderer.setSize(W, H, false);
renderer.setPixelRatio(window.devicePixelRatio);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 0, 0);

// Lighting
scene.add(new THREE.AmbientLight(0xffffff, 0.7));
const dir = new THREE.DirectionalLight(0xffffff, 1.0);
dir.position.set(300, 500, 200);
scene.add(dir);
const dir2 = new THREE.DirectionalLight(0xffffff, 0.35);
dir2.position.set(-300, 300, -200);
scene.add(dir2);

// Ground grid
const grid = new THREE.GridHelper(2000, 100, 0x555555, 0x333333);
grid.position.y = 0;
scene.add(grid);

// Ground plane
const planeGeo = new THREE.PlaneGeometry(2000, 2000);
const planeMat = new THREE.MeshLambertMaterial({{ color: 0x2a2a30, side: THREE.DoubleSide }});
const plane = new THREE.Mesh(planeGeo, planeMat);
plane.rotation.x = -Math.PI / 2;
plane.position.y = -0.01;
scene.add(plane);

// Equipment
const items = {data_json};
const meshes = [];

function makeLabel(text) {{
    const c = document.createElement('canvas');
    c.width = 256; c.height = 64;
    const ctx = c.getContext('2d');
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(0,0,256,64);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 22px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text.substring(0, 22), 128, 32);
    const tex = new THREE.CanvasTexture(c);
    const mat = new THREE.SpriteMaterial({{ map: tex, depthTest: false }});
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(40, 10, 1);
    return sprite;
}}

items.forEach(it => {{
    let geo;
    if (it.kind === 'circle') {{
        geo = new THREE.CylinderGeometry(it.width/2, it.width/2, it.height, 32);
    }} else {{
        geo = new THREE.BoxGeometry(it.width, it.height, it.depth);
    }}
    const mat = new THREE.MeshLambertMaterial({{ color: it.color }});
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(it.x, it.height / 2, it.z);
    mesh.rotation.y = -it.angle * Math.PI / 180;
    scene.add(mesh);
    meshes.push(mesh);

    const label = makeLabel(it.name);
    label.position.set(it.x, it.height + 8, it.z);
    scene.add(label);
}});

function animate() {{
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}}
animate();

window.addEventListener('resize', () => {{
    const w = container.clientWidth;
    camera.aspect = w / H;
    camera.updateProjectionMatrix();
    renderer.setSize(w, H, false);
}});
</script>
</body>
</html>
"""
