"""
Owner: Anjum
Module: temperature_field

Handles the core 2D temperature field data representation.
"""
import numpy as np

def create_field(width: int, height: int, ambient_temp: float = 20.0) -> np.ndarray:
    """
    Creates the initial 2D temperature field.
    
    Args:
        width: The number of columns in the spatial grid.
        height: The number of rows in the spatial grid.
        ambient_temp: The default starting temperature for every cell.
        
    Returns:
        np.ndarray: A 2D floating-point NumPy array of shape (height, width).
        Each element represents the temperature at one sampled spatial location.
        Every initial cell contains the ambient temperature.
    """
    pass

def reset_field(T: np.ndarray, ambient_temp: float = 20.0) -> np.ndarray:
    """
    Resets the current temperature field to the ambient temperature.
    
    Args:
        T: The current temperature field as a 2D NumPy ndarray.
        ambient_temp: The temperature to reset all cells to.
        
    Returns:
        np.ndarray: A 2D floating-point NumPy array with the same shape as the input T.
        Every returned cell represents the reset ambient temperature.
        Contract: Returns a new array.
    """
    pass

def get_temperature_at(T: np.ndarray, x: int, y: int) -> float:
    """
    Retrieves the temperature at a specific grid location.
    
    Args:
        T: The 2D temperature field as a NumPy ndarray.
        x: The column index (spatial x-coordinate).
        y: The row index (spatial y-coordinate).
        
    Returns:
        float: The temperature value at that grid location.
    """
    pass
