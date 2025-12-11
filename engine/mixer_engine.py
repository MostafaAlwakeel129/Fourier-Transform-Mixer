import numpy as np
from typing import Dict, Optional, List, Literal
from models.image_model import ImageModel
from utils.region_handler import RegionHandler

class MixerEngine:
    """Performs image mixing and reconstruction using Fourier Transform components."""
    
    def __init__(self):
        self._region_handler = RegionHandler()

    def _perform_ifft(self, complex_ft: np.ndarray) -> np.ndarray:
        """
        Centralized IFFT method:
        - Undo shift (ifftshift)
        - Compute inverse FFT
        - Return real clipped image
        """
        # Undo shift applied to FFT before masking
        unshifted_ft = np.fft.ifftshift(complex_ft)
        
        # Inverse FFT
        result = np.fft.ifft2(unshifted_ft)
        result = np.real(result)
        result = np.clip(result, 0, 255)
        return result

    def mix_images_mag_phase(
        self, 
        magnitude_sources: Dict[int, float],
        phase_sources: Dict[int, float],
        images: List[ImageModel],
        mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        if not images:
            raise ValueError("No images provided")
        
        shape = images[0].shape
        
        # Mix magnitudes
        mixed_magnitude = np.zeros(shape, dtype=np.float64)
        total_mag_weight = sum(magnitude_sources.values())
        if total_mag_weight > 0:
            for idx, w in magnitude_sources.items():
                if idx < len(images):
                    mixed_magnitude += images[idx].get_visual_data('magnitude') * (w / total_mag_weight)
        else:
            mixed_magnitude = images[0].get_visual_data('magnitude')
        
        # Mix phases
        mixed_phase = np.zeros(shape, dtype=np.float64)
        total_phase_weight = sum(phase_sources.values())
        if total_phase_weight > 0:
            for idx, w in phase_sources.items():
                if idx < len(images):
                    mixed_phase += images[idx].get_visual_data('phase') * (w / total_phase_weight)
        else:
            mixed_phase = images[0].get_visual_data('phase')
        
        # Apply mask to magnitude if provided
        if mask is not None:
            if mask.shape != shape:
                raise ValueError("Mask shape does not match image shape")
            mixed_magnitude *= mask
            # TODO
            # mixed_phase*=mask
        
        # Reconstruct complex
        complex_ft = mixed_magnitude * np.exp(1j * mixed_phase)
        
        # Use centralized IFFT method
        return self._perform_ifft(complex_ft)

    def mix_images_real_imag(
        self,
        real_sources: Dict[int, float],
        imag_sources: Dict[int, float],
        images: List[ImageModel],
        mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        if not images:
            raise ValueError("No images provided")
        
        shape = images[0].shape
        
        # Mix real parts
        mixed_real = np.zeros(shape, dtype=np.float64)
        total_real_weight = sum(real_sources.values())
        if total_real_weight > 0:
            for idx, w in real_sources.items():
                if idx < len(images):
                    mixed_real += images[idx].get_visual_data('real') * (w / total_real_weight)
        else:
            mixed_real = images[0].get_visual_data('real')
        
        # Mix imaginary parts
        mixed_imag = np.zeros(shape, dtype=np.float64)
        total_imag_weight = sum(imag_sources.values())
        if total_imag_weight > 0:
            for idx, w in imag_sources.items():
                if idx < len(images):
                    mixed_imag += images[idx].get_visual_data('imag') * (w / total_imag_weight)
        else:
            mixed_imag = images[0].get_visual_data('imag')
        
        # Apply mask if provided
        if mask is not None:
            if mask.shape != shape:
                raise ValueError("Mask shape does not match image shape")
            mixed_real *= mask
            mixed_imag *= mask
        
        # Reconstruct complex
        complex_ft = mixed_real + 1j * mixed_imag
        
        # Use centralized IFFT method
        return self._perform_ifft(complex_ft)

    def mix_images_unified(
        self,
        mode: Literal['mag_phase', 'real_imag'],
        component1_sources: Dict[int, float],
        component2_sources: Dict[int, float],
        images: List[ImageModel],
        mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        if mode == 'mag_phase':
            return self.mix_images_mag_phase(component1_sources, component2_sources, images, mask)
        elif mode == 'real_imag':
            return self.mix_images_real_imag(component1_sources, component2_sources, images, mask)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def create_region_mask(
        self,
        shape: tuple[int, int],
        rect_coords: Optional[tuple[int, int, int, int]] = None,
        is_inner: bool = True
    ) -> np.ndarray:
        return self._region_handler.create_mask(shape, rect_coords, is_inner)
