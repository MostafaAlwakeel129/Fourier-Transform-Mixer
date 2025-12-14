# """Controller class for handling UI interactions and data flow."""
#
# from typing import Optional, Dict, Any, Literal
# import numpy as np
# import plotly.graph_objs as go
# from models.global_session_state import GlobalSessionState
# from models.image_model import ImageModel
# from utils.unit_unificator import UnitUnificator
#
#
# class Controller:
#     """Handles UI interactions and data flow."""
#
#     def __init__(self):
#         """Initialize Controller with session state and unificator."""
#         self._session: GlobalSessionState = GlobalSessionState()
#         self._unificator: UnitUnificator = UnitUnificator()
#         self._weights: Dict[int, float] = {0: 0.25, 1: 0.25, 2: 0.25, 3: 0.25}
#
#     def handle_upload(self, contents: str, index: int, ft_component: str = 'magnitude') -> Dict[str, Any]:
#         """
#         Handle image uploads.
#
#         Args:
#             contents: Base64 encoded image content
#             index: Index of the viewport where image is uploaded
#
#         Returns:
#                 Handle image uploads and prepare display data.
#                 Returns ALL FT components so the callback can choose which to display.
#         """
#         try:
#             if contents is None:
#                 return {'status': 'error', 'message': 'No content provided'}
#
#             # Create new ImageModel and load from contents
#             image_model = ImageModel() #creates instance of imagemodel (due to image being uploaded)
#             image_model.load_from_contents(contents) #process image and converts go gray scale
#
#             # Store in session
#             self._session.store_image(index, image_model) #stores the current image_model data and its index
#
#             # Enforce unified size across all images
#             self._unificator.enforce_unified_size(self._session) # gets all present image models from globalsessionstate and gets minimum width/height from the created min_shape tuple then STORES the current min shape of all the currently uploaded images then resizes all images.
#
#             raw_image_data = image_model.get_visual_data('raw')
#
#             ft_component_data = image_model.get_visual_data(ft_component)
#
#             if ft_component in ['magnitude', 'real', 'imag']:
#                 ft_component_data = np.log(np.abs(ft_component_data) + 1e-10)
#
#             return {
#             'status': 'success',
#             'message': f'Image {index+1} uploaded successfully',
#             'raw_image_data': raw_image_data.tolist(),
#             'ft_component_data': ft_component_data.tolist(),
#             'ft_component_type': ft_component,
#             'image_shape': image_model.shape,
#             'unified_shape': self._session.get_min_shape()
#         }
#
#         except Exception as e:
#             return {'status': 'error', 'message': str(e)}
#
#     def handle_slider_update(self, val: float, index: int) -> Dict[str, Any]:
#         """
#         Handle updates from sliders.
#
#         Args:
#             val: New slider value (weight)
#             index: Index of the viewport/slider
#
#         Returns:
#             Dictionary with updated value and status
#         """
#         # Slider updates are typically handled by callbacks
#         # This method can be used for validation or preprocessing
#         if val < 0 or val > 1:
#             return {'status': 'error', 'message': 'Weight must be between 0 and 1'}
#
#         self._weights[index] = val
#
#         return {'status': 'success', 'value': val}
#
#     def get_plotting_data(self, index: int, mode: Literal['raw', 'magnitude', 'phase', 'real', 'imag'] = 'raw') -> Optional[go.Figure]:
#         """
#             Retrieve data for plotting when user switches FT component dropdown.
#
#             This is called when user changes the FT component selection,
#             NOT during initial upload (that's handled by handle_upload).
#
#             Args:
#                 index: Index of the image (0-3)
#                 mode: Type of component to display
#
#             Returns:
#                 Numpy array of the requested data with appropriate scaling
#         """
#         image_model = self._session.get_image(index)
#
#         if image_model is None:
#             return None
#
#         try:
#             data = image_model.get_visual_data(mode)
#
#             # Apply log transform for FT components (for visualization)
#           #  if mode in ['magnitude', 'real', 'imag']:
#            #     data = np.log(np.abs(data) + 1e-10)
#
#             return data
#
#         except Exception as e:
#             return None
#
#     def get_session(self) -> GlobalSessionState:
#         """
#         Get the session state.
#
#         Returns:
#             GlobalSessionState instance
#         """
#         return self._session
#
#     def get_all_weights(self) -> Dict[int, float]:
#         """
#         Get all current weights (placeholder - would be managed by callbacks).
#
#         Returns:
#             Dictionary mapping index to weight value
#         """
#         return self._weights.copy()
#
"""Controller class for handling UI interactions and data flow."""

from typing import Optional, Dict, Any, Literal
import numpy as np
import plotly.graph_objs as go
from models.global_session_state import GlobalSessionState
from models.image_model import ImageModel
from utils.unit_unificator import UnitUnificator
from engine.async_job_manager import AsyncJobManager
from utils.region_handler import RegionHandler

