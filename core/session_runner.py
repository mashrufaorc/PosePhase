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

FSM_MAP = {"squat": SquatFSM, "pushup": PushupFSM, "lunge": LungeFSM}


class SessionRunner:
    """
    Shared runner for webcam + video modes.

    Features:
      - MediaPipe Pose 2D landmarks -> angles/features
      - EMA smoothing
      - Exercise classifier OR forced_exercise from UI
      - FSM phase detection for squat/pushup/lunge
      - Rep counting from phase transitions
      - Form scoring + warnings
      - UI overlay renderer
      - TTS: speaks ONLY when feedback changes
      - Praise audio when form is good and no warnings
      - CSV logs + JSON summary including avg_score & warnings_breakdown
    """

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg

        # Pipeline modules
        self.pose = PoseEstimator()
        self.feats = FeatureExtractor()
        self.smoother = SignalSmoother(method="ema", alpha=0.25)
        self.classifier = ExerciseClassifier(cfg["classifier"])

        self.fsm = None
        self.form = None
        self.reps = RepCounter()
        self.feedback = FeedbackEngine()
        self.audio = AudioFeedback(enabled=True, rate=185, change_gap_s=0.8)

        self.current_ex = None
        self.ui = RendererUI()

        # Logging
        self.frame_logger = CSVLogger(
            "reports/frame_log.csv",
            ["time_s", "frame_idx", "exercise", "conf", "phase",
             "knee_avg", "elbow_avg", "rep_count", "score", "warnings"]
        )
        self.rep_logger = CSVLogger(
            "reports/rep_log.csv",
            ["rep_id", "exercise", "start_time", "end_time", "duration_s",
             "min_knee", "min_elbow", "avg_score", "warnings_count", "warnings_top"]
        )

        # Internal bookkeeping
        self.frame_idx = 0
        self.rep_id = 0
        self.rep_buffer = []
        self.session_start = time.time()

        # Score + warning tracking
        self._score_sum = 0.0
        self._score_n = 0
        self._warning_counter = Counter()

        # Session summary exported to JSON & UI
        self.summary = {
            "exercise": None,
            "rep_count": 0,
            "phase_counts": {},
            "warnings_count": 0,
            "warnings_examples": [],
            "warnings_breakdown": {},
            "avg_score": 0.0
        }

    # ---------------------------
    # Helpers
    # ---------------------------
    def _reset_trackers(self):
        self._score_sum = 0.0
        self._score_n = 0
        self._warning_counter.clear()

    def _swap_exercise(self, label: str):
        """Switch FSM + form model when predicted/forced exercise changes."""
        self.current_ex = label
        self.fsm = FSM_MAP[label](self.cfg[label])
        self.form = FormEvaluator(label, self.cfg["form"][label])

        # reset per-exercise counters
        self.reps.reset()
        self.rep_buffer.clear()
        self.rep_id = 0
        self._reset_trackers()

        self.summary["exercise"] = label

    # ---------------------------
    # Main loop
    # ---------------------------
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
        mode: "webcam" or "video"
        forced_exercise: if set ("squat"/"pushup"/"lunge"), bypass classifier
        """
        stream.start()

        # Audio pacing:
        # webcam = fast response to changes
        # video  = slower spacing
        if mode == "webcam":
            self.audio.set_change_gap(0.4)
        else:
            self.audio.set_change_gap(2.5)

        # video writer setup
        writer = None
        if mode == "video" and output_path:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_path, fourcc, stream.fps, (stream.w, stream.h))

        while True:
            frame = stream.readFrame()
            if frame is None:
                break

            landmarks = self.pose.detect(frame)
            if landmarks:
                raw_features = self.feats.compute_all(landmarks)
                features = self.smoother.update(raw_features)

                # -----------------------------
                # Exercise selection
                # -----------------------------
                if forced_exercise:
                    if self.current_ex != forced_exercise:
                        self._swap_exercise(forced_exercise)

                    class _Pred: pass
                    pred = _Pred()
                    pred.label = forced_exercise
                    pred.confidence = 1.0
                    pred.debug = {}
                else:
                    pred = self.classifier.predict(features)
                    if self.current_ex != pred.label:
                        self._swap_exercise(pred.label)

                # -----------------------------
                # FSM + reps + form
                # -----------------------------
                state = self.fsm.update(features)
                rep_count = self.reps.update(state)
                phase_score = self.form.scorePhase(state, features)  # dict: {score,warnings}
                fb = self.feedback.generate(state, phase_score, features, rep_count)

                # Speak warnings OR praise (AudioFeedback prevents repeats)
                speak_msg = fb.get("speak_text", "")
                if speak_msg:
                    self.audio.speak(speak_msg)

                # -----------------------------
                # Update trackers
                # -----------------------------
                self._score_sum += float(fb["score"])
                self._score_n += 1
                for w in fb["warnings"]:
                    self._warning_counter[w] += 1

                # -----------------------------
                # Logging to CSV
                # -----------------------------
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
                self.frame_logger.log(row)
                self.rep_buffer.append(row)
                self.frame_idx += 1

                # flush rep-level log when rep increments
                if rep_count > self.rep_id:
                    self._flush_rep(rep_count)

                # -----------------------------
                # Summary stats
                # -----------------------------
                self.summary["rep_count"] = rep_count
                self.summary["phase_counts"][state.pretty] = (
                    self.summary["phase_counts"].get(state.pretty, 0) + 1
                )

                if fb["warnings"]:
                    self.summary["warnings_count"] += len(fb["warnings"])
                    if len(self.summary["warnings_examples"]) < 10:
                        self.summary["warnings_examples"].extend(fb["warnings"])

                self.summary["avg_score"] = round(self._score_sum / max(self._score_n, 1), 3)
                self.summary["warnings_breakdown"] = dict(self._warning_counter)

                # -----------------------------
                # UI rendering
                # -----------------------------
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

            if writer:
                writer.write(frame)

            if show_window:
                self.ui.display(frame)
                if self.ui.should_quit():
                    break

        # -----------------------------
        # Cleanup
        # -----------------------------
        stream.stop()
        if writer:
            writer.release()

        self.frame_logger.close()
        self.rep_logger.close()

        if save_summary_path:
            with open(save_summary_path, "w", encoding="utf-8") as f:
                json.dump(self.summary, f, indent=2)

        return self.summary

    # ---------------------------
    # Rep aggregation
    # ---------------------------
    def _flush_rep(self, rep_count: int):
        """Compute rep-level stats from buffered frames and write to rep_log.csv."""
        if not self.rep_buffer:
            return

        self.rep_id = rep_count
        start_t = self.rep_buffer[0]["time_s"]
        end_t = self.rep_buffer[-1]["time_s"]

        knees = [r["knee_avg"] for r in self.rep_buffer if r["knee_avg"] > 0]
        elbows = [r["elbow_avg"] for r in self.rep_buffer if r["elbow_avg"] > 0]
        scores = [r["score"] for r in self.rep_buffer]

        all_warn = []
        for r in self.rep_buffer:
            if r["warnings"]:
                all_warn += r["warnings"].split(";")

        top_warn = max(set(all_warn), key=all_warn.count) if all_warn else ""

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
        self.rep_logger.log(rep_row)
        self.rep_buffer.clear()
