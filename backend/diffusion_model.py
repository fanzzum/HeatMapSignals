"""
Owner: Anjum
Module: diffusion_model

Manages the time-evolution of the temperature field, combining the physical 
source, cooling, boundary loss, and heat spreading.
"""
import numpy as np
import math

def apply_temporal_decay(
    T: np.ndarray,
    ambient_temp: float,
    decay_rate: float,
    dt: float
) -> np.ndarray:
    """
    Pulls each cell's temperature toward the ambient temperature over time.
    
    Args:
        T: The current 2D temperature field as a NumPy ndarray.
        ambient_temp: The baseline ambient temperature to decay towards.
        decay_rate: The rate of exponential cooling.
        dt: The time step duration.
        
    Returns:
        np.ndarray: A 2D floating-point NumPy array of exactly the same shape as T.
        The returned field represents the temperature field after temporal cooling 
        toward ambient temperature. The data remains real-valued.
    """
    current_difference = T - ambient_temp
    new_difference = current_difference * math.exp(-dt* decay_rate)
    return ambient_temp + new_difference


def apply_boundary_loss(
    T: np.ndarray,
    loss_rate: float
) -> np.ndarray:
    """
    Reduces the temperature at the edges of the field to model heat leaving the environment.
    
    Args:
        T: The current 2D temperature field as a NumPy ndarray.
        loss_rate: The rate at which heat is lost at the boundaries.
        
    Returns:
        np.ndarray: A 2D floating-point NumPy array of the same shape as T.
        The returned field represents the temperature after boundary heat loss.
        Only the boundary behavior is conceptually affected. The result remains real-valued.
    """
    rows, cols = T.shape
    T[0,:] = T[0,:] * (1-loss_rate)
    T[-1,:] = T[-1,:] * (1-loss_rate)
    T[1:-1,0] = T[1:-1,0] * (1-loss_rate)
    T[1:-1, -1] = T[1:-1, -1] * (1-loss_rate)
    return T



def set_diffusion_coefficient(D: float) -> float:
    """
    Validates and sets the diffusion coefficient.
    
    Args:
        D: A scalar diffusion coefficient. Negative values are invalid.
        
    Returns:
        float: The validated scalar diffusion coefficient, ready to be passed 
        into the diffusion-kernel generation stage.
    """
    if not D<0:
        return float(D)
    return 0.0

def step(
    T: np.ndarray,
    S: np.ndarray,
    kernel: np.ndarray,
    ambient_temp:float,
    decay_rate: float,
    boundary_loss_rate: float,
    dt: float,
    convolve_fn
) -> np.ndarray:
    """
    Performs a single simulation timestep update.
    
    Args:
        T: The current 2D temperature field.
        S: The current 2D candle source array.
        kernel: The spatial diffusion kernel.
        decay_rate: The rate of temporal cooling.
        boundary_loss_rate: The rate of heat loss at the edges.
        dt: The time step duration.
        convolve_fn: A callable that accepts (source_array, kernel_array) and 
                     returns a 2D spread array of exactly the same spatial shape.
                     
    Returns:
        np.ndarray: A 2D floating-point NumPy array of exactly the same shape as T.
        The returned field represents the temperature after one simulation timestep.
        The conceptual update includes source spreading, accumulation, temporal decay, 
        and boundary loss.
    """
    spread = convolve_fn(S, kernel)
    T= (T+spread).copy()
    T = apply_temporal_decay(T, ambient_temp, decay_rate,dt)
    T = apply_boundary_loss(T,boundary_loss_rate)
    return T

def run_simulation(
    T: np.ndarray,
    get_source_fn,
    ambient_temp,
    kernel: np.ndarray,
    decay_rate: float,
    boundary_loss_rate: float,
    dt: float,
    num_steps: int,
    convolve_fn
) -> list[np.ndarray]:
    """
    Runs the simulation over multiple timesteps.
    
    Args:
        T: The initial 2D temperature field.
        get_source_fn: A callable that supplies the 2D source array for each time step.
        kernel: The spatial diffusion kernel.
        decay_rate: The rate of temporal cooling.
        boundary_loss_rate: The rate of heat loss at the edges.
        dt: The time step duration.
        num_steps: The number of simulation steps to generate.
        convolve_fn: A callable that performs the 2D spatial convolution of source and kernel.
        
    Returns:
        list[np.ndarray]: A sequence of 2D floating-point NumPy arrays. 
        Every returned field has the same (height, width) shape.
        Each list element represents the temperature field at one simulation timestep.
        Contract: The initial field T is included as the first element in the returned sequence.
    """
    sim = []
    sim.append(T)
    for i in range(num_steps) :
        T = step(T,get_source_fn(),kernel,ambient_temp,decay_rate,boundary_loss_rate,dt,convolve_fn)
        sim.append(T)
    return sim