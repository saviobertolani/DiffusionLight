import torch
import torch.nn.functional as F

class PadBlackBorder:
    """
    DiffusionLight PadBlackBorder class

    """
    def __init__(self):
        pass 
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "height": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1, "label": "Image Height"}),
                "width": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1, "label": "Image Width"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)

    FUNCTION = "pad_black_border"

    def pad_black_border(self, image, height=1024, width=1024):
        """
        Resize and pad an image to the desired size while maintaining aspect ratio.
        Args:
            image (IMAGE): The input image tensor of shape [B, H, W, 3].
            height (int): Desired height of the output image.
            width (int): Desired width of the output image. 
        Returns:
            tuple: A tuple containing the padded image tensor of shape [B, height, width, 3].
        """
        # Assuming envmap is already in the correct format
        padded_image = torch_pad_image(image, desired_size=(height, width))
        return (padded_image, )
    

def torch_pad_image(images, desired_size=(1024, 1024)):
    """
    Resize and pad a batch of images [B, H, W, 3] to the desired square size while maintaining aspect ratio.
    Args:
        images (torch.Tensor): Tensor of shape [B, H, W, 3], values in [0, 1] or [0, 255].
        desired_size (tuple): (height, width), e.g. (1024, 1024)
    Returns:
        torch.Tensor: Tensor of shape [B, desired_size[0], desired_size[1], 3]
    """
    assert images.dim() == 4 and images.size(-1) == 3, "Input must be [B, H, W, 3]"
    B, H, W, C = images.shape

    # Convert to [B, 3, H, W]
    images = images.permute(0, 3, 1, 2)

    # Calculate new sizes
    scale = torch.minimum(
        torch.tensor(desired_size[0] / H, dtype=torch.float32),
        torch.tensor(desired_size[1] / W, dtype=torch.float32),
    )
    new_H = int(H * scale)
    new_W = int(W * scale)

    resized = F.interpolate(images, size=(new_H, new_W), mode='bilinear', align_corners=False)

    # Create black canvas
    padded = torch.zeros((B, 3, desired_size[0], desired_size[1]), dtype=images.dtype, device=images.device)

    # Calculate offsets for centering
    top = (desired_size[0] - new_H) // 2
    left = (desired_size[1] - new_W) // 2

    padded[:, :, top:top+new_H, left:left+new_W] = resized

    # Convert back to [B, H, W, 3]
    return padded.permute(0, 2, 3, 1)