import numpy as np
import cv2
import mediapipe as mp
from feedback.pullup_feedback import PullupFeedback
from exercise_modules.base_analyser import BaseAnalyser

mp_pose = mp.solutions.pose

class PullupAnalyser(BaseAnalyser):
    def __init__(self, mode, file_path=None):
        super().__init__(mode, "Pull-up", file_path)
        self.feedback_module = PullupFeedback(self)
        self.stage = "down"

    def extract_joints(self, landmarks):
        self.joints['shoulder'] = np.array([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y])
        self.joints['elbow'] = np.array([landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y])
        self.joints['wrist'] = np.array([landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y])

    def feedback(self, image):
        self.feedback_module.range_of_motion(image)
        self.feedback_module.body_control(image)

    def rep_angle(self):
        return self.calculate_joint_angle(self.joints['shoulder'], self.joints['elbow'], self.joints['wrist'])
