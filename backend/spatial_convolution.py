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
    pass
