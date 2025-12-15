"""UnitUnificator class for ensuring consistent image sizing."""

from typing import List, Tuple
from models.global_session_state import GlobalSessionState
from models.image_model import ImageModel


class UnitUnificator:
    """Ensures consistent image sizing across all images in a session."""
    
    def enforce_unified_size(self, state: GlobalSessionState) -> None:
        """
        Enforce a unified size across images in the given state.
        
        Args:
            state: GlobalSessionState instance containing images
        """
        images = state.get_all_images()
        
        if not images:
            return
        
        # Always recalculate min dimensions from original image sizes
        min_shape = self._find_min_dimensions(images)
        
        # Update state's min_shape
        state.update_min_shape(min_shape)
        
        # Resize all images to minimum dimensions
        for image in images:
            if image.shape != min_shape:
                image.resize(min_shape)
    
    def _find_min_dimensions(self, images: List[ImageModel]) -> Tuple[int, int]:
        """
        Find the minimum dimensions among a set of images.
        Uses ORIGINAL image sizes to allow growing back to larger dimensions.
        
        Args:
            images: List of ImageModel instances
        
        Returns:
            Tuple of (min_height, min_width)
        """
        if not images:
            raise ValueError("Cannot find min dimensions of empty image list")
        
        min_height = float('inf')
        min_width = float('inf')
        
        for img in images:
            # Use original shape if available, otherwise fall back to current shape
            if hasattr(img, '_original_raw_pixels') and img._original_raw_pixels is not None:
                h, w = img._original_raw_pixels.shape
            else:
                h, w = img.shape
            
            min_height = min(min_height, h)
            min_width = min(min_width, w)
        
        return (int(min_height), int(min_width))