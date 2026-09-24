"""
Custom Streamlit component: embedded Fabric.js editor with two-way sync.
The frontend is a single static index.html served from ./fabric_editor_frontend/.
"""

import os
import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "fabric_editor_frontend")

if not os.path.isdir(_FRONTEND_DIR):
    raise RuntimeError(
        f"fabric_editor frontend folder not found at: {_FRONTEND_DIR}\n"
        f"Create it and place index.html inside."
    )

_component_func = components.declare_component("fabric_editor", path=_FRONTEND_DIR)


def fabric_editor(
    initial_drawing: dict,
    reset_nonce: str,
    width: int,
    height: int,
    background: str = "#ffffff",
    key: str = "fabric_editor",
):
    """
    Render the Fabric.js editor. Returns the current canvas JSON
    as a dict (updated live on every edit).
    """
    return _component_func(
        initial_drawing=initial_drawing,
        reset_nonce=reset_nonce,
        width=width,
        height=height,
        background=background,
        key=key,
        default=initial_drawing,
    )
