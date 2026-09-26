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

    # Use scipy if available for fast convolution, otherwise fall back to
    # numpy FFT-based approach (much faster than the nested Python loop).
    try:
        from scipy.signal import fftconvolve
        result = fftconvolve(field, kernel, mode='same')
        return result
    except ImportError:
        pass

    # FFT-based "same"-mode convolution using only numpy.
    # This is mathematically equivalent to the direct spatial convolution
    # but runs in O(N log N) instead of O(N * K^2).
    full_h = H + kh - 1
    full_w = W + kw - 1
    field_freq = np.fft.rfft2(field, s=(full_h, full_w))
    kernel_freq = np.fft.rfft2(kernel, s=(full_h, full_w))
    full_conv = np.fft.irfft2(field_freq * kernel_freq, s=(full_h, full_w))

    # Extract "same"-sized output (centered on the kernel's anchor)
    start_y = kh // 2
    start_x = kw // 2
    return full_conv[start_y:start_y + H, start_x:start_x + W]