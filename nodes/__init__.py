from .image_size_analyzer import ImageSizeAnalyzer

__version__ = "0.1.0"

NODE_CLASS_MAPPINGS = {
    "ImageSizeAnalyzer": ImageSizeAnalyzer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageSizeAnalyzer": "Image Size Analyzer",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "__version__"]
