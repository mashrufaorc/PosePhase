import json, time, cv2
from typing import Dict, Any, Optional
from collections import Counter

from core.pose_estimator import PoseEstimator
from core.feature_extractor import FeatureExtractor
from core.fsm.squat_fsm import SquatFSM
from core.fsm.pushup_fsm import PushupFSM
from core.fsm.lunge_fsm import LungeFSM
from core.exercise_classifier import ExerciseClassifier
from core.rep_counter import RepCounter
from core.form_evaluator import FormEvaluator
from core.feedback_engine import FeedbackEngine
from core.audio_feedback import AudioFeedback
from utils.smoothing import SignalSmoother
from utils.logger import CSVLogger
from ui.renderer import RendererUI

# Mapping from exercise label to corresponding finite state machine class
FSM_MAP = {"squat": SquatFSM, "pushup": PushupFSM, "lunge": LungeFSM}


class SessionRunner:
    """
    Central session controller that connects all processing components.
    Shared runner for both webcam and pre-recorded video modes.

    Responsibilities:
      - Capture pose landmarks using MediaPipe
      - Convert landmarks into angles and features
      - Apply EMA smoothing to noisy signals
      - Classify the active exercise type
      - Run exercise-specific FSM for phase detection
      - Count repetitions from phase transitions
      - Evaluate form and generate warnings
      - Render HUD overlay onto frames
      - Generate text and audio feedback
      - Log frame-level and rep-level statistics
      - Produce JSON summary with average score and warning breakdown
    """

    def __init__(self, cfg: Dict[str, Any]):
        # Configuration dictionary containing thresholds and settings
        self.cfg = cfg

        # Core processing modules
        self.pose = PoseEstimator()
        self.feats = FeatureExtractor()
        self.smoother = SignalSmoother(method="ema", alpha=0.25)
        self.classifier = ExerciseClassifier(cfg["classifier"])

        # FSM and form evaluation will be assigned after exercise selection
        self.fsm = None
        self.form = None

        # Repetition counter and feedback systems
        self.reps = RepCounter()
        self.feedback = FeedbackEngine()
        self.audio = AudioFeedback(enabled=True, rate=185, change_gap_s=0.8)

        # Currently active exercise label
        self.current_ex = None

        # UI renderer for pose and HUD
        self.ui = RendererUI()

        # Frame-level logger (per frame)
        self.frame_logger = CSVLogger(
            "reports/frame_log.csv",
            ["time_s", "frame_idx", "exercise", "conf", "phase",
             "knee_avg", "elbow_avg", "rep_count", "score", "warnings"]
        )

        # Rep-level logger (per completed repetition)
        self.rep_logger = CSVLogger(
            "reports/rep_log.csv",
            ["rep_id", "exercise", "start_time", "end_time", "duration_s",
             "min_knee", "min_elbow", "avg_score", "warnings_count", "warnings_top"]
        )

        # Internal counters and buffers
        self.frame_idx = 0
        self.rep_id = 0
        self.rep_buffer = []  # stores frame rows belonging to the current rep
        self.session_start = time.time()

        # Running statistics for score and warnings
        self._score_sum = 0.0
        self._score_n = 0
        self._warning_counter = Counter()

        # Session-level summary for export and UI
        self.summary = {
            "exercise": None,
            "rep_count": 0,
            "phase_counts": {},
            "warnings_count": 0,
            "warnings_examples": [],
            "warnings_breakdown": {},
            "avg_score": 0.0
        }

    # Helpers
    def _reset_trackers(self):
        # Reset running statistics for score and warnings
        self._score_sum = 0.0
        self._score_n = 0
        self._warning_counter.clear()

    def _swap_exercise(self, label: str):
        """
        Update FSM and form evaluator when exercise label changes.
        Also reset per-exercise counters and statistics.
        """
        self.current_ex = label

        # Create a new FSM instance for the selected exercise
        self.fsm = FSM_MAP[label](self.cfg[label])

        # Create a new form evaluator for the selected exercise
        self.form = FormEvaluator(label, self.cfg["form"][label])

        # Reset repetition counters and rep buffer
        self.reps.reset()
        self.rep_buffer.clear()
        self.rep_id = 0

        # Reset score and warning trackers
        self._reset_trackers()

        # Update summary with current exercise
        self.summary["exercise"] = label

    # Main loop
    def run(
        self,
        stream,
        mode="webcam",
        output_path: Optional[str] = None,
        save_summary_path: Optional[str] = None,
        show_window=True,
        forced_exercise: Optional[str] = None
    ):
        """
        Run the full session loop.

        Args:
            stream: frame source (webcam or video file)
            mode: "webcam" or "video"
            output_path: optional output video file path
            save_summary_path: optional JSON summary output path
            show_window: whether to display live window
            forced_exercise: fixed exercise label to bypass classifier
                             (e.g., "squat", "pushup", "lunge")
        """
        # Start underlying frame stream
        stream.start()

        # Audio pacing adjustment:
        # webcam mode: short gap for responsive feedback
        # video mode: longer gap to avoid dense TTS output
        if mode == "webcam":
            self.audio.set_change_gap(0.4)
        else:
            self.audio.set_change_gap(2.5)

        # Optional video writer for saving annotated output
        writer = None
        if mode == "video" and output_path:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_path, fourcc, stream.fps, (stream.w, stream.h))

        while True:
            # Read next frame from stream
            frame = stream.readFrame()
            if frame is None:
                # End of stream or error condition
                break

            # Pose detection step
            landmarks = self.pose.detect(frame)
            if landmarks:
                # Compute raw features from pose landmarks
                raw_features = self.feats.compute_all(landmarks)

                # Apply smoothing to reduce noise and jitter
                features = self.smoother.update(raw_features)

                # Exercise selection
                if forced_exercise:
                    # Fixed exercise mode: bypass classifier and lock label
                    if self.current_ex != forced_exercise:
                        self._swap_exercise(forced_exercise)

                    # Create a minimal prediction-like object
                    class _Pred:
                        pass

                    pred = _Pred()
                    pred.label = forced_exercise
                    pred.confidence = 1.0
                    pred.debug = {}
                else:
                    # Classifier-based exercise prediction
                    pred = self.classifier.predict(features)
                    if self.current_ex != pred.label:
                        self._swap_exercise(pred.label)

                # FSM, repetition count, and form scoring
                state = self.fsm.update(features)
                rep_count = self.reps.update(state)

                # Form score and warnings for current phase
                phase_score = self.form.scorePhase(state, features)

                # Feedback for UI and audio (score, warnings, praise)
                fb = self.feedback.generate(state, phase_score, features, rep_count)

                # Handle spoken feedback (warnings or praise)
                speak_msg = fb.get("speak_text", "")
                if speak_msg:
                    # AudioFeedback handles debouncing and repetition control
                    self.audio.speak(speak_msg)

                # Running statistics updates
                self._score_sum += float(fb["score"])
                self._score_n += 1

                # Count occurrences of each warning message
                for w in fb["warnings"]:
                    self._warning_counter[w] += 1

                # Per-frame CSV logging
                t = time.time() - self.session_start
                warnings_str = ";".join(fb["warnings"])

                row = {
                    "time_s": round(t, 3),
                    "frame_idx": self.frame_idx,
                    "exercise": pred.label,
                    "conf": round(pred.confidence, 3),
                    "phase": state.pretty,
                    "knee_avg": round(features.get("knee_angle_avg", 0), 2),
                    "elbow_avg": round(features.get("elbow_angle_avg", 0), 2),
                    "rep_count": rep_count,
                    "score": round(float(fb["score"]), 3),
                    "warnings": warnings_str
                }

                # Write frame-level row and store it for rep aggregation
                self.frame_logger.log(row)
                self.rep_buffer.append(row)
                self.frame_idx += 1

                # Flush rep-level log when repetition count increases
                if rep_count > self.rep_id:
                    self._flush_rep(rep_count)

                # Session summary statistics
                self.summary["rep_count"] = rep_count
                self.summary["phase_counts"][state.pretty] = (
                    self.summary["phase_counts"].get(state.pretty, 0) + 1
                )

                # Track cumulative warnings and collect example messages
                if fb["warnings"]:
                    self.summary["warnings_count"] += len(fb["warnings"])
                    if len(self.summary["warnings_examples"]) < 10:
                        self.summary["warnings_examples"].extend(fb["warnings"])

                # Average score across all processed frames
                self.summary["avg_score"] = round(self._score_sum / max(self._score_n, 1), 3)

                # Frequency of each warning type
                self.summary["warnings_breakdown"] = dict(self._warning_counter)

                # UI rendering (pose + HUD)
                self.ui.drawPose(frame, landmarks)
                self.ui.drawHUD(
                    frame,
                    pred.label,
                    pred.confidence,
                    state,
                    rep_count,
                    fb["warnings"],
                    fb["ui_text"],
                    pred.debug
                )

            # Write annotated frame to output video if writer is active
            if writer:
                writer.write(frame)

            # Display live window when enabled
            if show_window:
                self.ui.display(frame)
                if self.ui.should_quit():
                    # Stop loop when quit request is detected
                    break

        # Cleanup and finalization
        stream.stop()
        if writer:
            writer.release()

        self.frame_logger.close()
        self.rep_logger.close()

        # Save JSON summary file when a path is provided
        if save_summary_path:
            with open(save_summary_path, "w", encoding="utf-8") as f:
                json.dump(self.summary, f, indent=2)

        # Return in-memory summary for external consumers
        return self.summary

    # Rep aggregation
    def _flush_rep(self, rep_count: int):
        """
        Aggregate buffered frame rows into rep-level statistics
        and write a single entry to rep_log.csv.
        """
        if not self.rep_buffer:
            return

        # Update internal rep counter
        self.rep_id = rep_count

        # Rep start and end timestamps from buffered frames
        start_t = self.rep_buffer[0]["time_s"]
        end_t = self.rep_buffer[-1]["time_s"]

        # Collect angles and scores for the current repetition
        knees = [r["knee_avg"] for r in self.rep_buffer if r["knee_avg"] > 0]
        elbows = [r["elbow_avg"] for r in self.rep_buffer if r["elbow_avg"] > 0]
        scores = [r["score"] for r in self.rep_buffer]

        # Collect all warning messages from buffered frames
        all_warn = []
        for r in self.rep_buffer:
            if r["warnings"]:
                all_warn += r["warnings"].split(";")

        # Identify the most frequent warning during this repetition
        top_warn = max(set(all_warn), key=all_warn.count) if all_warn else ""

        # Construct rep-level summary row
        rep_row = {
            "rep_id": rep_count,
            "exercise": self.current_ex,
            "start_time": start_t,
            "end_time": end_t,
            "duration_s": round(end_t - start_t, 3),
            "min_knee": round(min(knees), 2) if knees else 0,
            "min_elbow": round(min(elbows), 2) if elbows else 0,
            "avg_score": round(sum(scores) / len(scores), 3) if scores else 0,
            "warnings_count": len(all_warn),
            "warnings_top": top_warn
        }

        # Write rep-level row and clear buffer for the next repetition
        self.rep_logger.log(rep_row)
        self.rep_buffer.clear()
