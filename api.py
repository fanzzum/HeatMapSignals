import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import numpy as np

from backend.diffusion_model import step
from backend.heat_source import generate_gaussian_source
from backend.kernel import generate_diffusion_kernel
from backend.spatial_convolution import convolve_2d
from backend.frequency_domain import get_power_spectrum
from backend.temperature_field import create_field, get_temperature_at, reset_field

GRID_SIZE = 48
AMBIENT_TEMP = 20.0
# Buffer zone: how far outside the grid a candle can be placed (in grid units)
CANDLE_BUFFER = 12
DEFAULTS = {"diffusion": 0.8, "sigma": 4.5, "cooling": 0.08, "boundary_loss": 0.01, "time_scale": 1.0}


class Simulation:
    def __init__(self):
        self.reset()

    def reset(self):
        self.settings = DEFAULTS.copy()
        self.candles = [{"id": 1, "x": 24.0, "y": 24.0, "intensity": 88.0}]
        self.selected_candle_id = 1
        self.field = create_field(GRID_SIZE, GRID_SIZE, AMBIENT_TEMP)
        self.step_number = 0

    def source_field(self):
        source = np.zeros_like(self.field)
        for candle in self.candles:
            source += generate_gaussian_source(
                GRID_SIZE,
                GRID_SIZE,
                (candle["x"], candle["y"]),
                candle["intensity"],
                self.settings["sigma"],
            )
        return source

    def update(self, payload):
        if payload.get("reset"):
            self.reset()
        self.settings.update({key: float(value) for key, value in payload.get("settings", {}).items() if key in DEFAULTS})
        if "candles" in payload:
            self.candles = [self.clamp_candle(candle) for candle in payload["candles"]]
            if self.candles and self.selected_candle_id not in {candle["id"] for candle in self.candles}:
                self.selected_candle_id = self.candles[0]["id"]
        if "source_position" in payload:
            self.move_candle(self.selected_candle_id, payload["source_position"])
        if "add_candle" in payload:
            candle = self.clamp_candle(payload["add_candle"])
            self.candles.append(candle)
            self.selected_candle_id = candle["id"]
        if "move_candle" in payload:
            move = payload["move_candle"]
            self.move_candle(move["id"], (move["x"], move["y"]))
            self.selected_candle_id = move["id"]
        if "select_candle" in payload:
            self.selected_candle_id = payload["select_candle"]
        if "remove_candle" in payload:
            # Simply remove the candle — the heat field T persists and will
            # naturally cool/diffuse without the source contribution.
            self.candles = [candle for candle in self.candles if candle["id"] != payload["remove_candle"]]
            if self.candles and self.selected_candle_id not in {candle["id"] for candle in self.candles}:
                self.selected_candle_id = self.candles[0]["id"]
        if payload.get("clear_candles"):
            self.candles = []
        if payload.get("running", True):
            source = self.source_field()
            dt = self.settings.get("time_scale", 1.0)
            kernel = generate_diffusion_kernel(self.settings["diffusion"], dt, 7)
            self.field = step(
                self.field, source, kernel, AMBIENT_TEMP,
                self.settings["cooling"],
                self.settings.get("boundary_loss", 0.01),
                dt,
                convolve_2d,
            )
            self.step_number += 1

    @staticmethod
    def clamp_candle(candle):
        """Allow candles within the buffer zone around the grid."""
        lo = -CANDLE_BUFFER
        hi_x = GRID_SIZE - 1.0 + CANDLE_BUFFER
        hi_y = GRID_SIZE - 1.0 + CANDLE_BUFFER
        return {
            "id": candle["id"],
            "x": max(lo, min(hi_x, float(candle["x"]))),
            "y": max(lo, min(hi_y, float(candle["y"]))),
            "intensity": max(0.0, float(candle.get("intensity", 88.0))),
        }

    def move_candle(self, candle_id, position):
        lo = -CANDLE_BUFFER
        hi = GRID_SIZE - 1.0 + CANDLE_BUFFER
        for candle in self.candles:
            if candle["id"] == candle_id:
                candle["x"] = max(lo, min(hi, float(position[0])))
                candle["y"] = max(lo, min(hi, float(position[1])))
                return

    def response(self):
        selected = next((candle for candle in self.candles if candle["id"] == self.selected_candle_id), None)
        selected_x = max(0, min(GRID_SIZE - 1, round(selected["x"]))) if selected else 0
        selected_y = max(0, min(GRID_SIZE - 1, round(selected["y"]))) if selected else 0
        return {
            "field": self.field.tolist(),
            "spectrum": get_power_spectrum(self.field).tolist(),
            "peak": float(np.max(self.field)),
            "minimum": float(np.min(self.field)),
            "average": float(np.mean(self.field)),
            "selected_temperature": get_temperature_at(self.field, selected_x, selected_y) if selected else AMBIENT_TEMP,
            "candles": self.candles,
            "selected_candle_id": self.selected_candle_id,
            "settings": self.settings,
            "step": self.step_number,
            "grid_size": GRID_SIZE,
            "candle_buffer": CANDLE_BUFFER,
        }


simulation = Simulation()


class ApiHandler(BaseHTTPRequestHandler):
    def _send(self, payload, status=200):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(encoded)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/state":
            self._send(simulation.response())
        else:
            self._send({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path != "/api/state":
            self._send({"error": "Not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")
        simulation.update(payload)
        self._send(simulation.response())

    def log_message(self, format, *args):
        pass  # Suppress noisy per-request logging


if __name__ == "__main__":
    print("HeatMap Signals API listening on http://127.0.0.1:8000")
    HTTPServer(("127.0.0.1", 8000), ApiHandler).serve_forever()
