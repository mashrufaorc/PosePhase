import cv2
import mediapipe as mp

class PoseEstimator:
    def __init__(self, static_image_mode=False, min_det_conf=0.5, min_track_conf=0.5):
        # MediaPipe pose solution reference
        self.mp_pose = mp.solutions.pose
        
        # Initialize the pose detector with specified confidence thresholds
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            min_detection_confidence=min_det_conf,
            min_tracking_confidence=min_track_conf
        )
        
        # Mapping from MediaPipe landmark indices to lowercase landmark names
        self.names = {lm.value: lm.name.lower() for lm in self.mp_pose.PoseLandmark}

    def detect(self, frame):
        # Convert input frame from BGR (OpenCV) to RGB (MediaPipe requirement)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run pose detection on the RGB frame
        out = self.pose.process(rgb)

        # When no landmarks are detected, return None
        if not out.pose_landmarks:
            return None

        # Extract (x, y) coordinates for each landmark
        lms = {}
        for i, lm in enumerate(out.pose_landmarks.landmark):
            lms[self.names[i]] = (lm.x, lm.y)

        # Dictionary contains all landmark names mapped to their 2D coordinates
        return lms
