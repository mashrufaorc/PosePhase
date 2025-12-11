# PosePhase

### Real-Time 2D Pose-Based Phase-Aware Biomechanical Analysis for Automated Exercise Evaluation Using a Finite State Machine Framework

PosePhase transforms a standard webcam or video file into a real-time exercise analysis system.
Using 2D pose estimation, interpretable finite state machines, rule-based biomechanical scoring, and text-to-speech feedback, the system evaluates exercise form, counts repetitions, and generates detailed logs for performance assessment or research.

---
## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mashrufaorc/PosePhase.git
cd posephase
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Launch GUI (recommended)

```bash
python app_launcher.py
```

---

## Features

### Real-Time Pose Estimation

* MediaPipe Pose model (33 landmarks)
* Runs on CPU in real time
* No wearable sensors required

### Finite State Machine (FSM) Movement Phases

Supports:

* Squat
* Push-Up
* Lunge

Movement phases:

* Start / Top
* Descending
* Bottom
* Ascending

FSMs enable:

* Accurate rep detection
* Clear phase interpretation
* Consistent labeling across exercises

### Automated Form Evaluation

Detects:

* Insufficient depth
* Knee drift and hip drop
* Incomplete elbow extension
* Lateral asymmetry
* Trunk instability

Outputs:

* Phase-wise score
* Rep quality score
* Warnings and corrective suggestions

### Audio Coaching Feedback

* Spoken warnings (“Straighten your back”, etc.)
* Spoken praise when form is correct
* Audio is triggered only when feedback changes

### Exercise Auto-Detection

Automatically determines whether the user is performing:

* Squat
* Push-Up
* Lunge

Uses motion patterns, posture orientation, and angle profiles.

### Launcher UI

* Webcam mode
* Video file mode
* Exercise selection
* Auto-detect option
* Start session button
* End-of-session results panel (reps, scores, warnings summary)

### Comprehensive Logging

Automatically generates:

* `frame_log.csv` – per-frame metrics
* `rep_log.csv` – per-rep statistics
* `summary.json` – overall metrics
* Annotated output video (optional)

### Evaluation Module

Compares predictions vs ground truth to compute:

* Frame accuracy
* Precision, Recall, and F1-score
* Intersection-over-Union (IoU) for each phase
* Phase-transition accuracy
* Exercise classifier accuracy
* Rep-count error

---

## Folder Structure

```
posephase/
│
├── app_launcher.py
├── main_webcam.py
├── run_video.py
│
├── config/
│   └── thresholds.yaml
│
├── core/
│   ├── session_runner.py
│   ├── video_stream.py
│   ├── video_file_stream.py
│   ├── pose_estimator.py
│   ├── feature_extractor.py
│   ├── exercise_classifier.py
│   ├── rep_counter.py
│   ├── form_evaluator.py
│   ├── feedback_engine.py
│   ├── audio_feedback.py
│   │
│   └── fsm/
│       ├── fsm_base.py
│       ├── states.py
│       ├── squat_fsm.py
│       ├── pushup_fsm.py
│       └── lunge_fsm.py
│
├── ui/
│   └── renderer.py
│
├── utils/
│   ├── geometry.py
│   ├── smoothing.py
│   └── logger.py
│
├── evaluation/
│   └── metrics.py
│
├── reports/
│
└── README.md
```
---

## Output Files

| File              | Description                                          |
| ----------------- | ---------------------------------------------------- |
| `frame_log.csv`   | Per-frame landmarks, phases, angles, warnings, score |
| `rep_log.csv`     | Start/end frame of each rep, time, depth, quality    |
| `summary.json`    | Overall summary for the session results screen       |
| `annotated_*.mp4` | Video with pose overlay and HUD             |

---

## Configuration

Thresholds and parameters are located in:

```
config/thresholds.yaml
```

Includes:

* Joint-angle thresholds
* Symmetry penalties
* Depth requirements
* Exercise classifier rules
* Praise and warning criteria

---

## Architecture Diagram

Place architecture diagram here:

```
...................
```

---

Potential areas:

* Additional exercises
* ML-based exercise classifier
* 3D pose uplift
* Mobile application interface
* Automatic ground-truth labelling tools

---
