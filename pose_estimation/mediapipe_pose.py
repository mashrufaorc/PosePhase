import mediapipe as mp

class MediaPipePose:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False)

    def get_keypoints(self, frame):
        results = self.pose.process(frame)
        if not results.pose_landmarks:
            return None
        return results.pose_landmarks.landmark
