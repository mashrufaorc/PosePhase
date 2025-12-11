import time, cv2

# Pairs of body landmarks used to draw skeleton edges on the frame
MP_EDGES = [
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
]

class RendererUI:
    def __init__(self):
        # Last timestamp used for FPS calculation
        self.last_time = time.time()

        # Smoothed frames-per-second estimate
        self.fps = 0.0

        # Keyboard key used to request exit from the main loop
        self.quit_key = ord('q')

    def should_quit(self):
        """
        Return True when quit key is pressed.
        Uses a short delay to allow GUI event processing.
        """
        return cv2.waitKey(1) & 0xFF == self.quit_key

    def drawPose(self, frame, landmarks):
        """
        Draw skeleton lines and joint circles on the frame,
        based on normalized landmark coordinates in [0, 1].
        """
        h, w = frame.shape[:2]

        # Draw skeleton edges between connected landmarks
        for a, b in MP_EDGES:
            if a in landmarks and b in landmarks:
                xa, ya = landmarks[a]
                xb, yb = landmarks[b]
                cv2.line(
                    frame,
                    (int(xa * w), int(ya * h)),
                    (int(xb * w), int(yb * h)),
                    (0, 255, 0),
                    2
                )

        # Draw small circles at each landmark position
        for _, (x, y) in landmarks.items():
            cv2.circle(
                frame,
                (int(x * w), int(y * h)),
                4,
                (0, 0, 255),
                -1
            )

    def drawHUD(
        self,
        frame,
        exercise_label,
        exercise_conf,
        state,
        reps,
        warnings,
        feedback_text="",
        extra=None
    ):
        """
        Render heads-up display (HUD) block with exercise info,
        phase, repetition count, feedback text, FPS, and extra debug values.
        """
        h, w = frame.shape[:2]

        # HUD background rectangle at top of frame
        cv2.rectangle(frame, (10, 10), (w - 10, 190), (0, 0, 0), -1)

        # HUD border
        cv2.rectangle(frame, (10, 10), (w - 10, 190), (255, 255, 255), 2)

        # Text rows inside HUD
        y = 40
        cv2.putText(
            frame,
            f"Exercise: {exercise_label} ({exercise_conf:.2f})",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        y += 30
        cv2.putText(
            frame,
            f"Phase: {state.pretty}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        y += 30
        cv2.putText(
            frame,
            f"Reps: {reps}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        # Feedback text row (warnings or praise)
        y += 30
        if feedback_text:
            cv2.putText(
                frame,
                f"Feedback: {feedback_text}",
                (20, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

        # FPS display in bottom-right corner of HUD
        self._update_fps()
        cv2.putText(
            frame,
            f"FPS: {self.fps:.1f}",
            (w - 140, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        # Optional extra debug values (for example: scores or angles)
        if extra:
            y2 = 210
            for k, v in list(extra.items())[:4]:
                cv2.putText(
                    frame,
                    f"{k}: {v:.2f}",
                    (20, y2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (200, 200, 200),
                    1
                )
                y2 += 18

    def display(self, frame):
        """
        Show current frame in a named window.
        Window name: "PosePhase".
        """
        cv2.imshow("PosePhase", frame)

    def _update_fps(self):
        """
        Update FPS estimate based on time difference between consecutive calls.
        Uses exponential smoothing to stabilize displayed FPS value.
        """
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        if dt > 0:
            # First update uses raw 1/dt value;
            # subsequent updates blend new measurement with previous FPS
            self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt) if self.fps else (1.0 / dt)
