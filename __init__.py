from .Ball2Envmap import Ball2Envmap
from .Exposure2HDR import Exposure2HDR
from .SaveHDR import SaveHDR
from .ExposureBracket import ExposureBracket
# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "DiffusionLightBall2Envmap": Ball2Envmap,
    "DiffusionLightExposure2HDR": Exposure2HDR,
    "DiffusionLightSaveHDR": SaveHDR,
    "DiffusionLightExposureBracket": ExposureBracket
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "DiffusionLightBall2Envmap": "Ball2Envmap",
    "DiffusionLightExposure2HDR": "Exposure2HDR",
    "DiffusionLightSaveHDR": "SaveHDR",
    "DiffusionLightExposureBracket": "ExposureBracket"
}


__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']