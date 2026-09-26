import os
import sys
import cv2
import time
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import HARPipeline, load_config
from src.gui.video_panel import VideoPanel
from PyQt6.QtWidgets import QApplication

# Initialize QApplication to allow VideoPanel to be created
app_qt = QApplication(sys.argv)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DummySignal:
    def __init__(self, callback):
        self.callback = callback
    def emit(self, *args, **kwargs):
        self.callback(*args, **kwargs)

class WebGUIAdapter:
    def __init__(self):
        self.is_pipeline_running = True
        
        class TimelinePanel:
            def setup_steps(self, steps): pass
            def update_state(self, *args): pass
        self.timeline_panel = TimelinePanel()
        
        class LogPanel:
            def set_logger(self, logger): pass
        self.log_panel = LogPanel()
        
        class HealthPanel:
            def update_pipeline_status(self, status): pass
            def update_recording_status(self, is_rec, duration=0): pass
            def update_fps(self, fps): 
                global_state["health"]["fps"] = fps
            def update_latency(self, latency):
                global_state["health"]["latency"] = latency
        self.health_panel = HealthPanel()
        
        self.update_frame_signal = DummySignal(self._on_frame)
        self.update_alert_signal = DummySignal(self._on_alert)
        self.update_log_signal = DummySignal(self._on_log)
        self.update_timeline_signal = DummySignal(self._on_timeline)
        self.update_metrics_signal = DummySignal(self._on_metrics)
        
        self.video_drawer = VideoPanel()
        
    def _on_frame(self, frame, detections, hand_states, interactions, current_step):
        if frame is not None:
            annotated = frame.copy()
            annotated = self.video_drawer._draw_hud_frame(annotated)
            if detections:
                annotated = self.video_drawer._draw_detections(annotated, detections)
            if hand_states:
                annotated = self.video_drawer._draw_hands(annotated, hand_states)
            if interactions:
                annotated = self.video_drawer._draw_interactions(annotated, interactions)
            if current_step:
                annotated = self.video_drawer._draw_step_overlay(annotated, current_step)
            
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ret:
                global_state["latest_frame"] = buffer.tobytes()

        # Update detections globally for WS
        global_state["experiment"]["currentStepId"] = str(current_step)
        
        # Serialize detections for frontend
        dets = []
        for d in (detections or []):
            dets.append({
                "class_name": d.class_name,
                "confidence": d.confidence,
                "bbox": d.bbox if hasattr(d, 'bbox') else None
            })
        global_state["detections"] = dets

    def _on_alert(self, severity, message):
        global_state["alerts"].append({"severity": severity, "message": message, "timestamp": time.time()})
        if len(global_state["alerts"]) > 50:
            global_state["alerts"].pop(0)

    def _on_log(self, event):
        global_state["logs"].append(event)
        if len(global_state["logs"]) > 100:
            global_state["logs"].pop(0)

    def _on_timeline(self, current_step, completed, next_suggestion, progress):
        global_state["experiment"]["currentStepId"] = str(current_step)
        global_state["experiment"]["completedStepIds"] = list(completed)
        global_state["experiment"]["nextStepId"] = str(next_suggestion)
        global_state["experiment"]["progress"] = progress

    def _on_metrics(self, confidence):
        global_state["experiment"]["confidence"] = confidence

# Global state to share between pipeline and FastAPI
global_state = {
    "latest_frame": None,
    "health": {"fps": 0, "latency": 0},
    "experiment": {
        "currentStepId": "IDLE",
        "completedStepIds": [],
        "nextStepId": "DETECT_OUTER",
        "confidence": 0,
        "status": "IN_PROGRESS"
    },
    "alerts": [],
    "logs": [],
    "detections": []
}

# Initialize pipeline
config = load_config("config.yaml")
gui_adapter = WebGUIAdapter()
pipeline = HARPipeline(config, gui_window=gui_adapter)

@app.on_event("startup")
async def startup_event():
    pipeline.start()

@app.on_event("shutdown")
async def shutdown_event():
    pipeline.stop()

def video_stream():
    while True:
        frame = global_state.get("latest_frame")
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.03) # ~30fps

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = {
                "health": global_state["health"],
                "experiment": global_state["experiment"],
                "alerts": global_state["alerts"][-5:], # send recent alerts
                "detections": global_state["detections"]
            }
            await websocket.send_json(payload)
            await asyncio.sleep(0.1) # 10Hz updates
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
