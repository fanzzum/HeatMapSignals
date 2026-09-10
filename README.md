# Interactive 2D Heat Diffusion Simulation

## 1. Project Overview
This project simulates the spreading of heat over time in a 2D environment. It is primarily a Signals and Linear Systems application, applying concepts like convolution and frequency-domain analysis to model the diffusion of heat from a localized source (a candle). The backend provides a pure mathematical and signal-processing core, uncoupled from any UI or web framework.

## 2. Mathematical Model
The system models temperature as a discretized two-dimensional spatial signal $T(x, y, t)$ that evolves in discrete time steps. At every time step, heat from the candle is spread via spatial convolution, accumulated into the temperature field, and then subjected to cooling (decay) and edge effects (boundary loss).

## 3. What the 2D Temperature Signal Represents
The core data structure is a 2D floating-point grid (NumPy array). Each cell corresponds to a sampled physical location in space. The value inside the cell is the temperature at that location.

## 4. Candle Heat Source
The candle is not a single hot point; it is a finite, smooth 2D Gaussian distribution. This provides a physically plausible source of heat. The intensity sets how strong the heat is, and the spread (sigma) dictates how wide the flame's footprint is.

## 5. Diffusion Kernel
The diffusion kernel represents the natural physical spreading of heat. Given a specific diffusion coefficient and time step, the kernel is a small 2D array that dictates exactly what percentage of heat moves to neighboring cells. 

## 6. Convolution
Convolution is the central operation that physically spreads the heat. The candle source is the "input signal," and the diffusion kernel is the "system impulse response." Convolving the two yields a new 2D array where the heat has been properly dispersed according to the diffusion coefficient.

## 7. Time Evolution
The simulation steps forward iteratively. In a single update step:
1. The heat source is spread via convolution.
2. The newly spread heat is added to the current temperature field.
3. The entire field undergoes temporal cooling.
4. Edge boundary losses are applied.

## 8. Heat Decay
To model natural cooling, the entire temperature field slowly decays toward the baseline ambient temperature based on an exponential rate.

## 9. Boundary Heat Loss
Cells at the very edge of the simulated environment lose heat to the outside world, preventing the overall system from overheating and preventing heat from reflecting back inwards unphysically.

## 10. Fourier-Domain Representation
Because spatial signals can be analyzed as sums of frequencies, the project explores the frequency-domain representation of the temperature field via the 2D Discrete Fourier Transform. The power spectrum reveals the spatial frequencies present in the heat distribution.

## 11. FFT-Based Convolution
By the Convolution Theorem, convolution in the spatial domain is equivalent to element-wise multiplication in the frequency domain. Transforming the source and the kernel via FFT, multiplying them, and performing the inverse FFT achieves the identical spreading effect as direct spatial convolution, often with high computational efficiency.

## 12. How Anjum's Modules Connect to Naeem's Modules
Anjum manages the physical model (the temperature arrays and the physics-based update steps). Naeem manages the mathematical machinery for convolution and Fourier analysis.

The central connection point is the **convolution callable** passed into Anjum's `step()` and `run_simulation()` functions. Anjum provides the `source_array` and the `kernel_array`. Naeem's functions (`convolve_2d` or `convolve_via_fft`) perform the spreading and return the `spread_array`. Anjum's code accumulates this `spread_array` without needing to know if the calculation happened via direct summation or FFTs.

## 13. Backend Data Flow
- **Initialization**: Create the initial temperature field.
- **Each Step**:
  - `generate_gaussian_source()` -> `S`
  - `generate_diffusion_kernel()` -> `h`
  - `convolve_fn(S, h)` -> `spread`
  - `T = T + spread`
  - `T = apply_temporal_decay(T)`
  - `T = apply_boundary_loss(T)`

## 14. Function-by-Function Implementation Checklist

### Anjum
- [ ] `create_field`: Initialize a NumPy array filled with ambient temperature.
- [ ] `reset_field`: Re-fill an existing array with the ambient temperature.
- [ ] `get_temperature_at`: Return the value at a specific (x, y) index.
- [ ] `generate_gaussian_source`: Compute a 2D Gaussian mathematical formula over a grid of coordinates.
- [ ] `apply_temporal_decay`: Apply an exponential decay formula pulling values toward the ambient baseline.
- [ ] `apply_boundary_loss`: Identify edge indices in the 2D array and reduce their temperatures.
- [ ] `set_diffusion_coefficient`: Ensure the input number is not negative.
- [ ] `step`: Call the convolution function, add the result to the field, then apply decay and boundary loss sequentially.
- [ ] `run_simulation`: Loop over the specified number of steps, calling `step()` repeatedly and saving a snapshot of the field each time.

### Naeem
- [ ] `generate_diffusion_kernel`: Compute the heat equation's fundamental Gaussian solution on a small grid, then normalize it so all values sum to 1.
- [ ] `convolve_2d`: Use a library function (like `scipy.signal.fftconvolve` or `scipy.ndimage.convolve`) to perform direct 2D spatial convolution.
- [ ] `compute_fft2`: Apply the 2D FFT to the input real field.
- [ ] `compute_ifft2`: Apply the 2D Inverse FFT to the complex frequency field, taking the real part as the result.
- [ ] `convolve_via_fft`: Pad the small kernel to match the source's dimensions, transform both via FFT, multiply them element-wise, and inverse transform the result.
- [ ] `get_power_spectrum`: Compute the magnitude squared of the 2D FFT, and apply an FFT shift to center the zero-frequency component.

## 15. Testing Checklist
- Validate array dimensions match contracts precisely.
- Validate types (e.g., ensuring physical fields are strictly real-valued floats).
- Verify setting the candle intensity to 0 yields an empty array.
- Verify that `convolve_2d` and `convolve_via_fft` return nearly identical numerical results.

## 16. Suggested Implementation Order
1. Build the data representations: `create_field`, `generate_gaussian_source`, `generate_diffusion_kernel`.
2. Implement direct spatial convolution: `convolve_2d`.
3. Link them together in `step` without decay/loss to verify basic heat spreading.
4. Add physical realism: `apply_temporal_decay`, `apply_boundary_loss`.
5. Implement the frequency domain logic: `compute_fft2`, `compute_ifft2`.
6. Replace direct convolution with `convolve_via_fft` and ensure the simulation continues to work exactly the same.
7. Compute and analyze the `get_power_spectrum`.

## 17. Core Mathematical Concepts to Review

### For Anjum (Physical Model & Time Evolution):
- **NumPy basics**: 2D arrays, indexing, array-wide math operations.
- **Continuous vs Discrete**: How a continuous function $T(x,y)$ becomes a sampled grid.
- **Gaussian functions**: How the parameters (center, intensity, spread) control the shape.
- **Discrete-time updates**: Implementing difference equations (updating a state variable iteratively).
- **Exponential decay**: Newton's Law of Cooling concepts.
- **Boundary conditions**: Basic array slicing to isolate edges.
- **Convolution concept**: High level intuition of spreading a source with a kernel.

### For Naeem (Signal Processing & Frequency Domain):
- **1D and 2D Discrete Convolution**: The intuition of sliding a weighted kernel over a matrix.
- **Fourier Transforms**: Converting spatial signals to spatial-frequency representations, DFT and FFT.
- **Complex Numbers in NumPy**: Managing real and imaginary components returned by FFTs.
- **Convolution Theorem**: The mathematical principle that spatial convolution equals frequency-domain multiplication.
- **Zero-Padding**: Ensuring the kernel has the same pixel resolution and dimensions as the source before doing FFT multiplication.
- **Power Spectrum**: Computing magnitude from complex frequency coefficients and shifting the DC term to the center.
