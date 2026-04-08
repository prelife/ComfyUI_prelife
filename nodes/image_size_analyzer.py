"""
Image Size Analyzer Node for ComfyUI (V3 API)

A node that takes an image input and returns the longer side size and shorter side size as integers.
"""

from __future__ import annotations

import comfy.node_io as io
from comfy.node_io import ComfyNode, ComfyExtension


class ImageSizeAnalyzer(ComfyNode):
    """
    A node that analyzes image dimensions and returns longer and shorter side sizes.
    
    This node processes images in batch mode, analyzing each image individually
    and returning the dimensions for each one.
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the node schema using V3 API."""
        return io.Schema(
            title="Image Size Analyzer",
            description="Analyzes image dimensions and returns longer and shorter side sizes.",
            category="prelife/analysis",
            inputs={
                "image": io.ImageInput(
                    description="Input image tensor with shape [B, H, W, C]",
                    tooltip="The image to analyze. Can be a single image or a batch of images."
                )
            },
            outputs={
                "longer_side": io.IntOutput(
                    description="The longer side dimension (max of height and width)",
                    tooltip="Returns the maximum dimension for each image in the batch"
                ),
                "shorter_side": io.IntOutput(
                    description="The shorter side dimension (min of height and width)",
                    tooltip="Returns the minimum dimension for each image in the batch"
                )
            }
        )
    
    @classmethod
    def validate_inputs(cls, data: io.NodeInputData) -> io.ValidationError | None:
        """Validate input data before processing."""
        if "image" not in data:
            return io.ValidationError("Missing required 'image' input")
        
        image = data["image"]
        # Validate image tensor shape: should be [B, H, W, C]
        if len(image.shape) != 4:
            return io.ValidationError(
                f"Expected image tensor with shape [B, H, W, C], got shape {image.shape}"
            )
        
        return None
    
    def execute(self, data: io.NodeInputData) -> io.NodeOutputData:
        """
        Execute the node to analyze image dimensions.
        
        Args:
            data: Input data containing the image tensor
            
        Returns:
            Output data with longer_side and shorter_side lists
        """
        image = data["image"]
        
        # Get dimensions from the image tensor
        # Shape is [B, H, W, C]
        batch_size = image.shape[0]
        height = image.shape[1]
        width = image.shape[2]
        
        # Calculate longer and shorter sides
        longer_side = max(height, width)
        shorter_side = min(height, width)
        
        # Return lists to support batch processing
        # Each image in the batch gets the same dimensions (since they're all the same size)
        longer_sides = [longer_side] * batch_size
        shorter_sides = [shorter_side] * batch_size
        
        return {
            "longer_side": longer_sides,
            "shorter_side": shorter_sides
        }


# V3 Entry Point
def comfy_entrypoint() -> ComfyExtension:
    """
    V3 API entry point for ComfyUI.
    
    Returns:
        ComfyExtension instance with registered nodes
    """
    return ComfyExtension(
        name="ComfyUI_prelife",
        version="0.2.0",
        nodes=[
            ImageSizeAnalyzer,
        ]
    )
