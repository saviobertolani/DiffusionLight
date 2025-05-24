import numpy as np
import torch

class Ball2Envmap:
    """
    DiffusionLight Ball2Envmap class

    """
    def __init__(self):
        pass 

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "chromeball": ("IMAGE",),
                "envmap_height": ("INT", {"default": 256, "min": 1, "max": 8192, "step": 1, "label": "Image Size"}),
                "anti_aliasing": (["1", "2", "4", "8", "16"], {"label": "MSAA Anti-Aliasing Scale", "default": "4"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)

    FUNCTION = "convert"

    def convert(self, chromeball, anti_aliasing="4", envmap_height=256):
        """
        Convert an environment map to a ball2envmap format.

        Args:
            chromeball (IMAGE): The input environment map image. #Tensor of image format shape (range 0-1) shape [1, H, W, 3]

        Returns:
            tuple: A tuple containing the converted image.
        """
        # Assuming envmap is already in the correct format
        msaa_scale = int(anti_aliasing)
        envmap = ball2envmap(chromeball, msaa_scale, envmap_height)
        return (envmap, )
    

# HELPER FUNCTION
def ball2envmap(chromeball, msaa_scale, envmap_height):
    """
    Helper function to convert a chromeball image to an environment map.

    Args:
        chromeball (torch.Tensor): The input chromeball image tensor.

    Returns:
        torch.Tensor: The converted environment map tensor.
    """
    # Assuming the input is already in the correct format

    I = np.array([1,0, 0]) # incoming vector, pointing to the camera
    
    # compute  normal map that create from reflect vector
    env_grid = create_envmap_grid(envmap_height * msaa_scale)   
    reflect_vec = get_cartesian_from_spherical(env_grid[...,1], env_grid[...,0])
    normal = get_normal_vector(I[None,None], reflect_vec)

    # turn from normal map to position to lookup [Range: 0,1]
    pos = (normal + 1.0) / 2
    pos  = 1.0 - pos
    pos = pos[...,1:]

    env_map = None

    # using pytorch method for bilinear interpolation
    with torch.no_grad():
        # convert position to pytorch grid look up
        grid = torch.from_numpy(pos)[None].float()
        grid = grid * 2 - 1 # convert to range [-1,1]

        # convert ball to support pytorch
        ball_image = chromeball.permute(0,3,1,2) # [1,3,H,W]
        envmap = torch.nn.functional.grid_sample(ball_image, grid, mode='bilinear', padding_mode='border', align_corners=True)
        envmap = torch.nn.functional.interpolate(envmap, size=(envmap_height, envmap_height * 2), mode='bilinear', align_corners=False) 
        envmap = envmap.permute(0,2,3,1) # [1,H,W,3]

    return envmap

def create_envmap_grid(size: int):
    """
    BLENDER CONVENSION
    Create the grid of environment map that contain the position in sperical coordinate
    Top left is (0,0) and bottom right is (pi/2, 2pi)
    """    
    
    theta = torch.linspace(0, np.pi * 2, size * 2)
    phi = torch.linspace(0, np.pi, size)
    
    #use indexing 'xy' torch match vision's homework 3
    theta, phi = torch.meshgrid(theta, phi ,indexing='xy') 
    theta_phi = torch.cat([theta[..., None], phi[..., None]], dim=-1)
    theta_phi = theta_phi.numpy()



    return theta_phi

def get_cartesian_from_spherical(theta: np.array, phi: np.array, r = 1.0):
    """
    BLENDER CONVENSION
    theta: vertical angle
    phi: horizontal angle
    r: radius
    """
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return np.concatenate([x[...,None],y[...,None],z[...,None]], axis=-1)

def get_normal_vector(incoming_vector: np.ndarray, reflect_vector: np.ndarray):
    """
    BLENDER CONVENSION
    incoming_vector: the vector from the point to the camera
    reflect_vector: the vector from the point to the light source
    """
    #N = 2(R ⋅ I)R - I
    N = (incoming_vector + reflect_vector) / np.linalg.norm(incoming_vector + reflect_vector, axis=-1, keepdims=True)
    return N

def get_cartesian_from_spherical(theta: np.array, phi: np.array, r = 1.0):
    """
    BLENDER CONVENSION
    theta: vertical angle
    phi: horizontal angle
    r: radius
    """
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return np.concatenate([x[...,None],y[...,None],z[...,None]], axis=-1)
