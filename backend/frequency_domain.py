"""
Owner: Naeem
Module: frequency_domain

Implements Fourier-domain operations, including FFT-based convolution and spectral analysis.
"""
import numpy as np

def compute_fft2(field: np.ndarray) -> np.ndarray:
    """
    Computes the 2D Discrete Fourier Transform of a spatial signal.
    
    Args:
        field: A real-valued 2D NumPy ndarray spatial signal.
        
    Returns:
        np.ndarray: A 2D complex-valued NumPy ndarray with shape exactly 
        matching the input spatial shape. The array contains the 2D discrete 
        Fourier transform / FFT coefficients, representing the signal in the 
        frequency domain.
    """
    return np.fft.fft2(np.asarray(field, dtype=np.float64))

def compute_ifft2(field_freq: np.ndarray) -> np.ndarray:
    """
    Computes the inverse 2D Discrete Fourier Transform.
    
    Args:
        field_freq: A 2D complex-valued NumPy ndarray representing frequency-domain coefficients.
        
    Returns:
        np.ndarray: A 2D real-valued floating-point NumPy ndarray with shape 
        matching the frequency-domain input's 2D dimensions.
        The returned array represents the reconstructed spatial-domain field 
        corresponding to the supplied frequency-domain coefficients.
        Since the physical temperature/source field is real-valued, the returned 
        result is expected to be explicitly real-valued.
    """
    return np.real(np.fft.ifft2(np.asarray(field_freq)))

def convolve_via_fft(
    S: np.ndarray,
    h: np.ndarray
) -> np.ndarray:
    """
    Computes the 2D spatial convolution of a source and kernel using the Convolution Theorem.
    
    Args:
        S: The spatial source signal as a 2D NumPy ndarray.
        h: The spatial diffusion kernel as a 2D NumPy ndarray.
        
    Returns:
        np.ndarray: A 2D real-valued floating-point NumPy array with shape exactly matching `S`.
        The returned value represents the spatial convolution of `S` and `h` performed 
        through the Fourier-domain interpretation. Its mathematical contract is equivalent 
        to the result obtained from direct spatial convolution.
    """
    source = np.asarray(S, dtype=np.float64)
    kernel = np.asarray(h, dtype=np.float64)
    height, width = source.shape
    kernel_height, kernel_width = kernel.shape
    full_shape = (height + kernel_height - 1, width + kernel_width - 1)

    source_freq = np.fft.fft2(source, s=full_shape)
    kernel_freq = np.fft.fft2(kernel, s=full_shape)
    full_convolution = np.real(np.fft.ifft2(source_freq * kernel_freq))
    start_y = kernel_height // 2
    start_x = kernel_width // 2
    return full_convolution[start_y:start_y + height, start_x:start_x + width]

def get_power_spectrum(field: np.ndarray) -> np.ndarray:
    """
    Computes the power spectrum of a spatial field.
    
    Args:
        field: A 2D spatial-domain NumPy ndarray.
        
    Returns:
        np.ndarray: A 2D real-valued NumPy array whose shape corresponds to the 
        input spatial dimensions. The result represents the magnitude-squared 
        Fourier spectrum (power spectrum) to describe the spatial-frequency content.
        The zero-frequency component is placed at the center of the returned array.
    """
    magnitude = np.abs(compute_fft2(field))
    spectrum = np.log1p(magnitude)
    return np.fft.fftshift(spectrum).astype(np.float64)


def get_phase_spectrum(field: np.ndarray) -> np.ndarray:
    """
    Computes the phase spectrum of a spatial field.
    """
    phase = np.angle(compute_fft2(field))
    return np.fft.fftshift(phase).astype(np.float64)


def apply_high_pass(field: np.ndarray, cutoff_radius: float = 5.0) -> np.ndarray:
    """
    Applies a sharp high-pass filter in the frequency domain.
    Removes low frequencies (center of the shifted FFT).
    """
    freq = np.fft.fftshift(compute_fft2(field))
    h, w = freq.shape
    cy, cx = h // 2, w // 2
    y, x = np.ogrid[:h, :w]
    mask = (x - cx)**2 + (y - cy)**2 <= cutoff_radius**2
    freq[mask] = 0.0 # Zero out low frequencies
    return compute_ifft2(np.fft.ifftshift(freq))


def apply_low_pass(field: np.ndarray, cutoff_radius: float = 10.0) -> np.ndarray:
    """
    Applies a sharp low-pass filter in the frequency domain.
    Removes high frequencies (edges of the shifted FFT).
    """
    freq = np.fft.fftshift(compute_fft2(field))
    h, w = freq.shape
    cy, cx = h // 2, w // 2
    y, x = np.ogrid[:h, :w]
    mask = (x - cx)**2 + (y - cy)**2 > cutoff_radius**2
    freq[mask] = 0.0 # Zero out high frequencies
    return compute_ifft2(np.fft.ifftshift(freq))
