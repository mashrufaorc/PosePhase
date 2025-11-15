import numpy as np
import cv2
import mediapipe as mp
from feedback.squat_feedback import SquatFeedback
from exercise_modules.base_analyser import BaseAnalyser

mp_pose = mp.solutions.pose

class SquatAnalyser(BaseAnalyser):
    def __init__(self, mode, file_path=None):
        super().__init__(mode, "Squat", file_path)
        self.feedback_module = SquatFeedback(self)
        self.stage = "up"

    def extract_joints(self, landmarks):
        self.joints['shoulder'] = np.array([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y])
        self.joints['hip'] = np.array([landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y])
        self.joints['knee'] = np.array([landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y])
        self.joints['ankle'] = np.array([landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y])
        self.joints['heel'] = np.array([landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,
                                        landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y])
        self.joints['foot index'] = np.array([landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,
                                              landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y])

    def feedback(self, image):
        self.feedback_module.back_slacking(image)
        self.feedback_module.knee_over_toes(image)
        self.feedback_module.heels_off_ground(image)
        self.feedback_module.ensure_proper_depth(image)

    def rep_angle(self):
        return np.abs(180 * np.arctan2(self.joints['hip'][1] - self.joints['knee'][1],
                                       self.joints['hip'][0] - self.joints['knee'][0]) / np.pi)
