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

    # True convolution flips the kernel in both axes before sliding it
    # (as opposed to cross-correlation, which does not flip).
    flipped = kernel[::-1, ::-1]

    # "Same"-shape output: zero-pad the field so the kernel's centre can
    # visit every original pixel, including near the borders. For an
    # odd-sized kernel this pad is symmetric; for an even-sized kernel the
    # extra pixel goes on the trailing edge, matching NumPy/​SciPy's
    # "same"-mode convention.
    pad_top = kh // 2
    pad_bottom = kh - 1 - pad_top
    pad_left = kw // 2
    pad_right = kw - 1 - pad_left
    padded = np.pad(
        field,
        ((pad_top, pad_bottom), (pad_left, pad_right)),
        mode="constant",
        constant_values=0.0,
    )

    result = np.zeros((H, W), dtype=np.float64)
    for r in range(H):
        for c in range(W):
            window = padded[r:r + kh, c:c + kw]
            result[r, c] = np.sum(window * flipped)

    return result