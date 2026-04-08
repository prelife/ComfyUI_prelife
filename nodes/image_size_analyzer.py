class ImageSizeAnalyzer:
    """
    A node that takes an image input and returns the longer side size and shorter side size as integers.
    """
    
    CATEGORY = "prelife/analysis"
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", {})
            }
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("longer_side", "shorter_side")
    FUNCTION = "analyze_size"
    
    def analyze_size(self, image):
        """
        Analyze the image dimensions and return longer and shorter side sizes.
        
        Args:
            image: A tensor with shape [B, H, W, C] where B is batch size,
                   H is height, W is width, and C is channels.
        
        Returns:
            tuple: (longer_side, shorter_side) as integers
        """
        # Get dimensions from the first image in the batch
        # Image shape is [B, H, W, C]
        height = image.shape[1]
        width = image.shape[2]
        
        # Determine longer and shorter sides
        longer_side = max(height, width)
        shorter_side = min(height, width)
        
        return (longer_side, shorter_side)


# Register the node
NODE_CLASS_MAPPINGS = {
    "ImageSizeAnalyzer": ImageSizeAnalyzer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageSizeAnalyzer": "Image Size Analyzer",
}
