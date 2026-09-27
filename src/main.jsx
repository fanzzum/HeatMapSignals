import { StrictMode, useEffect, useRef, useState, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
const DEFAULTS = { diffusion: 2.0, sigma: 4.5, cooling: 0.01, boundary_loss: 0.005, time_scale: 1.5, convolution_mode: 'fft', spectrum_mode: 'power' };
/*
 * Thermal color palette: deep blue (cold) → cyan → green → yellow → orange → red → white (hot).
 * Each stop is [R, G, B].
 */
const THERMAL_STOPS = [
  [10,  15,  60],   // deep navy blue — ambient/cold
  [20,  50, 140],   // dark blue
  [15, 100, 180],   // medium blue
  [10, 160, 200],   // cyan-blue
  [40, 200, 170],   // teal-cyan
  [120, 220, 100],  // yellow-green
  [220, 210,  50],  // yellow
  [245, 160,  30],  // orange
  [230,  70,  30],  // red-orange
  [200,  25,  25],  // deep red
  [255, 200, 180],  // pinkish white — peak hot
];

function colorAt(value, minimum, maximum, spectrum = false) {
  const stops = THERMAL_STOPS;
  const range = Math.max(spectrum ? 0.001 : 10, maximum - minimum);
  const ratio = Math.max(0, Math.min(0.999, (value - minimum) / range));
  const scaled = ratio * (stops.length - 1);
  const index = Math.floor(scaled);
  const fraction = scaled - index;
  const start = stops[index];
  const end = stops[Math.min(stops.length - 1, index + 1)];
  const boost = spectrum ? 1.08 : 1;
  return [
    Math.min(255, (start[0] + (end[0] - start[0]) * fraction) * boost),
    Math.min(255, (start[1] + (end[1] - start[1]) * fraction) * boost),
    Math.min(255, (start[2] + (end[2] - start[2]) * fraction) * boost),
  ];
}

function MatrixCanvas({ matrix, minimum, maximum, spectrum = false, className = '' }) {
  const canvasRef = useRef(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    const source = document.createElement('canvas');
    source.width = matrix[0].length;
    source.height = matrix.length;
    const sourceContext = source.getContext('2d');
    const pixels = sourceContext.createImageData(source.width, source.height);
    matrix.forEach((row, y) => row.forEach((value, x) => {
      const [red, green, blue] = colorAt(value, minimum, maximum, spectrum);
      const offset = (y * source.width + x) * 4;
      pixels.data[offset] = red;
      pixels.data[offset + 1] = green;
      pixels.data[offset + 2] = blue;
      pixels.data[offset + 3] = 255;
    }));
    sourceContext.putImageData(pixels, 0, 0);
    canvas.width = 520;
    canvas.height = 520;
    const context = canvas.getContext('2d');
    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = 'high';
    context.drawImage(source, 0, 0, canvas.width, canvas.height);
  }, [matrix, minimum, maximum, spectrum]);
  return <canvas ref={canvasRef} className={`matrix-canvas ${className}`} aria-label={spectrum ? 'FFT power spectrum' : 'Temperature field'} />;
}

function Candle({ candle, selected, bounds, gridSize, candleBuffer, onSelect, onMove }) {
  const [dragging, setDragging] = useState(null);
  const position = dragging || candle;
  const lo = -candleBuffer;
  const hi = gridSize - 1 + candleBuffer;
  const move = (event) => {
    // Map pixel position to grid coordinates, allowing the candle to go outside the heatmap
    const rawX = ((event.clientX - bounds.left) / bounds.width) * gridSize;
    const rawY = ((event.clientY - bounds.top) / bounds.height) * gridSize;
    const x = Math.max(lo, Math.min(hi, rawX));
    const y = Math.max(lo, Math.min(hi, rawY));
    setDragging({ ...candle, x, y });
    onMove(candle.id, x, y);
  };
  const finish = (event) => {
    if (!dragging) return;
    event.currentTarget.releasePointerCapture(event.pointerId);
    onMove(candle.id, dragging.x, dragging.y);
    setDragging(null);
  };
  // Position percentage: allow overflow outside 0–100% for the outer buffer zone
  const leftPct = ((position.x + 0.5) / gridSize) * 100;
  const topPct = ((position.y + 0.5) / gridSize) * 100;
  return <button className={`candle ${selected ? 'selected' : ''}`} style={{ left: `${leftPct}%`, top: `${topPct}%` }} onPointerDown={(event) => { event.stopPropagation(); onSelect(candle.id); event.currentTarget.setPointerCapture(event.pointerId); setDragging(candle); }} onPointerMove={(event) => { if (dragging) move(event); }} onPointerUp={finish} aria-label={`Candle ${candle.id}`}><span className="flame" /><span className="wick" /><span className="wax" /><span className="candle-base" /></button>;
}

