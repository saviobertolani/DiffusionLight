import torch
import torch.nn.functional as F

class ChromeballMask:
    """
    DiffusionLight ChromeballMask class

    """
    def __init__(self):
        pass 
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "height": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1, "label": "Image Height"}),
                "width": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1, "label": "Image Width"}),
                "ball_size": ("INT", {"default": 256, "min": 1, "max": 8192, "step": 1, "label": "Ball Size"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)

    FUNCTION = "chromeball_mask"

    def chromeball_mask(self, height=1024, width=1024, ball_size=256):
        """
        Resize and pad an image to the desired size while maintaining aspect ratio.
        Args:
            height (int): Desired height of the output image.
            width (int): Desired width of the output image. 
            ball_size (int): Size of the ball mask to be applied.
        Returns:
            tuple: A tuple containing the padded image tensor of shape [B, height, width, 3].
        """
        # Assuming envmap is already in the correct format
        mask = get_circle_mask(size=ball_size)
        big_mask = torch.zeros((height, width), dtype=torch.bool, device=mask.device)
        h_start = (height - ball_size) // 2
        w_start = (width - ball_size) // 2
        big_mask[h_start:h_start + ball_size, w_start:w_start + ball_size] = mask
        big_mask = big_mask.unsqueeze(0).unsqueeze(-1)  # Add batch and channel dimensions
        padded_image = big_mask.float()
        padded_image = padded_image.repeat(1, 1, 1, 3)
        return (padded_image, )

def get_circle_mask(size=256):
    x = torch.linspace(-1, 1, size)
    y = torch.linspace(1, -1, size)
    y, x = torch.meshgrid(y, x)
    z = (1 - x**2 - y**2)
    mask = z >= 0
    return mask 
