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

        # respect per-object override, fall back to catalog default
        height_3d = float(obj.get("equip_height_3d", equip["height_3d"]))

        scene_data.append({
            "kind": obj.get("type", "rect"),
            "name": obj.get("name") or equip["label"],
            "equipment_type": equip_key,
            "detail": equip.get("detail", "box"),
            "width": w,
            "depth": h,
            "height": height_3d,
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

// ---------- Helpers ----------
function addMesh(parent, geo, mat, x, y, z, rx = 0, ry = 0, rz = 0) {
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    m.rotation.set(rx, ry, rz);
    m.castShadow = true;
    m.receiveShadow = true;
    parent.add(m);
    return m;
}

// ---------- Builders ----------
function buildLattice(w, d, h, color) {
    const g = new THREE.Group();
    const steelMat = metal(color, 0.45, 0.9);
    const legT = Math.max(w * 0.035, 1.2);
    const legGeo = new THREE.BoxGeometry(legT, h, legT);

    const xInset = w * 0.34;
    const zInset = d * 0.34;
    const legPositions = [
        [-xInset, -zInset], [ xInset, -zInset],
        [-xInset,  zInset], [ xInset,  zInset],
    ];
    for (const [x, z] of legPositions) {
        addMesh(g, legGeo, steelMat, x, h / 2, z);
    }

    const braceThickness = legT * 0.6;
    const braceGeoX = new THREE.BoxGeometry(w * 0.68, braceThickness, braceThickness);
    const braceGeoZ = new THREE.BoxGeometry(braceThickness, braceThickness, d * 0.68);
    const levels = 8;
    for (let i = 1; i < levels; i++) {
        const y = (h / levels) * i;
        addMesh(g, braceGeoX, steelMat, 0, y, -zInset);
        addMesh(g, braceGeoX, steelMat, 0, y,  zInset);
        addMesh(g, braceGeoZ, steelMat, -xInset, y, 0);
        addMesh(g, braceGeoZ, steelMat,  xInset, y, 0);
    }

    const diagLen = Math.hypot(w * 0.68, h / levels);
    const diagGeo = new THREE.BoxGeometry(diagLen, braceThickness * 0.7, braceThickness * 0.7);
    const angle = Math.atan2(h / levels, w * 0.68);
    for (let i = 0; i < levels - 1; i++) {
        const y0 = (h / levels) * i + (h / levels) / 2;
        const m1 = addMesh(g, diagGeo, steelMat, 0, y0, -zInset);
        m1.rotation.z =  angle;
        const m2 = addMesh(g, diagGeo, steelMat, 0, y0, -zInset);
        m2.rotation.z = -angle;
    }
    return g;
}

function buildMonopole(w, h, color) {
    const g = new THREE.Group();
    const r = w * 0.28;
    const geo = new THREE.CylinderGeometry(r * 0.55, r, h, 24, 1, false);
    addMesh(g, geo, metal(color, 0.4, 0.9), 0, h / 2, 0);

    addMesh(
        g,
        new THREE.BoxGeometry(w * 0.9, 0.4, w * 0.9),
        metal(0x333333, 0.6, 0.9),
        0, 0.2, 0
    );

    for (let i = 1; i <= 4; i++) {
        const y = (h / 5) * i;
        const rr = r * (1 - (y / h) * 0.45);
        addMesh(
            g,
            new THREE.CylinderGeometry(rr + 0.3, rr + 0.3, 0.3, 20),
            metal(0x222222, 0.5, 0.9),
            0, y, 0
        );
    }
    return g;
}

function buildGuyed(w, h, color) {
    const g = new THREE.Group();
    const r = w * 0.22;
    const tower = new THREE.Mesh(
        new THREE.CylinderGeometry(r * 0.4, r, h, 16),
        metal(color, 0.45, 0.9)
    );
    tower.position.y = h / 2;
    tower.castShadow = true;
    g.add(tower);

    const wireMat = new THREE.LineBasicMaterial({ color: 0x888888 });
    const radius = w * 2.4;
    for (let a = 0; a < 6; a++) {
        const ang = (a / 6) * Math.PI * 2;
        const pts = [
            new THREE.Vector3(0, h * 0.98, 0),
            new THREE.Vector3(Math.cos(ang) * radius, 0, Math.sin(ang) * radius)
        ];
        g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), wireMat));
    }
    return g;
}

