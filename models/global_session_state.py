"""GlobalSessionState class for managing session-wide image data."""

from typing import Dict, Tuple, List, Optional
from .image_model import ImageModel


class GlobalSessionState:
    """Manages session-wide image data."""
    
    def __init__(self):
        """Initialize GlobalSessionState with empty image dictionary."""
        self._images: Dict[int, ImageModel] = {}
        self._min_shape: Optional[Tuple[int, ...]] = None
    
    def store_image(self, index: int, image_model: ImageModel) -> None:
        """
        Store an ImageModel with a given index.
        
        Args:
            index: Index to store the image at
            image_model: ImageModel instance to store
        """
        self._images[index] = image_model
        # min_shape is managed by UnitUnificator
    
    def get_image(self, index: int) -> Optional[ImageModel]:
        """
        Retrieve an ImageModel by its index.
        
        Args:
            index: Index of the image to retrieve
        
        Returns:
            ImageModel instance if found, None otherwise
        """
        return self._images.get(index)
    
    def get_all_images(self) -> List[ImageModel]:
        """
        Returns all stored ImageModel objects.
        
        Returns:
            List of all ImageModel instances
        """
        return list(self._images.values())
    
    def update_min_shape(self, shape: Tuple[int, ...]) -> None:
        """
        Update the minimum shape of images.
        
        Args:
            shape: New minimum shape tuple
        """
        self._min_shape = shape
    
    def get_min_shape(self) -> Optional[Tuple[int, ...]]:
        """
        Get the current minimum shape.
        
        Returns:
            Minimum shape tuple or None if no images stored
        """
        return self._min_shape
    
    def get_image_count(self) -> int:
        """
        Get the number of stored images.
        
        Returns:
            Number of images in the session
        """
        return len(self._images)
    
    def remove_image(self, index: int) -> None:
        """
        Remove an image from the session.
        
        Args:
            index: Index of the image to remove
        """
        if index in self._images:
            del self._images[index]
            # Clear min_shape if no images remain
            if not self._images:
                self._min_shape = None