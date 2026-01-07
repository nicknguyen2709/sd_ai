"""
Stub module for ldm.modules.midas
This provides minimal functionality for depth model loading without requiring the full midas package.
"""
import os


class MidasAPI:
    """Stub for midas API with model path configuration"""
    
    ISL_PATHS = {
        "dpt_large": "dpt_large-midas-2f21e586.pt",
        "dpt_hybrid": "dpt_hybrid-midas-501f0c75.pt",
        "midas_v21": "midas_v21-f6b98070.pt",
        "midas_v21_small": "midas_v21_small-70d6b9c8.pt",
    }
    
    load_model_inner = None
    
    @staticmethod
    def load_model(model_type):
        """Load a midas model - stub implementation"""
        if MidasAPI.load_model_inner:
            return MidasAPI.load_model_inner(model_type)
        raise RuntimeError(f"Midas model loading not configured. Model type: {model_type}")


# Create the API instance
api = MidasAPI()
