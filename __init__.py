"""
ComfyUI Prelife Custom Nodes (V3 API)

This package provides custom nodes for ComfyUI using the modern V3 API.
"""

from .nodes import ImageSizeAnalyzer, comfy_entrypoint

__version__ = "0.2.0"

# V3 API entry point - ComfyUI will call this function automatically
comfy_entrypoint = comfy_entrypoint

__all__ = ["ImageSizeAnalyzer", "comfy_entrypoint", "__version__"]