function buildPole(w, h, color) {
    const g = new THREE.Group();
    const geo = new THREE.CylinderGeometry(w * 0.12, w * 0.15, h, 16);
    addMesh(g, geo, metal(color, 0.4, 0.85), 0, h / 2, 0);
    addMesh(
        g,
        new THREE.BoxGeometry(w * 0.6, 0.15, w * 0.6),
        metal(0x333333, 0.6, 0.9),
        0, 0.07, 0
    );
    return g;
}

function buildCabinet(w, d, h, color) {
    const g = new THREE.Group();
    const bodyMat = metal(color, 0.55, 0.55);
    const trimMat = metal(0x3a3a3a, 0.6, 0.7);
    const body = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), bodyMat);
    body.position.y = h / 2 + 0.15;
    body.castShadow = true;
    body.receiveShadow = true;
    g.add(body);

    addMesh(g, new THREE.BoxGeometry(w + 2, 0.3, d + 2), trimMat, 0, 0.15, 0);
    addMesh(g, new THREE.BoxGeometry(0.3, h * 0.9, 0.3), trimMat, 0, h / 2 + 0.15, d / 2 + 0.02);

    for (const side of [-1, 1]) {
        for (const t of [0.3, 0.7]) {
            addMesh(
                g,
                new THREE.BoxGeometry(0.6, 1.2, 0.4),
                trimMat,
                side * (w / 2 - 1.5), 0.15 + h * t, d / 2 + 0.05
            );
        }
    }
    for (let i = 0; i < 6; i++) {
        addMesh(
            g,
            new THREE.BoxGeometry(w * 0.55, 0.35, 0.2),
            trimMat,
            0, h * 0.15 + i * 0.9, d / 2 + 0.06
        );
    }
    addMesh(
        g,
        new THREE.BoxGeometry(w + 1.2, 0.35, d + 1.2),
        trimMat,
        0, 0.15 + h + 0.15, 0
    );
    return g;
}

function buildRack(w, d, h, color) {
    const g = new THREE.Group();
    const frameMat = metal(color, 0.5, 0.6);
    const accentMat = metal(0x1a1a1a, 0.55, 0.5);

    addMesh(g, new THREE.BoxGeometry(w, h, d), frameMat, 0, h / 2, 0);

    const front = new THREE.Mesh(
        new THREE.BoxGeometry(w * 0.92, h * 0.94, 0.3),
        accentMat
    );
    front.position.set(0, h / 2, d / 2 + 0.16);
    front.castShadow = true;
    g.add(front);

    const units = Math.floor(h / 1.2);
    for (let i = 0; i < units; i++) {
        const y = 0.6 + i * 1.15;
        if (y + 0.6 > h - 0.1) break;
        addMesh(
            g,
            new THREE.BoxGeometry(w * 0.85, 0.75, 0.15),
            metal(0x3a3a3a, 0.6, 0.5),
            0, y, d / 2 + 0.33
        );
        addMesh(
            g,
            new THREE.BoxGeometry(0.35, 0.2, 0.1),
            new THREE.MeshStandardMaterial({
                color: 0x4ade80, emissive: 0x22aa55, emissiveIntensity: 1.4
            }),
            w * 0.32, y, d / 2 + 0.42
        );
    }
    return g;
}

function buildLadder(w, d, h, color) {
    const g = new THREE.Group();
    const railMat = metal(color, 0.5, 0.85);
    const railT = Math.max(d * 0.18, 0.6);
    const rail1 = new THREE.Mesh(new THREE.BoxGeometry(w, railT, railT), railMat);
    rail1.position.set(0, h + railT / 2, -d / 2 + railT / 2);
    rail1.castShadow = true;
    g.add(rail1);

    const rail2 = rail1.clone();
    rail2.position.z = d / 2 - railT / 2;
    g.add(rail2);

    const step = Math.max(w / 14, 6);
    for (let x = -w / 2 + step; x <= w / 2 - step; x += step) {
        addMesh(
            g,
            new THREE.BoxGeometry(railT * 0.6, railT * 0.6, d - railT * 2),
            railMat,
            x, h + railT / 2, 0
        );
    }
    return g;
}

