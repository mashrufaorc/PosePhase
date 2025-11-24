import time, cv2

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
        self.last_time = time.time()
        self.fps = 0.0
        self.quit_key = ord('q')

    def should_quit(self):
        return cv2.waitKey(1) & 0xFF == self.quit_key

    def drawPose(self, frame, landmarks):
        h, w = frame.shape[:2]
        for a, b in MP_EDGES:
            if a in landmarks and b in landmarks:
                xa, ya = landmarks[a]
                xb, yb = landmarks[b]
                cv2.line(frame, (int(xa*w), int(ya*h)), (int(xb*w), int(yb*h)), (0,255,0), 2)
        for _, (x, y) in landmarks.items():
            cv2.circle(frame, (int(x*w), int(y*h)), 4, (0,0,255), -1)

    def drawHUD(self, frame, exercise_label, exercise_conf, state, reps, warnings, feedback_text="", extra=None):
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (10,10), (w-10, 190), (0,0,0), -1)
        cv2.rectangle(frame, (10,10), (w-10, 190), (255,255,255), 2)

        y = 40
        cv2.putText(frame, f"Exercise: {exercise_label} ({exercise_conf:.2f})",
                    (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        y += 30
        cv2.putText(frame, f"Phase: {state.pretty}",
                    (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        y += 30
        cv2.putText(frame, f"Reps: {reps}",
                    (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        y += 30
        if feedback_text:
            cv2.putText(frame, f"Feedback: {feedback_text}",
                        (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

        self._update_fps()
        cv2.putText(frame, f"FPS: {self.fps:.1f}",
                    (w-140, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

        if extra:
            y2 = 210
            for k, v in list(extra.items())[:4]:
                cv2.putText(frame, f"{k}: {v:.2f}", (20, y2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,200,200), 1)
                y2 += 18

    def display(self, frame):
        cv2.imshow("PosePhase", frame)

    def _update_fps(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        if dt > 0:
            self.fps = 0.9*self.fps + 0.1*(1.0/dt) if self.fps else (1.0/dt)
