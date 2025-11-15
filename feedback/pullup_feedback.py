import numpy as np
import cv2

class PullupFeedback:
    def __init__(self, analyser):
        self.analyser = analyser

    def range_of_motion(self, image):
        # Check for full range of motion (arm extension)
        angle = self.analyser.calculate_joint_angle(
            self.analyser.joints['shoulder'],
            self.analyser.joints['elbow'],
            self.analyser.joints['wrist']
        )
        elbow = np.multiply(self.analyser.joints['elbow'], self.analyser.frame_size).astype(int)
        if angle < 65:
            self._draw_feedback(image, elbow, "Full Pull-up! (Chin over bar)", (23, 185, 43))
        elif angle > 175:
            self._draw_feedback(image, elbow, "Start from Full Hang", (255, 255, 255))

    def body_control(self, image):
        # Check for excessive swinging (horizontal/vertical deviation between reps could be a metric)
        shoulder = np.multiply(self.analyser.joints['shoulder'], self.analyser.frame_size)
        wrist = np.multiply(self.analyser.joints['wrist'], self.analyser.frame_size)
        movement = np.linalg.norm(shoulder - wrist)
        if movement > 0.8 * self.analyser.frame_height:  # Flag large movement
            self._draw_feedback(image, shoulder.astype(int), "Avoid Swinging", (255, 199, 44))

    def _draw_feedback(self, image, position, text, color):
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        rect_start = (position[0] - 5, position[1] - text_height - 5)
        rect_end = (position[0] + text_width + 5, position[1] + baseline + 5)
        cv2.rectangle(image, rect_start, rect_end, (0, 0, 0), cv2.FILLED)
        cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
