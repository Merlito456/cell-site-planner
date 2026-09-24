"""
Custom Streamlit component: embedded Fabric.js editor with two-way sync.
"""

import os
import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
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
    Render the Fabric.js editor and return the current canvas JSON as a dict.
    The component reruns Streamlit on every edit (add / remove / modify).
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