function buildBasepad(w, d, h, color) {
    const g = new THREE.Group();
    const slab = new THREE.Mesh(
        new THREE.BoxGeometry(w, h, d),
        matte(color, 0.95)
    );
    slab.position.y = h / 2;
    slab.receiveShadow = true;
    slab.castShadow = true;
    g.add(slab);
    return g;
}

function buildFence(w, d, h, color) {
    const g = new THREE.Group();
    const postMat = metal(color, 0.6, 0.7);
    const meshMat = new THREE.MeshStandardMaterial({
        color: 0xcccccc, roughness: 0.8, metalness: 0.4,
        transparent: true, opacity: 0.35, side: THREE.DoubleSide
    });

    const postGeo = new THREE.BoxGeometry(0.5, h, 0.5);
    const postEvery = 20;
    const nX = Math.max(1, Math.floor(w / postEvery));
    const nZ = Math.max(1, Math.floor(d / postEvery));

    for (let i = 0; i <= nX; i++) {
        const x = -w / 2 + (i / nX) * w;
        for (const z of [-d / 2, d / 2]) {
            addMesh(g, postGeo, postMat, x, h / 2, z);
        }
    }
    for (let i = 0; i <= nZ; i++) {
        const z = -d / 2 + (i / nZ) * d;
        for (const x of [-w / 2, w / 2]) {
            addMesh(g, postGeo, postMat, x, h / 2, z);
        }
    }
    const panelH = h * 0.95;
    const front = new THREE.Mesh(new THREE.PlaneGeometry(w, panelH), meshMat);
    front.position.set(0, panelH / 2, -d / 2);
    g.add(front);
    const back = front.clone();
    back.position.z = d / 2;
    g.add(back);
    const left = new THREE.Mesh(new THREE.PlaneGeometry(d, panelH), meshMat);
    left.rotation.y = Math.PI / 2;
    left.position.set(-w / 2, panelH / 2, 0);
    g.add(left);
    const right = left.clone();
    right.position.x = w / 2;
    g.add(right);
    return g;
}

function buildGenerator(w, d, h, color) {
    const g = new THREE.Group();
    const bodyMat = metal(color, 0.55, 0.35);
    const darkMat = metal(0x1f1f1f, 0.6, 0.5);

    addMesh(g, new THREE.BoxGeometry(w * 1.02, 0.2, d * 1.02), darkMat, 0, 0.1, 0);

    const enclosure = new THREE.Mesh(
        new THREE.BoxGeometry(w, h * 0.85, d), bodyMat
    );
    enclosure.position.y = 0.2 + (h * 0.85) / 2;
    enclosure.castShadow = true;
    enclosure.receiveShadow = true;
    g.add(enclosure);

    const roof = new THREE.Mesh(
        new THREE.CylinderGeometry(d * 0.5, d * 0.5, w, 16, 1, false, 0, Math.PI),
        bodyMat
    );
    roof.rotation.z = Math.PI / 2;
    roof.position.set(0, 0.2 + h * 0.85, 0);
    roof.scale.y = 0.6;
    roof.castShadow = true;
    g.add(roof);

    for (let i = 0; i < 5; i++) {
        addMesh(
            g,
            new THREE.BoxGeometry(0.3, h * 0.6, d * 0.8),
            darkMat,
            w / 2 - 0.6 - i * 1.6, 0.2 + h * 0.45, 0
        );
    }

    const exhaust = new THREE.Mesh(
        new THREE.CylinderGeometry(0.5, 0.5, h * 0.9, 12),
        darkMat
    );
    exhaust.position.set(-w * 0.3, 0.2 + h * 0.85 + h * 0.35, -d * 0.25);
    exhaust.castShadow = true;
    g.add(exhaust);

    addMesh(
        g,
        new THREE.BoxGeometry(w * 0.22, h * 0.35, 0.2),
        darkMat,
        w * 0.35, 0.2 + h * 0.5, d / 2 + 0.12
    );
    return g;
}

