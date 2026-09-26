"""
Owner: Anjum
Module: heat_source

Handles the creation and representation of the physical heat source (candle).
"""
import numpy as np

def generate_gaussian_source(
    width: int,
    height: int,
    position: tuple[float, float],
    intensity: float,
    sigma: float
) -> np.ndarray:
    """
    Generates the candle heat source signal as a 2D Gaussian distribution.
    
    Args:
        width: The number of columns in the spatial grid.
        height: The number of rows in the spatial grid.
        position: A tuple (x, y) representing the spatial center of the candle.
                  The position may lie outside the grid (negative or > width/height),
                  in which case the Gaussian tail naturally falls off within the grid.
        intensity: The amplitude/strength of the source. Zero intensity means 
                   an all-zero source array.
        sigma: The spatial spread of the heat source.
        
    Returns:
        np.ndarray: A 2D floating-point NumPy array of shape (height, width).
        The array represents the candle source signal, centered around the 
        provided (x, y) position. It is a finite smooth spatial heat source, 
        not a single-pixel impulse. The values are source strengths at each grid point.
    """
    if intensity == 0:
        return np.zeros((height, width), dtype=np.float64)

    # Vectorized computation — much faster than nested Python loops
    js = np.arange(width, dtype=np.float64)   # column indices
    is_ = np.arange(height, dtype=np.float64) # row indices
    dx = js - position[0]          # shape (width,)
    dy = is_ - position[1]         # shape (height,)
    # Outer sum of squared distances: (height, width)
    dist_sq = dy[:, np.newaxis] ** 2 + dx[np.newaxis, :] ** 2
    gaussianSource = intensity * np.exp(-dist_sq / (2.0 * sigma ** 2))
    return gaussianSource
