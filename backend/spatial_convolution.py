"""
Owner: Naeem
Module: spatial_convolution

Implements direct spatial convolution.
"""
import numpy as np


def convolve_2d(
    field: np.ndarray,
    kernel: np.ndarray
) -> np.ndarray:
    """
    Computes the 2D spatial convolution of a field with a kernel.

    Args:
        field: A 2D NumPy ndarray representing the source or temperature spatial signal.
        kernel: A 2D NumPy ndarray representing the spatial diffusion response.

    Returns:
        np.ndarray: A 2D NumPy array with the exact same shape as `field`.
        The returned array is the spatial convolution of the two input signals
        under the project's chosen boundary/shape convention.
    """
    field = np.asarray(field, dtype=np.float64)
    kernel = np.asarray(kernel, dtype=np.float64)

    H, W = field.shape
    kh, kw = kernel.shape

    # For pedagogical reasons, if "Direct" is chosen, we purposefully do not 
    # use scipy or FFT to demonstrate the massive O(N^2 K^2) cost compared 
    # to O(N log N) FFT.
    
    # Pad the field to handle boundaries (wrap mode)
    pad_y, pad_x = kh // 2, kw // 2
    padded = np.pad(field, ((pad_y, pad_y), (pad_x, pad_x)), mode='wrap')
    
    result = np.zeros((H, W), dtype=np.float64)
    
    # True direct convolution O(N^2 K^2)
    # This intentionally demonstrates computational expense!
    for y in range(H):
        for x in range(W):
            # Extract region and multiply by kernel (sliding window)
            region = padded[y:y+kh, x:x+kw]
            result[y, x] = np.sum(region * kernel)
            
    return result