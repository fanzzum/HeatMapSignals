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
    # The heat equation dU/dt = D * grad^2(U) has, as its fundamental solution
    # (the response to a single point of heat after one timestep), a 2D
    # Gaussian whose variance grows with how much heat has had a chance to
    # spread: sigma^2 = 2 * D * dt. Larger D or a longer dt both widen the
    # Gaussian, which is exactly "greater spatial spreading".
    sigma = np.sqrt(2.0 * diffusion_coefficient * dt)

    centre = (size - 1) / 2.0
    axis = np.arange(size, dtype=np.float64) - centre
    x_grid, y_grid = np.meshgrid(axis, axis)

    if sigma <= 0.0:
        # No time has passed / no diffusivity: heat does not move at all, so
        # the kernel is a discrete point mass (identity under convolution)
        # at the centre pixel rather than a division by zero.
        kernel = np.zeros((size, size), dtype=np.float64)
        row = col = size // 2
        kernel[row, col] = 1.0
        return kernel

    kernel = np.exp(-(x_grid ** 2 + y_grid ** 2) / (2.0 * sigma ** 2))

    # Normalize to sum to 1: convolving with this kernel redistributes the
    # existing heat rather than creating or destroying any of it.
    kernel /= kernel.sum()

    return kernel