import numpy as np
import cv2

class SquatFeedback:
    def __init__(self, analyser):
        self.analyser = analyser

    def back_slacking(self, image):
        # Excessive spine flexion
        upper_back = np.multiply(self.analyser.joints['shoulder'], self.analyser.frame_size)
        lower_back = np.multiply(self.analyser.joints['hip'], self.analyser.frame_size)
        distance = np.linalg.norm(upper_back - lower_back)
        mid_back = ((upper_back + lower_back) / 2).astype(int)
        if not hasattr(self.analyser, 'initial_back_length') or self.analyser.initial_back_length == 0:
            self.analyser.initial_back_length = distance
        if distance + 7 < self.analyser.initial_back_length:
            self._draw_feedback(image, mid_back, "Excessive Spine Flexion", (255, 255, 255))

    def heels_off_ground(self, image):
        # Heels lifting off the ground
        heel = self.analyser.joints['heel']
        foot_index = self.analyser.joints['foot index']
        radians = np.arctan2(heel[1] - foot_index[1], heel[0] - foot_index[0])
        angle = np.abs(radians * 180 / np.pi)
        if not hasattr(self.analyser, 'initial_heel_angle') or self.analyser.initial_heel_angle == 0:
            self.analyser.initial_heel_angle = angle
        if angle > self.analyser.initial_heel_angle + 3:
            mid = np.multiply(heel, self.analyser.frame_size).astype(int)
            self._draw_feedback(image, mid, "Heels Off Ground", (255, 255, 255))

    def knee_over_toes(self, image):
        hip = self.analyser.joints['hip']
        knee = self.analyser.joints['knee']
        foot_index = self.analyser.joints['foot index']
        radians = np.arctan2(hip[1] - knee[1], hip[0] - knee[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle < 44 and knee[0] > foot_index[0]:
            mid = np.multiply(knee, self.analyser.frame_size).astype(int)
            self._draw_feedback(image, mid, "Knees Behind Toes", (255, 255, 255))

    def ensure_proper_depth(self, image):
        hip = self.analyser.joints['hip']
        knee = self.analyser.joints['knee']
        radians = np.arctan2(hip[1] - knee[1], hip[0] - knee[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle < 20:
            position = (10, 70)
            self._draw_feedback(image, position, "Awesome Depth", (23, 185, 43), large=True)

    def _draw_feedback(self, image, position, text, color, large=False):
        scale = 1 if large else 0.5
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)
        rect_start = (position[0] - 5, position[1] - text_height - 5)
        rect_end = (position[0] + text_width + 5, position[1] + baseline + 5)
        cv2.rectangle(image, rect_start, rect_end, (0, 0, 0), cv2.FILLED)
        cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)
