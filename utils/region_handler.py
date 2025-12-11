"""RegionHandler class for handling creation of image masks."""

import numpy as np
from typing import Tuple, Optional, Dict, Any


class RegionHandler:
    """Handles creation of image masks for region selection."""
    
    def __init__(self):
        """Initialize RegionHandler with stored state."""
        self._current_rect_coords: Optional[Tuple[int, int, int, int]] = None
        self._is_inner: bool = True
    
    def set_rectangle_from_plotly(self, relayout_data: Dict[str, Any]) -> bool:
        """
        Extract and store rectangle coordinates from Plotly relayoutData.
        
        This simplifies callbacks - just pass the relayoutData directly!
        
        Args:
            relayout_data: The relayoutData from Plotly Graph callback
        
        Returns:
            True if rectangle was extracted successfully, False otherwise
        
        Example:
            >>> handler = RegionHandler()
            >>> # In callback:
            >>> if handler.set_rectangle_from_plotly(relayout_data):
            >>>     print("Rectangle captured!")
        """
        if relayout_data is None:
            return False
        
        # Check if shapes were drawn
        if 'shapes' in relayout_data and len(relayout_data['shapes']) > 0:
            shape = relayout_data['shapes'][-1]  # Get last drawn shape
            
            if shape['type'] == 'rect':
                # Extract coordinates
                x0 = int(shape['x0'])
                y0 = int(shape['y0'])
                x1 = int(shape['x1'])
                y1 = int(shape['y1'])
                
                # Store as (x1, y1, x2, y2) ensuring min/max order
                self._current_rect_coords = (
                    min(x0, x1),
                    min(y0, y1),
                    max(x0, x1),
                    max(y0, y1)
                )
                return True
        
        return False
    
    def set_region_mode(self, is_inner: bool) -> None:
        """
        Set whether to use inner or outer region.
        
        Args:
            is_inner: True for inner region (low freq), False for outer (high freq)
        
        Example:
            >>> handler.set_region_mode(True)  # Select inner region
        """
        self._is_inner = is_inner
    
    def get_current_rectangle(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the currently stored rectangle coordinates.
        
        Returns:
            Tuple of (x1, y1, x2, y2) or None if no rectangle set
        """
        return self._current_rect_coords
    
    def get_region_mode(self) -> bool:
        """
        Get the current region mode.
        
        Returns:
            True if inner mode, False if outer mode
        """
        return self._is_inner
    
    def has_rectangle(self) -> bool:
        """
        Check if a rectangle has been set.
        
        Returns:
            True if rectangle exists, False otherwise
        """
        return self._current_rect_coords is not None
    
    def clear_rectangle(self) -> None:
        """Clear the stored rectangle coordinates."""
        self._current_rect_coords = None
    
    def create_current_mask(self, shape: Tuple[int, int]) -> np.ndarray:
        """
        Create a mask using the currently stored rectangle and region mode.
        
        This is the SIMPLEST method to use in callbacks - no parameters needed!
        
        Args:
            shape: Shape of the mask (height, width)
        
        Returns:
            NumPy array mask based on stored rectangle and mode
        
        Example:
            >>> handler.set_rectangle_from_plotly(relayout_data)
            >>> handler.set_region_mode(True)
            >>> mask = handler.create_current_mask((256, 256))
        """
        return self.create_mask(shape, self._current_rect_coords, self._is_inner)
    
    def create_mask(self, shape: Tuple[int, int], rect_coords: Optional[Tuple[int, int, int, int]] = None, is_inner: bool = True) -> np.ndarray:
        """
        Create a mask based on shape, rectangular coordinates, and whether it's an inner or outer mask.
        
        The mask is used to select frequency regions in Fourier Transform:
        - Inner mask (is_inner=True): Selects LOW frequencies (center of FT)
        - Outer mask (is_inner=False): Selects HIGH frequencies (edges of FT)
        
        Args:
            shape: Shape of the mask (height, width)
            rect_coords: Optional tuple of (x1, y1, x2, y2) defining rectangular region.
                        If None, returns a mask of all ones (selects everything).
            is_inner: If True, mask is 1 inside the rectangle and 0 outside (low freq).
                     If False, mask is 0 inside the rectangle and 1 outside (high freq).
        
        Returns:
            NumPy array of shape 'shape' with mask values (0 or 1)
        
        Example:
            >>> handler = RegionHandler()
            >>> # Select center 100x100 region (low frequencies)
            >>> mask = handler.create_mask((200, 200), (50, 50, 150, 150), is_inner=True)
            >>> # Select everything EXCEPT center (high frequencies)
            >>> mask = handler.create_mask((200, 200), (50, 50, 150, 150), is_inner=False)
        """
        # If no rectangle specified, select everything
        if rect_coords is None:
            return np.ones(shape, dtype=np.float64)
        
        x1, y1, x2, y2 = rect_coords
        
        # Ensure coordinates are within bounds
        x1 = max(0, min(x1, shape[1] - 1))
        y1 = max(0, min(y1, shape[0] - 1))
        x2 = max(0, min(x2, shape[1] - 1))
        y2 = max(0, min(y2, shape[0] - 1))
        
        # Ensure x1 < x2 and y1 < y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        if is_inner:
            # Inner mask: 1 inside rectangle, 0 outside
            # Start with all zeros, then set rectangle to 1
            mask = np.zeros(shape, dtype=np.float64)
            mask[y1:y2+1, x1:x2+1] = 1.0
        else:
            # Outer mask: 0 inside rectangle, 1 outside
            # Start with all ones, then set rectangle to 0
            mask = np.ones(shape, dtype=np.float64)
            mask[y1:y2+1, x1:x2+1] = 0.0
        
        return mask
    
    def get_rectangle_info(self) -> Dict[str, Any]:
        """
        Get human-readable information about the current rectangle.
        
        Returns:
            Dictionary with rectangle info for display purposes
        
        Example:
            >>> info = handler.get_rectangle_info()
            >>> print(info['description'])
        """
        if self._current_rect_coords is None:
            return {
                'has_rectangle': False,
                'description': 'No region selected (using full image)',
                'mode': 'Inner' if self._is_inner else 'Outer'
            }
        
        x1, y1, x2, y2 = self._current_rect_coords
        width = x2 - x1
        height = y2 - y1
        
        return {
            'has_rectangle': True,
            'coordinates': self._current_rect_coords,
            'width': width,
            'height': height,
            'mode': 'Inner (Low Frequencies)' if self._is_inner else 'Outer (High Frequencies)',
            'description': f'Region: {width}x{height} pixels, Mode: {"Inner" if self._is_inner else "Outer"}'
        }