import numpy as np
import cv2

class PushupFeedback:
    def __init__(self, analyser):
        self.analyser = analyser

    def back_straight(self, image):
        # Check if back (shoulders to hips) is straight (minimal deviation in vertical axis)
        shoulder = np.multiply(self.analyser.joints['shoulder'], self.analyser.frame_size)
        elbow = np.multiply(self.analyser.joints['elbow'], self.analyser.frame_size)
        wrist = np.multiply(self.analyser.joints['wrist'], self.analyser.frame_size)
        # Calculate the average line from shoulders to wrist and draw
        mid_back = ((shoulder + wrist) / 2).astype(int)
        vertical_diff = abs(shoulder[1] - wrist[1])
        horizontal_diff = abs(shoulder[0] - wrist[0])
        # If vertical difference more than horizontal, warn
        if vertical_diff > 0.22 * self.analyser.frame_height:
            self._draw_feedback(image, mid_back, "Keep Back Straight", (255, 255, 255))

    def elbow_angle(self, image):
        # Elbow angle feedback
        angle = self.analyser.calculate_joint_angle(
            self.analyser.joints['shoulder'],
            self.analyser.joints['elbow'],
            self.analyser.joints['wrist']
        )
        elbow = np.multiply(self.analyser.joints['elbow'], self.analyser.frame_size).astype(int)
        if angle < 60:
            self._draw_feedback(image, elbow, "Go Lower (More Depth)", (23, 185, 43))
        elif angle > 160:
            self._draw_feedback(image, elbow, "Arms Locked Out", (23, 185, 43))

    def hand_position(self, image):
        # Hands not too wide or narrow (distance from shoulders)
        shoulder = np.multiply(self.analyser.joints['shoulder'], self.analyser.frame_size)
        wrist = np.multiply(self.analyser.joints['wrist'], self.analyser.frame_size)
        hand_width = abs(wrist[0] - shoulder[0])
        # Simple threshold: should be close to shoulder width
        if hand_width > 1.5 * abs(shoulder[1] - wrist[1]):
            self._draw_feedback(image, wrist.astype(int), "Hands Too Wide", (255, 199, 44))
        elif hand_width < 0.5 * abs(shoulder[1] - wrist[1]):
            self._draw_feedback(image, wrist.astype(int), "Hands Too Narrow", (255, 199, 44))

    def _draw_feedback(self, image, position, text, color):
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        rect_start = (position[0] - 5, position[1] - text_height - 5)
        rect_end = (position[0] + text_width + 5, position[1] + baseline + 5)
        cv2.rectangle(image, rect_start, rect_end, (0, 0, 0), cv2.FILLED)
        cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