class Controller:
    """Handles UI interactions and data flow."""

    def __init__(self):
        """Initialize Controller with session state and unificator."""
        self._session: GlobalSessionState = GlobalSessionState()
        self._unificator: UnitUnificator = UnitUnificator()

        # Initialize AsyncJobManager for threading
        self._job_manager = AsyncJobManager()

        # Track weights for both component groups separately
        # Component 1: Magnitude (or Real)
        # Component 2: Phase (or Imaginary)
        self._weights_comp1: Dict[int, float] = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
        self._weights_comp2: Dict[int, float] = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}

        self._mode: Literal['mag_phase', 'real_imag'] = 'mag_phase'
        self._current_mask: Optional[np.ndarray] = None

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
            image_model = ImageModel()  # creates instance of imagemodel (due to image being uploaded)
            image_model.load_from_contents(contents)  # process image and converts go gray scale

            # Store in session
            self._session.store_image(index, image_model)  # stores the current image_model data and its index

            # Enforce unified size across all images
            self._unificator.enforce_unified_size(
                self._session)  # gets all present image models from globalsessionstate and gets minimum width/height from the created min_shape tuple then STORES the current min shape of all the currently uploaded images then resizes all images.

            # Get visual data (ImageModel handles log transform and normalization internally)
            raw_image_data = image_model.get_visual_data('raw')
            ft_component_data = image_model.get_visual_data(ft_component)

            # Note: We do NOT apply np.log here anymore because get_visual_data() already does it.
            # This prevents the "Double Log" bug.

            return {
                'status': 'success',
                'message': f'Image {index + 1} uploaded successfully',
                'raw_image_data': raw_image_data.tolist(),
                'ft_component_data': ft_component_data.tolist(),
                'ft_component_type': ft_component,
                'image_shape': image_model.shape,
                'unified_shape': self._session.get_min_shape()
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def handle_slider_update(self, val: float, index: int, component_group: str) -> Dict[str, Any]:
        """
        Handle updates from sliders.

        Args:
            val: New slider value (weight)
            index: Index of the viewport/slider
            component_group: Identifier for which set of weights to update ('comp1' or 'comp2')

        Returns:
            Dictionary with updated value and status
        """
        # Slider updates are typically handled by callbacks
        # This method can be used for validation or preprocessing
        if val < 0 or val > 1:
            return {'status': 'error', 'message': 'Weight must be between 0 and 1'}

        # Update the correct weight dictionary
        if component_group == 'comp1':
            self._weights_comp1[index] = val
            self._weights_comp2[index] = 0
        else:
            self._weights_comp2[index] = val
            self._weights_comp1[index] = 0

        # Trigger the async mixing job automatically
        # self.start_mixing_job()

        return {'status': 'success', 'value': val}

    def mix_button_update(self,):
        self.start_mixing_job()

    def start_mixing_job(self):
        """Bundles current state and triggers the Async Job Manager."""
        images = self._session.get_all_images()
        if not images:
            return

        # Prepare inputs dictionary for the MixerEngine
        inputs = {
            'mode': self._mode,
            'weights1': self._weights_comp1.copy(),
            'weights2': self._weights_comp2.copy(),
            'images': images,
            'mask': self._current_mask
        }

        # Fire and forget - polling callbacks will check progress
        self._job_manager.start_mixing_job(inputs, callback=None)

    def update_mixing_mode(self, mode: str):
        """Updates the mixing mode (mag_phase vs real_imag) and restarts mixing."""
        if mode in ['mag_phase', 'real_imag']:
            self._mode = mode
            # self.start_mixing_job()

    def get_plotting_data(self, index: int, mode: Literal['raw', 'magnitude', 'phase', 'real', 'imag'] = 'raw') -> \
    Optional[np.ndarray]:
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
            # Use get_visual_data to ensure consistent brightness/contrast/log-scaling
            data = image_model.get_visual_data(mode)

            return data

        except Exception as e:
            return None

        # In code/controllers/controller.py

    def apply_region_mask(self, rect_coords: Optional[tuple], is_inner: bool = True):
        """
        Generates a mask based on the selected region and triggers mixing.

        Args:
            rect_coords: Tuple (x1, y1, x2, y2) or None if clearing
            is_inner: True for Inner Pass (Low Freq), False for Outer Pass (High Freq)
        """
        # 1. Get the unified shape (needed to build the mask array)
        shape = self._session.get_min_shape()
        if shape is None:
            return

        # 2. Use RegionHandler to create the mathematical mask (0s and 1s)
        handler = RegionHandler()

        self._current_mask = handler.create_mask(shape, rect_coords, is_inner)

        # 3. Automatically restart the mixing job with the new mask
        # self.start_mixing_job()


    def get_session(self) -> GlobalSessionState:
        """
        Get the session state.

        Returns:
            GlobalSessionState instance
        """
        return self._session

    def get_all_weights(self) -> Dict[str, Dict[int, float]]:
        """
        Get all current weights.

        Returns:
            Dictionary containing both weight groups
        """
        return {
            'comp1': self._weights_comp1.copy(),
            'comp2': self._weights_comp2.copy()
        }

    # --- Polling Methods for UI Callbacks ---
    def get_job_progress(self) -> float:
        """Get the progress of the current background job."""
        return self._job_manager.get_progress()

    def get_job_result(self):
        """Get the result of the completed background job."""
        return self._job_manager.get_result()

    def is_processing(self) -> bool:
        """Check if a job is currently running."""
        return self._job_manager.is_job_running()