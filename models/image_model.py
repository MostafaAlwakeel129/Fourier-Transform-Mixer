"""ImageModel class representing an individual image and its data."""

import base64
import io
import threading
import numpy as np
from PIL import Image
from typing import Tuple, Optional, Literal


class ImageModel:
    """Represents an individual image and its data."""

    def __init__(self):
        """Initialize ImageModel with empty data and thread lock."""
        self._ndarray_raw_pixels: Optional[np.ndarray] = None
        self._ndarray_complex_arr: Optional[np.ndarray] = None
        self.shape: Tuple[int, ...] = ()

        # Caching attributes
        self._ndarray_cached_magnitude: Optional[np.ndarray] = None
        self._ndarray_cached_phase: Optional[np.ndarray] = None
        self._ndarray_cached_real: Optional[np.ndarray] = None
        self._ndarray_cached_imag: Optional[np.ndarray] = None

        # Thread safety lock
        self._lock = threading.Lock()

    def load_from_contents(self, base64_string: str) -> None:
        """
        Load image data from a base64 string (Thread-Safe).
        """
        # Decode base64 string
        try:
            header, encoded = base64_string.split(',', 1)
            image_data = base64.b64decode(encoded)

            # Load image using PIL
            image = Image.open(io.BytesIO(image_data))

            # Convert to grayscale if needed
            if image.mode != 'L':
                image = image.convert('L')

            with self._lock:
                # Convert to numpy array
                self._ndarray_raw_pixels = np.array(image, dtype=np.float64)
                self.shape = self._ndarray_raw_pixels.shape

                # Reset cached data
                self._reset_cache()

        except Exception as e:
            print(f"Error loading image: {e}")

    def resize(self, target_shape: Tuple[int, ...]) -> None:
        """
        Resize the image to a target shape (Thread-Safe).
        """
        with self._lock:
            if self._ndarray_raw_pixels is None:
                return

            # Resize using PIL
            image = Image.fromarray(self._ndarray_raw_pixels.astype(np.uint8))
            image = image.resize((target_shape[1], target_shape[0]), Image.Resampling.LANCZOS)

            # Update raw pixels and shape
            self._ndarray_raw_pixels = np.array(image, dtype=np.float64)
            self.shape = target_shape

            # Reset cached data
            self._reset_cache()

    def get_data(self, component_type: Literal['raw', 'magnitude', 'phase', 'real', 'imag']) -> np.ndarray:
        """
        Retrieve specific scientific data based on component type (Thread-Safe).
        """
        with self._lock:
            if self._ndarray_raw_pixels is None:
                raise ValueError("No image data loaded")

            if component_type == 'raw':
                return self._ndarray_raw_pixels.copy()

            # Compute FFT if not already computed
            if self._ndarray_complex_arr is None:
                self._compute_fft()

            if component_type == 'magnitude':
                if self._ndarray_cached_magnitude is None:
                    self._ndarray_cached_magnitude = np.abs(self._ndarray_complex_arr)
                return self._ndarray_cached_magnitude.copy()

            elif component_type == 'phase':
                if self._ndarray_cached_phase is None:
                    self._ndarray_cached_phase = np.angle(self._ndarray_complex_arr)
                return self._ndarray_cached_phase.copy()

            elif component_type == 'real':
                if self._ndarray_cached_real is None:
                    self._ndarray_cached_real = np.real(self._ndarray_complex_arr)
                return self._ndarray_cached_real.copy()

            elif component_type == 'imag':
                if self._ndarray_cached_imag is None:
                    self._ndarray_cached_imag = np.imag(self._ndarray_complex_arr)
                return self._ndarray_cached_imag.copy()

            else:
                raise ValueError(f"Unknown component type: {component_type}")

    def get_visual_data(self, component_type: str, brightness: float = 0.0, contrast: float = 1.0) -> np.ndarray:
        """
        Get data adjusted for display purposes (Encapsulated Visualization Logic).

        Args:
            component_type: Type of component to retrieve
            brightness: Offset value (default 0.0)
            contrast: Multiplier value (default 1.0)

        Returns:
            NumPy array normalized to 0-1 range with adjustments applied.
        """
        # 1. Get raw data (thread-safe copy)
        data = self.get_data(component_type)

        # 2. Apply Log Transform for spectral components for better visibility
        if component_type in ['magnitude', 'real', 'imag']:
            # Log transform: log(1 + abs(x))
            data = np.log(np.abs(data) + 1.0)

        # 3. Normalize to 0-1 range
        data_min, data_max = data.min(), data.max()
        if data_max > data_min:
            data = (data - data_min) / (data_max - data_min)
        else:
            data = np.zeros_like(data)

        # 5. Clip to valid display range
        return np.clip(data, 0, 1)

    def _compute_fft(self) -> None:
        """Private method to compute the FFT and shift zero-frequency to center."""
        if self._ndarray_raw_pixels is None:
            raise ValueError("No image data to compute FFT")

        # Compute FFT and immediately shift DC component to the center
        # This matches the Region Selection logic (Inner = Center = Low Freq)
        self._ndarray_complex_arr = np.fft.fftshift(np.fft.fft2(self._ndarray_raw_pixels))

    def _reset_cache(self) -> None:
        """Reset all cached data."""
        self._ndarray_complex_arr = None
        self._ndarray_cached_magnitude = None
        self._ndarray_cached_phase = None
        self._ndarray_cached_real = None
        self._ndarray_cached_imag = None