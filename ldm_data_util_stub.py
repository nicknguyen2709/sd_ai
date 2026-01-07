"""
Stub module for ldm.data.util providing depth preprocessing utilities
"""
import numpy as np
from PIL import Image


class AddMiDaS:
    """
    Stub implementation for MiDaS depth model preprocessing.
    Converts images to the format expected by MiDaS depth estimation models.
    """
    
    def __init__(self, model_type="dpt_hybrid", keep_in_fp32=True):
        """Initialize MiDaS preprocessor
        
        Args:
            model_type: Type of MiDaS model ("dpt_large", "dpt_hybrid", "midas_v21", "midas_v21_small")
            keep_in_fp32: Whether to keep values in fp32 format
        """
        self.model_type = model_type
        self.keep_in_fp32 = keep_in_fp32
    
    def __call__(self, sample):
        """Process an image sample for MiDaS input
        
        Args:
            sample: Dict with "jpg" key containing image array (H, W, C) with values 0-1 or 0-255
            
        Returns:
            Dict with "midas_in" key containing preprocessed image
        """
        if "jpg" in sample:
            image = sample["jpg"]
        else:
            # Handle case where image is passed directly
            image = sample
        
        # Ensure image is numpy array
        if not isinstance(image, np.ndarray):
            if hasattr(image, 'numpy'):
                image = image.numpy()
            else:
                image = np.array(image)
        
        # Normalize to 0-1 range if needed
        if image.max() > 1.0:
            image = image.astype(np.float32) / 255.0
        else:
            image = image.astype(np.float32)
        
        # Ensure image is in correct format (H, W, C)
        if image.ndim == 2:
            # Grayscale - expand to 3 channels
            image = np.stack([image] * 3, axis=-1)
        elif image.shape[-1] == 4:
            # RGBA - remove alpha channel
            image = image[..., :3]
        elif image.shape[-1] != 3:
            # Wrong number of channels
            raise ValueError(f"Expected image with 1, 3, or 4 channels, got {image.shape[-1]}")
        
        # Convert to tensor-like format (normalized)
        midas_input = image.astype(np.float32)
        
        return {
            "midas_in": midas_input
        }