function buildFuelTank(w, d, h, color) {
    const g = new THREE.Group();
    const r = Math.min(w, d) / 2;
    const length = Math.max(w, d);
    const tankMat = metal(color, 0.55, 0.7);

    const along = w >= d ? "x" : "z";
    const body = new THREE.Mesh(
        new THREE.CylinderGeometry(r, r, length, 32),
        tankMat
    );
    if (along === "x") body.rotation.z = Math.PI / 2;
    else body.rotation.x = Math.PI / 2;
    body.position.y = h / 2;
    body.castShadow = true;
    body.receiveShadow = true;
    g.add(body);

    for (const s of [-1, 1]) {
        const cap = new THREE.Mesh(new THREE.SphereGeometry(r, 24, 16), tankMat);
        cap.position.set(along === "x" ? s * length / 2 : 0, h / 2,
                         along === "z" ? s * length / 2 : 0);
        cap.castShadow = true;
        g.add(cap);
    }

    const saddleMat = metal(0x3a3a3a, 0.7, 0.4);
    for (const x of [-length * 0.3, length * 0.3]) {
        addMesh(
            g,
            new THREE.BoxGeometry(2, h * 0.4, r * 1.6),
            saddleMat,
            along === "x" ? x : 0, h * 0.2,
            along === "z" ? x : 0
        );
    }

    addMesh(
        g,
        new THREE.CylinderGeometry(0.8, 0.8, 1.2, 12),
        metal(0x222222, 0.6, 0.6),
        0, h + 0.4, 0
    );
    return g;
}

function buildATS(w, d, h, color) {
    const g = new THREE.Group();
    addMesh(g, new THREE.BoxGeometry(w, h, d), metal(color, 0.55, 0.4), 0, h / 2, 0);
    const colors = [0x4ade80, 0xfbbf24, 0xef4444];
    for (let i = 0; i < 3; i++) {
        addMesh(
            g,
            new THREE.CylinderGeometry(0.3, 0.3, 0.15, 12),
            new THREE.MeshStandardMaterial({
                color: colors[i], emissive: colors[i], emissiveIntensity: 1.4
            }),
            -w * 0.25 + i * w * 0.25, h * 0.6, d / 2 + 0.05,
            Math.PI / 2, 0, 0
        );
    }
    addMesh(
        g,
        new THREE.BoxGeometry(w * 0.7, h * 0.15, 0.2),
        metal(0x111111, 0.5, 0.4),
        0, h * 0.25, d / 2 + 0.1
    );
    return g;
}

function buildAntenna(w, d, h, color) {
    const g = new THREE.Group();
    const panelMat = new THREE.MeshStandardMaterial({
        color, roughness: 0.5, metalness: 0.2
    });
    const backMat = metal(0x666666, 0.5, 0.7);

    const thickness = Math.max(w, d);
    const panel = new THREE.Mesh(
        new THREE.BoxGeometry(thickness, h, thickness * 0.6),
        panelMat
    );
    panel.position.y = h / 2;
    panel.castShadow = true;
    g.add(panel);

    addMesh(
        g,
        new THREE.BoxGeometry(thickness * 1.2, h * 0.15, thickness * 0.9),
        backMat,
        0, h * 0.5, -thickness * 0.4
    );
    addMesh(
        g,
        new THREE.BoxGeometry(thickness * 1.2, h * 0.15, thickness * 0.9),
        backMat,
        0, h * 0.85, -thickness * 0.4
    );
    return g;
}

