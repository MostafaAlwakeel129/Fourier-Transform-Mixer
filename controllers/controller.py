"""Controller class for handling UI interactions and data flow."""

from typing import Optional, Dict, Any, Literal
import numpy as np
import plotly.graph_objs as go
from models.global_session_state import GlobalSessionState
from models.image_model import ImageModel
from utils.unit_unificator import UnitUnificator


class Controller:
    """Handles UI interactions and data flow."""
    
    def __init__(self):
        """Initialize Controller with session state and unificator."""
        self._session: GlobalSessionState = GlobalSessionState()
        self._unificator: UnitUnificator = UnitUnificator()
        self._weights: Dict[int, float] = {0: 0.25, 1: 0.25, 2: 0.25, 3: 0.25}
    
    def handle_upload(self, contents: str, index: int, ft_component: str = 'magnitude') -> Dict[str, Any]:
        """
        Handle image uploads.
        
        Args:
            contents: Base64 encoded image content
            index: Index of the viewport where image is uploaded
        
        Returns:
                Handle image uploads and prepare display data.
                Returns ALL FT components so the callback can choose which to display.
        """
        try:
            if contents is None:
                return {'status': 'error', 'message': 'No content provided'}
            
            # Create new ImageModel and load from contents
            image_model = ImageModel() #creates instance of imagemodel (due to image being uploaded)
            image_model.load_from_contents(contents) #process image and converts go gray scale
            
            # Store in session
            self._session.store_image(index, image_model) #stores the current image_model data and its index
            
            # Enforce unified size across all images
            self._unificator.enforce_unified_size(self._session) # gets all present image models from globalsessionstate and gets minimum width/height from the created min_shape tuple then STORES the current min shape of all the currently uploaded images then resizes all images.

            raw_image_data = image_model.get_visual_data('raw')

            ft_component_data = image_model.get_visual_data(ft_component)

            if ft_component in ['magnitude', 'real', 'imag']:
                ft_component_data = np.log(np.abs(ft_component_data) + 1e-10)
            
            return {
            'status': 'success',
            'message': f'Image {index+1} uploaded successfully',
            'raw_image_data': raw_image_data.tolist(),
            'ft_component_data': ft_component_data.tolist(),
            'ft_component_type': ft_component,
            'image_shape': image_model.shape,
            'unified_shape': self._session.get_min_shape()
        }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def handle_slider_update(self, val: float, index: int) -> Dict[str, Any]:
        """
        Handle updates from sliders.
        
        Args:
            val: New slider value (weight)
            index: Index of the viewport/slider
        
        Returns:
            Dictionary with updated value and status
        """
        # Slider updates are typically handled by callbacks
        # This method can be used for validation or preprocessing
        if val < 0 or val > 1:
            return {'status': 'error', 'message': 'Weight must be between 0 and 1'}
        
        self._weights[index] = val
        
        return {'status': 'success', 'value': val}
    
    def get_plotting_data(self, index: int, mode: Literal['raw', 'magnitude', 'phase', 'real', 'imag'] = 'raw') -> Optional[go.Figure]:
        """
            Retrieve data for plotting when user switches FT component dropdown.
    
            This is called when user changes the FT component selection,
            NOT during initial upload (that's handled by handle_upload).
    
            Args:
                index: Index of the image (0-3)
                mode: Type of component to display
    
            Returns:
                Numpy array of the requested data with appropriate scaling
        """
        image_model = self._session.get_image(index)
    
        if image_model is None:
            return None
    
        try:
            data = image_model.get_visual_data(mode)
        
            # Apply log transform for FT components (for visualization)
          #  if mode in ['magnitude', 'real', 'imag']:
           #     data = np.log(np.abs(data) + 1e-10)
        
            return data
    
        except Exception as e:
            return None
    
    def get_session(self) -> GlobalSessionState:
        """
        Get the session state.
        
        Returns:
            GlobalSessionState instance
        """
        return self._session
    
    def get_all_weights(self) -> Dict[int, float]:
        """
        Get all current weights (placeholder - would be managed by callbacks).
        
        Returns:
            Dictionary mapping index to weight value
        """
        return self._weights.copy()

