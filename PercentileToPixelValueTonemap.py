import numpy as np
import torch

class PercentileToPixelValueTonemap:
    """
    DiffusionLight Percentile map to pixel value tonemap 
    """
    def __init__(self):
        pass 
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "percentile": ("FLOAT", {
                    "default": 90,
                    "min": 0,
                    "max": 100,
                    "step": 0.01,
                    "round": False,
                    "display": "number",
                    "lazy": True
                }),
                "pixel_value": ("FLOAT", {
                    "default": 0.9,
                    "min": 0,
                    "max": 1,
                    "step": 0.000001,
                    "round": False,
                    "display": "number",
                    "lazy": True
                }),
                "gamma": ("FLOAT", {
                    "default": 2.4,
                    "min": -1000,
                    "max": 1000,
                    "step": 0.01,
                    "round": False,
                    "display": "number",
                    "lazy": True
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)

    FUNCTION = "percentile_to_pixel_value_tonemap"

    def percentile_to_pixel_value_tonemap(self, images, percentile, pixel_value, gamma):
        """
        map percentile of the HDR image to some value for tonemapping
        set gamma to 1.0 to disable gamma correction
        Args:
            images (IMAGE): The input HDR image. #Tensor of image format shape (range 0-1) shape [N, H, W, 3]
            percentile (float): The percentile value to use for tonemapping.
            pixel_value (float): The pixel value to map the percentile to.
            gamma (float): The gamma value to apply during the conversion.
        """
        # apply gamma correction
        if gamma != 1.0:
            images = torch.pow(images, 1.0 / gamma)

        # calculate the percentile value in beach image in batch dimension
        percentile_value = batch_percentile(images, percentile)

        # map the percentile value to the pixel value
        hdr_image = images / percentile_value[:,None,None,None] * pixel_value

        return (hdr_image, )

def batch_percentile(input_tensor: torch.Tensor, percentile: float) -> torch.Tensor:
    """
    input_tensor: shape [b, H, W, 3]
    percentile: scalar float between 0 and 100
    returns: shape [b]
    """
    # Flatten [H, W, 3] -> [-1] per image
    flattened = input_tensor.view(input_tensor.shape[0], -1)  # shape [b, H*W*3]

    # Compute percentile along dimension 1 (per image)
    result = torch.quantile(flattened, percentile / 100.0, dim=1)
    return result
    

