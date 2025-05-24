import numpy as np
import torch
import cv2
import imageio
import folder_paths

class SaveHDR:
    """
    DiffusionLight SaveHDR class

    """
    def __init__(self):
        pass 
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "hdr_image": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "DiffusionLight"}), 
                "file_extension": (["hdr","npy", "exr"], {"default": "hdr"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)

    FUNCTION = "save_hdr"

    def save_hdr(self, hdr_image, filename_prefix, file_extension):
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, folder_paths.get_output_directory())
        filename = f"{filename_prefix}_{counter:04d}.{file_extension}"
        full_path = f"{full_output_folder}/{filename}"
        print(f"Saving HDR image to {full_path}")
        out_image = hdr_image[0].cpu().numpy().astype(np.float32)
        if file_extension == "npy":
            np.save(full_path, out_image)
        elif file_extension == "hdr":
            imageio.imwrite(full_path, out_image)
        else:
            cv2.imwrite(full_path, out_image)  # save in HDR format
        return (hdr_image, )
    