/*
 * Nonlinear slider mapping for cooling rate:
 * First ~80% of slider (0–0.8) maps to cooling 0–0.3
 * Last ~20% (0.8–1.0) maps to cooling 0.3–1.0
 * Uses a piecewise linear mapping.
 */
function sliderToCooling(slider) {
  const s = Number(slider);
  if (s <= 0.8) {
    return (s / 0.8) * 0.3;         // 0→0.8 on slider → 0→0.3 cooling
  }
  return 0.3 + ((s - 0.8) / 0.2) * 0.7; // 0.8→1.0 on slider → 0.3→1.0 cooling
}

function coolingToSlider(cooling) {
  const c = Number(cooling);
  if (c <= 0.3) {
    return (c / 0.3) * 0.8;
  }
  return 0.8 + ((c - 0.3) / 0.7) * 0.2;
}

function App() {
  const [settings, setSettings] = useState(DEFAULTS);
  const [running, setRunning] = useState(true);
  const [state, setState] = useState(null);
  const [fieldBounds, setFieldBounds] = useState({ left: 0, top: 0, width: 1, height: 1 });
  const [probeInfo, setProbeInfo] = useState(null);
  const [viewMode, setViewMode] = useState('spatial');
  const fieldWrapRef = useRef(null);
  const heatmapInnerRef = useRef(null);

  const requestState = useCallback(async (changes = {}) => {
    const response = await fetch('http://127.0.0.1:8000/api/state', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...changes, running }) });
    if (!response.ok) throw new Error('Backend API unavailable');
    setState(await response.json());
  }, [running]);

  useEffect(() => {
    requestState().catch(() => setState(null));
    const timer = window.setInterval(() => { if (running) requestState().catch(() => setState(null)); }, 180);
    return () => window.clearInterval(timer);
  }, [running]);

  useEffect(() => {
    const measure = () => { if (heatmapInnerRef.current) setFieldBounds(heatmapInnerRef.current.getBoundingClientRect()); };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, [state]);

  const gridSize = state?.grid_size || 48;
  const candleBuffer = state?.candle_buffer || 12;

  const updateSetting = (key, value) => {
    const next = { ...settings, [key]: value };
    setSettings(next);
    requestState({ settings: next }).catch(() => setState(null));
  };
  const selectCandle = (id) => requestState({ select_candle: id }).catch(() => setState(null));
  const moveCandle = (id, x, y) => requestState({ move_candle: { id, x, y } }).catch(() => setState(null));
  const addCandle = () => {
    const nextId = Math.max(0, ...state.candles.map((candle) => Number(candle.id))) + 1;
    const offset = state.candles.length * 5;
    requestState({ add_candle: { id: nextId, x: Math.min(gridSize - 1, (gridSize / 2) + offset), y: Math.min(gridSize - 1, (gridSize / 2) + offset), intensity: 72 } }).catch(() => setState(null));
  };
  const removeSelected = () => requestState({ remove_candle: state.selected_candle_id }).catch(() => setState(null));
  const clearCandles = () => requestState({ clear_candles: true }).catch(() => setState(null));
  const updateIntensity = (value) => {
    const candles = state.candles.map((candle) => candle.id === state.selected_candle_id ? { ...candle, intensity: Number(value) } : candle);
    requestState({ candles }).catch(() => setState(null));
  };
  const applyFilter = (type) => requestState({ apply_filter: type }).catch(() => setState(null));
  const reset = () => { setSettings(DEFAULTS); requestState({ reset: true }).catch(() => setState(null)); };

  const handleHeatmapPointerMove = (event) => {
    if (!state) return;
    const rect = fieldWrapRef.current?.getBoundingClientRect();
    if (!rect) return;
    const gx = Math.floor(((event.clientX - rect.left) / rect.width) * gridSize);
    const gy = Math.floor(((event.clientY - rect.top) / rect.height) * gridSize);
    if (gx >= 0 && gx < gridSize && gy >= 0 && gy < gridSize) {
      const temp = state.field[gy]?.[gx];
      const freq = state.spectrum[gy]?.[gx];
      setProbeInfo({ x: gx, y: gy, temp: temp != null ? temp : 0, freq: freq != null ? freq : 0 });
    } else {
      setProbeInfo(null);
    }
  };

  if (!state) return <main className="app-shell loading"><h1>Connecting to simulation backend...</h1><p>Run <code>npm run api</code> in another terminal, then refresh this page.</p></main>;
  const { field, spectrum, peak, minimum, average, selected_temperature: selectedTemp, candles, selected_candle_id: selectedId, step: time, compute_time } = state;
  const spectrumPeak = Math.max(...spectrum.flat());
  const selectedCandle = candles.find((candle) => candle.id === selectedId) || candles[0];

  return <main className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark" /> <span>HEATMAP <b>SIGNALS</b></span></div><div className="status"><span className={`status-dot ${running ? '' : 'paused'}`} /> {running ? 'LIVE SIMULATION' : 'PAUSED'} <span className="divider" /> FIELD {gridSize} × {gridSize}</div></header>
    <section className="intro"><div><p className="eyebrow">2D DIFFUSION MODEL / RUN 01</p><h1>Temperature field</h1><p className="subhead">Spatial diffusion and frequency-domain analysis from the Python numerical model.</p></div><div className="controls"><button className="button primary" onClick={() => setRunning((current) => !current)}>{running ? 'Pause' : 'Resume'} simulation</button><button className="button" onClick={reset}>Reset</button></div></section>
    <section className="workspace">
      <div className="visual-panel"><div className="panel-heading"><div><span className="panel-kicker"><button className={`toggle-btn ${viewMode === 'spatial' ? 'active' : ''}`} onClick={() => setViewMode('spatial')}>SPATIAL FIELD</button> <button className={`toggle-btn ${viewMode === 'frequency' ? 'active' : ''}`} onClick={() => setViewMode('frequency')}>FREQUENCY DOMAIN</button></span><h2>{viewMode === 'spatial' ? 'Heat distribution' : (settings.spectrum_mode === 'power' ? 'Log-Magnitude Spectrum' : 'Phase Spectrum')}</h2></div><span className="step">t = {time.toString().padStart(4, '0')} steps</span></div><div className="heatmap-outer" ref={fieldWrapRef} onPointerMove={handleHeatmapPointerMove} onPointerLeave={() => setProbeInfo(null)}><div className="heatmap-wrap" ref={heatmapInnerRef}><MatrixCanvas matrix={viewMode === 'spatial' ? field : spectrum} minimum={viewMode === 'spatial' ? minimum : 0} maximum={viewMode === 'spatial' ? peak : spectrumPeak} spectrum={viewMode === 'frequency'} />{viewMode === 'spatial' && <div className="candle-layer">{candles.map((candle) => <Candle key={candle.id} candle={candle} selected={candle.id === selectedId} bounds={fieldBounds} gridSize={gridSize} candleBuffer={candleBuffer} onSelect={selectCandle} onMove={moveCandle} />)}</div>}</div><div className="axis axis-x"><span>0</span><span>{gridSize / 2}</span><span>{gridSize}</span></div><div className="axis axis-y"><span>0</span><span>{gridSize / 2}</span><span>{gridSize}</span></div></div><div className="legend">{viewMode === 'spatial' ? <><span>{minimum.toFixed(1)} °C</span><div className="legend-bar" /><span>{peak.toFixed(1)} °C</span><span className="legend-value">AVG {average.toFixed(1)} °C</span></> : <><span>LOW</span><div className="legend-bar spectrum-bar" /><span>HIGH</span><span className="legend-value">CENTER = DC</span></>}</div></div>
      <aside className="sidebar"><div className="metric-grid"><div><span>RANGE</span><strong>{(peak - minimum).toFixed(1)}°</strong></div><div><span>COMPUTE</span><strong>{compute_time ? compute_time.toFixed(1) : 0} ms</strong></div></div><div className="section"><div className="section-title"><span>DSP ENGINE</span></div><label className="row-label"><span>Convolution Method</span><select value={settings.convolution_mode} onChange={(e) => updateSetting('convolution_mode', e.target.value)}><option value="fft">FFT (O(N log N))</option><option value="direct">Direct (O(N²))</option></select></label><label className="row-label"><span>Spectrum View</span><select value={settings.spectrum_mode} onChange={(e) => updateSetting('spectrum_mode', e.target.value)}><option value="power">Magnitude (Power)</option><option value="phase">Phase</option></select></label><div className="mini-actions"><button className={`button ${settings.active_filter === 'highpass' ? 'primary' : ''}`} onClick={() => applyFilter('highpass')}>{settings.active_filter === 'highpass' ? 'High-Pass Active' : 'Apply High-Pass'}</button><button className={`button ${settings.active_filter === 'lowpass' ? 'primary' : ''}`} onClick={() => applyFilter('lowpass')}>{settings.active_filter === 'lowpass' ? 'Low-Pass Active' : 'Apply Low-Pass'}</button></div></div><div className="section"><div className="section-title"><span>PARAMETERS</span><span className="live-label">● BACKEND</span></div><label>Diffusion coefficient <output>{Number(settings.diffusion).toFixed(2)}</output><input type="range" min="0" max="5" step="0.1" value={settings.diffusion} onChange={(event) => updateSetting('diffusion', Number(event.target.value))} /></label><label>Source spread (σ) <output>{Number(settings.sigma).toFixed(1)}</output><input type="range" min="1.5" max="15" step="0.1" value={settings.sigma} onChange={(event) => updateSetting('sigma', Number(event.target.value))} /></label><label>Cooling rate <output>{Number(settings.cooling).toFixed(3)}</output><input type="range" min="0" max="1" step="0.005" value={coolingToSlider(settings.cooling)} onChange={(event) => updateSetting('cooling', sliderToCooling(event.target.value))} /></label><label>Boundary loss <output>{Number(settings.boundary_loss).toFixed(3)}</output><input type="range" min="0" max="0.2" step="0.002" value={settings.boundary_loss} onChange={(event) => updateSetting('boundary_loss', Number(event.target.value))} /></label><label>Time speed <output>{Number(settings.time_scale).toFixed(2)}×</output><input type="range" min="0.1" max="10.0" step="0.1" value={settings.time_scale} onChange={(event) => updateSetting('time_scale', Number(event.target.value))} /></label><div className="mini-actions"><button className="button" onClick={addCandle}>+ Add candle</button><button className="button" onClick={clearCandles}>Clear all</button></div></div><div className="section candle-controls"><div className="section-title"><span>SELECTED CANDLE</span><span>{selectedCandle ? `#${selectedCandle.id}` : 'NONE'}</span></div>{selectedCandle ? <><strong>{selectedTemp.toFixed(2)} °C</strong><label>Intensity <output>{selectedCandle.intensity}</output><input type="range" min="0" max="140" value={selectedCandle.intensity} onChange={(event) => updateIntensity(event.target.value)} /></label><button className="remove-button" onClick={removeSelected}>Remove selected candle</button></> : <small>Add a candle to begin.</small>}</div>{probeInfo && <div className="section probe-readout"><div className="section-title"><span>THERMOMETER</span><span>🌡️</span></div><strong className="probe-temp">{probeInfo.temp.toFixed(2)} °C</strong><div style={{marginTop: '12px', marginBottom: '8px'}}><strong className="probe-freq">{probeInfo.freq.toFixed(4)}</strong><small>Log-Frequency Amp</small></div><small>Grid position ({probeInfo.x}, {probeInfo.y})</small></div>}</aside>
    </section>
    <footer><span>HEAT DIFFUSION / SIGNALS &amp; LINEAR SYSTEMS</span><span>PYTHON / NUMPY · {time} STEPS</span></footer>
  </main>;
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
