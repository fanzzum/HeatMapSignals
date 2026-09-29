# HeatMapSignals

HeatMapSignals is an interactive, real-time 2D heat diffusion simulation built to demonstrate complex Digital Signal Processing (DSP) and Linear Systems concepts. It visually bridges the gap between raw physical models (the Heat Equation) and advanced frequency-domain analysis (Fourier Transforms, Convolution Theorem, and Spatial Filtering).

---

## Features

- **Real-Time Physics Engine:** Accurately simulates the 2D heat equation at 60 FPS, featuring thermodynamic decay (cooling) and boundary heat loss.
- **Interactive Canvas:** Place, drag, and adjust the intensity of multiple heat sources (candles) in real-time.
- **Direct vs. FFT Convolution:** Toggle between raw $\mathcal{O}(N^2 K^2)$ direct spatial convolution and highly-optimized $\mathcal{O}(N \log N)$ FFT-based convolution to immediately feel the computational difference.
- **Frequency Domain Analysis:** Switch to the frequency domain to view the live **Log-Magnitude (Power) Spectrum** or **Phase Spectrum** of the active heat field.
- **Spatial Filtering:** Apply live **High-Pass** (edge detection / ambient heat removal) and **Low-Pass** (spatial blurring) filters to manipulate the heat signals directly in the frequency domain.

---

## Tech Stack

### Frontend
- **React.js** (via Vite)
- **HTML5 Canvas** (for high-performance pixel manipulation and 60 FPS rendering)
- **Vanilla CSS** (custom design system and UI components)

### Backend
- **FastAPI** (Python REST API for serving computation steps)
- **NumPy** (for high-performance matrix operations and 2D Fourier Transforms)

---

## Installation & Setup

You will need both **Node.js** (for the frontend) and **Python 3.8+** (for the DSP backend) installed on your system.

### 1. Clone the repository
```bash
git clone https://github.com/fanzzum/HeatMapSignals.git
cd HeatMapSignals
```

### 2. Start the Python Backend
The backend handles all heavy matrix multiplications, convolutions, and FFTs.
```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn numpy

# Run the API server
npm run api
```
*The backend will start running on `http://127.0.0.1:8000`.*

### 3. Start the React Frontend
In a new terminal window:
```bash
# Install Node modules
npm install

# Start the Vite development server
npm run dev
```
*The web app will open in your browser at `http://localhost:5173`.*

---

## Under the Hood (Signal Processing)

HeatMapSignals treats temperature as a continuous 2D spatial signal $T(x,y,t)$. The spread of heat is modeled mathematically as a **Linear Time-Invariant (LTI) system**. 

- **The Impulse Response:** The fundamental solution to the heat equation is a Gaussian curve. Our application generates a 2D Gaussian kernel to represent how a single point of heat diffuses outward per frame.
- **The Convolution Theorem:** Sliding a 9x9 kernel over a 100x100 grid requires millions of operations per second ($\mathcal{O}(N^2 K^2)$), causing UI lag. By transforming both the grid and the kernel into the frequency domain via 2D FFT, we can multiply them point-by-point and run an Inverse FFT. This drops complexity to $\mathcal{O}(N \log N)$, yielding a $>50\times$ performance increase.
- **Boundary Conditions:** The grid features a Robin/absorbing boundary condition. Heat that reaches the edges naturally escapes the system, preventing thermal runaway and allowing the system to reach an equilibrium.

---

## Authors

**Farhan Anjum** & **Naeem Shuvo**  
*Developed for Signals and Linear Systems*
