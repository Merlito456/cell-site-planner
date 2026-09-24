"""
Realistic Three.js 3D preview.
Each equipment type is built from composed geometry (not just a box).
"""

import json
from equipment_library import EQUIPMENT_LIBRARY


def build_3d_html(objects_2d: list, canvas_w: int, canvas_h: int) -> str:
    scene_data = []
    for obj in objects_2d or []:
        equip_key = obj.get("equipment_type", "custom_box")
        equip = EQUIPMENT_LIBRARY.get(equip_key, EQUIPMENT_LIBRARY["custom_box"])

        w = (obj.get("width") or (obj.get("radius", 0) * 2)) * obj.get("scaleX", 1)
        h = (obj.get("height") or (obj.get("radius", 0) * 2)) * obj.get("scaleY", 1)
        left = obj.get("left", 0)
        top = obj.get("top", 0)

        cx = left + w / 2 - canvas_w / 2
        cz = top + h / 2 - canvas_h / 2

        scene_data.append({
            "kind": obj.get("type", "rect"),
            "name": obj.get("name") or equip["label"],
            "equipment_type": equip_key,
            "detail": equip.get("detail", "box"),
            "width": w,
            "depth": h,
            "height": equip["height_3d"],
            "x": cx,
            "z": cz,
            "angle": obj.get("angle", 0),
            "color": equip["color_3d"],
        })

    data_json = json.dumps(scene_data)

    return _HTML_TEMPLATE.replace("__DATA__", data_json)


_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
    html, body { margin:0; padding:0; overflow:hidden; background:#0f1116; }
    #c { width:100%; height:560px; display:block; }
    .hint {
        position:absolute; top:10px; left:10px; color:#eaeaea;
        font-family: system-ui, sans-serif; font-size:12px;
        background:rgba(0,0,0,0.55); padding:6px 10px; border-radius:6px;
        pointer-events:none; z-index:10;
    }
    .loading {
        position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
        color:#aaa; font-family: system-ui, sans-serif; font-size:14px;
    }
</style>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
</head>
<body>
<div class="hint">Left-drag rotate &nbsp;|&nbsp; Right-drag pan &nbsp;|&nbsp; Scroll zoom</div>
<canvas id="c"></canvas>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// ---------- Renderer ----------
const canvasEl = document.getElementById('c');
const W = canvasEl.clientWidth;
const H = 560;

const renderer = new THREE.WebGLRenderer({
    canvas: canvasEl, antialias: true, alpha: false
});
renderer.setSize(W, H, false);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;

// ---------- Scene ----------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0f1116);
scene.fog = new THREE.Fog(0x0f1116, 900, 2400);

const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// ---------- Camera ----------
const camera = new THREE.PerspectiveCamera(50, W/H, 0.5, 8000);
camera.position.set(420, 320, 520);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI / 2.02;
controls.target.set(0, 15, 0);

// ---------- Lights ----------
const hemi = new THREE.HemisphereLight(0xbfd3ff, 0x1a1a1f, 0.6);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffffff, 2.4);
sun.position.set(300, 500, 260);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 10;
sun.shadow.camera.far = 1500;
sun.shadow.camera.left = -700;
sun.shadow.camera.right = 700;
sun.shadow.camera.top = 700;
sun.shadow.camera.bottom = -700;
sun.shadow.bias = -0.0004;
scene.add(sun);

const fill = new THREE.DirectionalLight(0xaaccff, 0.4);
fill.position.set(-400, 200, -300);
scene.add(fill);

// ---------- Ground ----------
const groundGeo = new THREE.PlaneGeometry(4000, 4000);
const groundMat = new THREE.MeshStandardMaterial({
    color: 0x2a2d34, roughness: 0.95, metalness: 0.0
});
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.02;
ground.receiveShadow = true;
scene.add(ground);

// subtle grid
const grid = new THREE.GridHelper(2000, 100, 0x4a4d55, 0x2e3138);
grid.material.opacity = 0.35;
grid.material.transparent = true;
grid.position.y = 0.01;
scene.add(grid);

// ---------- Materials cache ----------
const matCache = {};
function metal(color, rough = 0.55, met = 0.85) {
    const k = `m_${color}_${rough}_${met}`;
    if (!matCache[k]) {
        matCache[k] = new THREE.MeshStandardMaterial({
            color, roughness: rough, metalness: met
        });
    }
    return matCache[k];
}
function matte(color, rough = 0.9) {
    const k = `f_${color}_${rough}`;
    if (!matCache[k]) {
        matCache[k] = new THREE.MeshStandardMaterial({
            color, roughness: rough, metalness: 0.05
        });
    }
    return matCache[k];
}

// ---------- Group
