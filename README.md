# TriNetra HAR System — ISRO BAS Experiment Monitor

**Smart India Hackathon 2026 — Problem Statement PS26174 (ISRO)**  
**AI-Based Human Activity Recognition (HAR) for On-board BAS Experiments**

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![PyTorch CPU](https://img.shields.io/badge/PyTorch-CPU_Optimized-EE4C2C.svg)
![YOLOv8](https://img.shields.io/badge/YOLO-v8_Nano-00FFFF.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-00A65A.svg)

TriNetra is an end-to-end, CPU-optimized AI pipeline designed to monitor astronaut actions during on-board Biological Activity Space (BAS) experiments. It enforces strict procedural protocols, logs anomalies, and provides a professional "Mission Control" telemetry dashboard.

---

## 🎯 Features

*   **Multi-Modal Perception (CPU Optimized):** 
    *   Object Detection via `YOLOv8-nano` combined with HSV color filtering.
    *   3D Hand Tracking via `MediaPipe` to extract 21-point skeletons and detect grasp/pinch gestures.
    *   Geometric Interaction heuristics to determine Hand-Object relationships (Touching, Grasping, Holding).
*   **Sequence Reasoning:** A robust Finite State Machine (FSM) enforcing a strict step-by-step procedural protocol. Throws `OUT_OF_SEQUENCE` errors if steps are skipped.
*   **ISRO Mission Control Dashboard:** Built with PyQt6 and PyQtGraph, featuring live video overlays, scrolling confidence telemetry charts, health metrics (FPS/CPU/MEM), and structured alerts.
*   **Immutable Audit Trail:** Append-only JSON Lines logging system that computes SHA-256 hashes for tamper evidence, alongside human-readable summary reports.
*   **Voice Alerts (TTS):** Priority-queued, non-blocking text-to-speech warnings for anomalies.
*   **Offline Video Streaming:** Local MP4 recording via OpenCV that automatically tags anomalies in the filename.

---

## 🏗️ Architecture

The system is strictly decoupled into 8 distinct layers communicating via a unified `SceneState` object:

1.  **Capture Layer** (`src/capture`): Threaded camera polling to prevent I/O blocking.
2.  **Perception Layer** (`src/perception`): YOLOv8 objects, MediaPipe hands, and Interaction classification.
3.  **Fusion Layer** (`src/fusion`): Merges spatial bounding boxes with hand landmarks into a unified state.
4.  **Sequence Reasoning** (`src/sequence`): Graph-based protocol definition and FSM logic.
5.  **Alerting Layer** (`src/alerting`): Voice synthesis queue.
6.  **Logging Layer** (`src/logging_layer`): JSONL auditing and summary generation.
7.  **Streaming Layer** (`src/streaming`): Frame writing to MP4.
8.  **GUI Layer** (`src/gui`): PyQt6 main window assembling metrics, timelines, alerts, and video panels.

---

## 🚀 Setup & Installation

The project is designed to run locally on a CPU without requiring bulky NVIDIA CUDA libraries.

### 1. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install PyTorch (CPU-Only)
To prevent `pip` from downloading massive GPU libraries, install the CPU version of PyTorch first:
```bash
pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
# Additionally ensure you have pyqtgraph installed for the telemetry panel
pip install pyqtgraph cloudpickle polars ultralytics-platform
```

*(Note: On some Linux distributions, you may need system dependencies for OpenCV and TTS, e.g., `sudo apt install libgl1-mesa-glx espeak`)*

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

Once the GUI opens, click **START** in the top right to initialize the pipeline. 
*The first time you run this, Ultralytics will automatically download the 6MB YOLOv8-nano weights.*

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
├── config.yaml             # Global configuration
├── main.py                 # Application entry point
├── requirements.txt        # Core dependencies
├── src/
│   ├── capture/            # Webcam threading
│   ├── perception/         # YOLO, MediaPipe, Heuristics
│   ├── fusion/             # SceneState data structures
│   ├── sequence/           # Finite State Machine rules
│   ├── alerting/           # Text-To-Speech engine
│   ├── logging_layer/      # JSONL + Hash integrity
│   ├── streaming/          # Local MP4 recording
│   └── gui/                # PyQt6 + PyQtGraph panels
├── data/
│   ├── models/             # YOLO weights
│   ├── logs/               # Generated JSONL and reports
│   └── recordings/         # Output MP4s
└── README.md
```
