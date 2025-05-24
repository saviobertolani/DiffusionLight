import numpy as np
import torch

class ExposureBracket:
    """
    DiffusionLight Exposure2HDR class

    """
    def __init__(self):
        pass 
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "hdr_image": ("IMAGE",),
                "gamma": ("FLOAT", {
                    "default": 2.4,
                    "min": -1000,
                    "max": 1000,
                    "step": 0.01,
                    "round": False,
                    "display": "number",
                    "lazy": True
                }),
                "ev_values": ("STRING", {
                    "multiline": False,
                    "default": "0.0,-1.0,-2.0,-3.0,-4.0,-5.0",
                    "lazy": True
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)

    FUNCTION = "exposure_bracket"

    def exposure_bracket(self, hdr_image, gamma, ev_values):
        """
        convert multiple image to a single HDR image
        Args:
            hdr_image (IMAGE): The input environment map image. #Tensor of image format shape (range 0-1) shape [1, H, W, 3]
            gamma (float): The gamma value to apply during the conversion.
            ev_values (str): A comma-separated string of EV values to use for the HDR conversion. 
        """
        # Assuming envmap is already in the correct format

        ev_values = [float(ev.strip()) for ev in ev_values.split(",")]
        output_image = []
        for i, ev in enumerate(ev_values):
            exposure = (hdr_image[0] * (2 ** ev)) ** (1/gamma)
            exposure = torch.clamp(exposure, 0.0, 1.0)
            output_image.append(exposure[None])
        exposures = torch.cat(output_image, dim=0)
        return (exposures, )
    

