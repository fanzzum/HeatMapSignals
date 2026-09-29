# HeatMapSignals Presentation Script

**Target Time:** ~3.5 to 4 minutes (approx. 25-30 seconds per slide)
**Presenters:** Farhan Anjum & Naeem Shuvo

---

## Slide 1: Title Slide (0:00 - 0:15)
*“Hello everyone. Today, Naeem and I will present our project, **HeatMapSignals**. We’re taking a classic physics problem—heat diffusion—and showing how it is fundamentally a 2D digital signal processing problem.”*

---

## Slide 2: Heat as a 2D Spatial Signal (0:15 - 0:45)
*“Let's start with how we represent heat. Instead of continuous physical space, we map temperature onto a 2D grid. The temperature field is simply a sampled 2D signal, $T(x,y,t)$, where each pixel stores an amplitude representing the heat at that spot.*

*In our simulation, we step forward in time frame-by-frame. For every frame, four things happen: we add heat from active sources (like candles), diffuse that heat outward, let the environment cool down, and account for heat escaping the edges.”*

---

## Slide 3: Thermodynamic Decay & Boundary Loss (0:45 - 1:15)
*“Let's look at the cooling and boundary steps. The cooling process isn't just a flat subtraction; it follows Newton's Law of Cooling, which is an exponential decay. The temperature approaches the ambient room temperature over time.*

*At the same time, we apply a boundary loss condition. This acts as an absorbing boundary where heat that reaches the very edge of our grid literally escapes the system, multiplying the edge pixels by a loss rate. These two factors ensure the system reaches a stable equilibrium.”*

---

## Slide 4: Why a Gaussian Kernel? (1:15 - 1:40)
*“Now for the diffusion step. How exactly does heat spread mathematically? The fundamental solution to the 2D heat equation—its impulse response—is a 2D Gaussian function.*

*Just like dropping ink in water creates a blurry circle, a point of heat naturally spreads outward in a bell-curve shape. This is our kernel.”*

---

## Slide 5: Convolution: How Heat Spreads (1:40 - 2:05)
*“To apply this spread to the entire board, we use 2D spatial convolution. We take that Gaussian kernel and slide it over every single pixel on our grid.* 

*If there's heat at a pixel, the kernel redistributes it to its neighbors. The result of this $S * h$ convolution is our next frame of the simulation.”*

---

## Slide 6: Why Fourier Transform? (2:05 - 2:25)
*“But there’s a problem: sliding that kernel over thousands of pixels is extremely computationally expensive. To solve this, we jump from the Spatial Domain to the Frequency Domain using the 2D Fast Fourier Transform (FFT).”*

---

## Slide 7: Direct Convolution vs. FFT Convolution (2:25 - 3:00)
*“Here is why we do that. For our 100x100 grid, doing standard spatial convolution requires sliding a 100-element kernel over 10,000 pixels. That’s 1 million operations per frame, causing massive lag.*

*By using the FFT, we bring the complexity down from $O(N^2)$ to $O(N \log N)$. This drops the operation count down to roughly 132,000—giving us a massive 50-times speedup. The simulation goes from incredibly choppy to perfectly smooth at 60 frames per second.”*

---

## Slide 8: The Convolution Theorem (3:00 - 3:20)
*“The math that makes this speedup possible is the Convolution Theorem. It states that convolution in the spatial domain is mathematically identical to pointwise multiplication in the frequency domain.*

*So, we take the 2D FFT of our heat grid, multiply it by the FFT of our kernel, and run an Inverse FFT to bring it back to the screen. It is an amazing mathematical cheat code.”*

---

## Slide 9: Frequency-Domain Filtering (3:20 - 3:50)
*“Finally, since we are already in the frequency domain, we can apply filters!* 

*If we apply a Low-pass filter, it smooths out all the sharp details, mimicking heat diffusion. In fact, heat diffusion itself behaves exactly as a spatial low-pass process.* 

*If we apply a High-pass filter, we cut out all the ambient low-frequency background heat, leaving only the high-frequency sharp edges, acting as an edge detector for our candles.* 

*Thank you! We'd now be happy to answer any questions.”*