function buildRRU(w, d, h, color) {
    const g = new THREE.Group();
    const bodyMat = metal(color, 0.5, 0.55);
    const ribMat = metal(0x2a2a2a, 0.6, 0.4);

    const t = Math.max(w, d);
    const body = new THREE.Mesh(
        new THREE.BoxGeometry(t, h, t * 0.55), bodyMat
    );
    body.position.y = h / 2;
    body.castShadow = true;
    g.add(body);

    const fins = 7;
    for (let i = 0; i < fins; i++) {
        addMesh(
            g,
            new THREE.BoxGeometry(t * 0.9, 0.06, 0.15),
            ribMat,
            0, h * 0.15 + i * (h * 0.7 / fins), t * 0.28
        );
    }
    addMesh(
        g,
        new THREE.CylinderGeometry(0.15, 0.15, 0.2, 8),
        metal(0x111111, 0.5, 0.6),
        -t * 0.25, h * 0.1, t * 0.3, Math.PI / 2, 0, 0
    );
    return g;
}

function buildBox(w, d, h, color) {
    const g = new THREE.Group();
    const m = new THREE.Mesh(
        new THREE.BoxGeometry(w, h, d),
        matte(color, 0.85)
    );
    m.position.y = h / 2;
    m.castShadow = true;
    m.receiveShadow = true;
    g.add(m);
    return g;
}

// ---------- Dispatch ----------
function buildObject(it) {
    const {detail, width, depth, height, color} = it;
    switch (detail) {
        case "lattice":    return buildLattice(width, depth, height, color);
        case "monopole":   return buildMonopole(width, height, color);
        case "guyed":      return buildGuyed(width, height, color);
        case "pole":       return buildPole(width, height, color);
        case "cabinet":    return buildCabinet(width, depth, height, color);
        case "rack":       return buildRack(width, depth, height, color);
        case "ladder":     return buildLadder(width, depth, height, color);
        case "basepad":    return buildBasepad(width, depth, height, color);
        case "fence":      return buildFence(width, depth, height, color);
        case "generator":  return buildGenerator(width, depth, height, color);
        case "fuel_tank":  return buildFuelTank(width, depth, height, color);
        case "ats":        return buildATS(width, depth, height, color);
        case "antenna":    return buildAntenna(width, depth, height, color);
        case "rru":        return buildRRU(width, depth, height, color);
        default:           return buildBox(width, depth, height, color);
    }
}

// ---------- Labels ----------
function makeLabel(text) {
    const c = document.createElement('canvas');
    c.width = 512; c.height = 128;
    const ctx = c.getContext('2d');
    ctx.fillStyle = 'rgba(15,17,22,0.85)';
    ctx.fillRect(0,0,512,128);
    ctx.strokeStyle = '#5a5f68';
    ctx.lineWidth = 3;
    ctx.strokeRect(2,2,508,124);
    ctx.fillStyle = '#f0f0f0';
    ctx.font = 'bold 42px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText((text || '').substring(0, 24), 256, 64);
    const tex = new THREE.CanvasTexture(c);
    tex.colorSpace = THREE.SRGBColorSpace;
    const mat = new THREE.SpriteMaterial({
        map: tex, depthTest: false, transparent: true
    });
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(60, 15, 1);
    return sprite;
}

// ---------- Build scene ----------
const items = __DATA__;

if (items.length > 0) {
    let maxDim = 200;
    items.forEach(it => {
        maxDim = Math.max(maxDim,
            Math.abs(it.x) + it.width,
            Math.abs(it.z) + it.depth,
            it.height * 1.2);
    });
    const dist = maxDim * 1.6;
    camera.position.set(dist * 0.9, dist * 0.7, dist * 1.0);
    controls.target.set(0, Math.min(20, maxDim * 0.15), 0);
    controls.update();
}

items.forEach(it => {
    const group = buildObject(it);
    group.position.set(it.x, 0, it.z);
    group.rotation.y = -it.angle * Math.PI / 180;
    scene.add(group);

    const labelY = Math.max(it.height + 6, 8);
    const label = makeLabel(it.name);
    label.position.set(it.x, labelY, it.z);
    scene.add(label);
});

// ---------- Resize ----------
function onResize() {
    const w = canvasEl.clientWidth;
    camera.aspect = w / H;
    camera.updateProjectionMatrix();
    renderer.setSize(w, H, false);
}
window.addEventListener('resize', onResize);

// ---------- Loop ----------
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();
</script>
</body>
</html>
"""
