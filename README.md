# 🗼 Cell Site Floor Plan Maker

A Streamlit app for planning cell site towers with a 2D drag-and-drop editor
(Fabric.js) and a live 3D preview (Three.js).

## Features
- Cell-site equipment library: lattice/monopole/guyed towers, cabinets, racks,
  19"/23" equipment racks, indoor/outdoor cable ladders, basepads, fences,
  generators, fuel tanks, ATS panels, antennas, RRUs, and custom boxes.
- Drag, rotate, resize, and delete objects (Fabric.js transform mode).
- Draw rectangles, circles, lines, polygons, and text annotations.
- Object renaming and per-object measurement (size in meters, m²).
- Point-to-point distance measurement.
- 3D preview with extruded volumes, lighting, grid, and name labels.
- Save/load full project as JSON.

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
