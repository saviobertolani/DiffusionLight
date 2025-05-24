import numpy as np
import torch

class Exposure2HDR:
    """
    DiffusionLight Exposure2HDR class

    """
    def __init__(self):
        pass 
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "exposures": ("IMAGE",),
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
                    "default": "0.0,-2.5,-5.0",
                    "lazy": True
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)

    FUNCTION = "exposure_to_hdr"

    def exposure_to_hdr(self, exposures, gamma, ev_values):
        """
        convert multiple image to a single HDR image
        Args:
            exposures (IMAGE): The input environment map image. #Tensor of image format shape (range 0-1) shape [N, H, W, 3]
            lowest_ev (int): The lowest EV value to use for the HDR conversion.
            ev_values (str): A comma-separated string of EV values to use for the HDR conversion. 
        """
        # Assuming envmap is already in the correct format

        ev_values = [float(ev.strip()) for ev in ev_values.split(",")]
        hdr_image = exposure_to_hdr(exposures, gamma, ev_values)[None]
        return (hdr_image, )
    

def exposure_to_hdr(exposures, gamma, evs):
    
    
    scaler = np.array([0.212671, 0.715160, 0.072169])

    
    # inital first image
    image0 = exposures[0]
    image0_linear = torch.pow(image0, gamma)

    # read luminace for every image 
    luminances = []
    for i in range(len(evs)):
        image = exposures[i]
        
        # apply gama correction
        linear_img = torch.pow(image, gamma)
        
        # convert the brighness
        linear_img *= 1 / (2 ** evs[i])
        
        # compute luminace
        lumi = linear_img @ scaler
        luminances.append(lumi)
        
    # start from darkest image
    out_luminace = luminances[len(evs) - 1]
    for i in range(len(evs) - 1, 0, -1):
        # compute mask
        maxval = 1 / (2 ** evs[i-1])
        p1 = torch.clamp((luminances[i-1] - 0.9 * maxval) / (0.1 * maxval), 0, 1)
        p2 = out_luminace > luminances[i-1]
        mask = (p1 * p2).float()
        out_luminace = luminances[i-1] * (1-mask) + out_luminace * mask
        
    hdr_rgb = image0_linear * (out_luminace / (luminances[0] + 1e-10))[:, :, None]

    return hdr_rgb
