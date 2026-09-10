"""
Owner: Naeem
Module: kernel

Handles the generation of the spatial heat-diffusion kernel.
"""
import numpy as np

def generate_diffusion_kernel(
    diffusion_coefficient: float,
    dt: float,
    size: int
) -> np.ndarray:
    """
    Generates a spatial diffusion kernel.
    
    Args:
        diffusion_coefficient: The scalar coefficient controlling the rate of spreading.
        dt: The time step duration.
        size: The side length of the square kernel (e.g., resulting in a size x size array).
        
    Returns:
        np.ndarray: A 2D floating-point NumPy array of shape (size, size).
        The result represents the spatial heat-diffusion kernel for the given 
        diffusion coefficient and time step. It dictates how heat is spatially 
        redistributed during one timestep.
        The kernel should be normalized so it represents redistribution of heat without 
        adding or removing it. Increasing the diffusion coefficient corresponds 
        conceptually to greater spatial spreading.
    """
    pass
