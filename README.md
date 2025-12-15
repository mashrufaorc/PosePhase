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

Squats
* Knee Alignment Uneven
* Insufficient Squat Depth
Push-Ups
* Body Line Not Straight
* Push-Up Depth Insufficient
Lunges
* Front Knee Not Bending Enough
* Back Knee Not Lowering Enough 

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
PosePhase/
├── app_launcher.py
├── requirements.txt
├── README.md
├── config/
│   └── thresholds.yaml
├── core/
│   ├── audio_feedback.py
│   ├── exercise_classifier.py
│   ├── feature_extractor.py
│   ├── feedback_engine.py
│   ├── form_evaluator.py
│   ├── pose_estimator.py
│   ├── rep_counter.py
│   ├── session_runner.py
│   ├── video_file_stream.py
│   ├── video_stream.py
│   └── fsm/
│       ├── fsm_base.py
│       ├── lunge_fsm.py
│       ├── pushup_fsm.py
│       ├── squat_fsm.py
│       └── states.py
├── ui/
│   └── renderer.py
├── utils/
│   ├── geometry.py
│   ├── logger.py
│   └── smoothing.py
├── evaluation/
│   ├── gt_frames_lunge.csv
│   ├── gt_frames_pushup.csv
│   ├── gt_frames_squat.csv
│   ├── metrics.py
│   └── reports/
│       ├── metrics_lunges/
│       ├── metrics_pushups/
│       └── metrics_squat/
├── reports/
│   ├── frame_log.csv
│   ├── rep_log.csv
│   ├── video_summary.json
│   └── webcam_summary.json
├── images/
│   └── video_file/
│       └── squat/
│           ├── bad_form/
│           └── good_form/
└── videos/
    ├── lunge/
    ├── pushup/
    └── squat/
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

```
PosePhase runs a per-frame pipeline: MediaPipe Pose → biomechanical features → smoothing → exercise detection or forced selection → FSM phase recognition → rep counting → rule-based form scoring → feedback (visual + audio) → logging + evaluation
```

---

Potential areas:

* Additional exercises
* ML-based exercise classifier
* 3D pose uplift
* Mobile application interface

---
