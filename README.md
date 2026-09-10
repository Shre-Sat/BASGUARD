# BASGUARD — ISRO BAS Experiment Monitor

**Smart India Hackathon 2026 — Problem Statement PS26174 (ISRO)**  
**AI-Based Human Activity Recognition (HAR) for On-board BAS Experiments**

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![PyTorch GPU](https://img.shields.io/badge/PyTorch-GPU_Optimized-EE4C2C.svg)
![YOLOv8](https://img.shields.io/badge/YOLO-v8_XLarge-00FFFF.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-00A65A.svg)
![GStreamer](https://img.shields.io/badge/GStreamer-Pipeline-blue.svg)

BASGUARD is an end-to-end AI pipeline designed to monitor astronaut actions during on-board Biological Activity Space (BAS) experiments. It enforces strict procedural protocols using deterministic Petri-net logic, logs anomalies, and provides a professional "Mission Control" telemetry dashboard.

---

## 🎯 Features

*   **Multi-Modal Perception (High Accuracy):** 
    *   Object Detection via `YOLOv8x` (X-Large) combined with HSV color filtering for precise box detection.
    *   3D Hand Tracking via `MediaPipe` to extract 21-point skeletons and detect grasp/pinch gestures.
*   **Sequence Reasoning (Petri-Net FSM):** A robust Finite State Machine enforcing a strict step-by-step procedural protocol. Tracks tokens, detects duration anomalies (too fast/slow), and suggests ranked next-steps.
*   **ISRO Mission Control Dashboard:** Built with PyQt6 and PyQtGraph, featuring live video overlays, scrolling confidence telemetry charts, health metrics (FPS/CPU/MEM), and structured alerts in a dark, high-contrast aesthetic.
*   **Voice Alerts (Piper TTS):** Priority-queued, non-blocking offline neural text-to-speech warnings for anomalies with sub-300ms latency.
*   **GStreamer Video Pipeline:** Simultaneous RTSP streaming and splitmuxsink ring-buffer MP4 recording, with per-frame JSONL logging for precise anomaly tracking.

---

## 🚀 Setup & Installation

### 1. System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **GPU**: NVIDIA GPU recommended for YOLOv8x inference
- **System Packages**: 
  ```bash
  # Install GStreamer and sound dependencies
  sudo apt-get update
  sudo apt-get install -y gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly libgstreamer1.0-dev libportaudio2
  ```

### 2. Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Piper TTS Model
The system uses Piper TTS for fast voice generation. You need to download the voice model:
```bash
mkdir -p data
cd data
wget https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-lessac-medium.tar.gz
tar -xzf voice-en-us-lessac-medium.tar.gz
# The ONNX model should be placed so the TTS manager can find it, or update the path in config.yaml
```

---

## 🎮 Usage

Launch the full GUI application:

```bash
source venv/bin/activate
python main.py
```

### Options:
*   `--source /path/to/video.mp4`: Run inference on a pre-recorded video instead of the webcam.
*   `--no-gui`: Run the system entirely headlessly in the terminal.
*   `--no-tts`: Disable voice warnings.
*   `--config custom.yaml`: Override the default settings defined in `config.yaml`.

### Experiment Protocol:
To successfully complete the sequence without triggering an anomaly alert, follow this protocol:
1. Wait in **IDLE** state.
2. Open Outer Box.
3. Touch the Red Box.
4. Grasp and Place the Red Box.
5. Touch the Yellow Box.
6. Grasp and Place the Yellow Box.
7. Close the Outer Box.

---

## 📁 Project Structure

```
SIH/
├── config.yaml             # Global configuration (YOLO, TTS, Streaming)
├── main.py                 # Application entry point
├── requirements.txt        # Core dependencies
├── src/
│   ├── capture/            # Webcam threading
│   ├── perception/         # YOLO, MediaPipe, Heuristics
│   ├── fusion/             # SceneState data structures
│   ├── sequence/           # Petri-net FSM & Rules
│   ├── alerting/           # Piper TTS engine
│   ├── logging_layer/      # JSONL + Hash integrity
│   ├── streaming/          # GStreamer pipelines
│   └── gui/                # PyQt6 + PyQtGraph panels
├── data/
│   ├── models/             # YOLO weights
│   ├── logs/               # Generated JSONL and reports
│   └── recordings/         # Output MP4s
└── README.md
```
