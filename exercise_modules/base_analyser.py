import numpy as np
import cv2
import mediapipe as mp

class BaseAnalyser:
    def __init__(self, mode: int, exercise_type: str, file_path: str = None):
        if mode == 0:
            self.cap = cv2.VideoCapture(0)
        else:
            self.cap = cv2.VideoCapture(file_path)
        if not self.cap.isOpened():
            raise ValueError("Error opening video stream or file")
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to read the first frame")
        original_height, original_width = frame.shape[:2]
        aspect_ratio = original_width / original_height
        self.frame_width = int(900 * aspect_ratio)
        self.frame_height = 900
        self.frame_size = [self.frame_width, self.frame_height]
        self.joints = {}
        self.reps = 0
        self.stage = None
        self.exercise_type = exercise_type

    def calculate_joint_angle(self, j1, j2, j3):
        v1 = np.array(j1 - j2)
        v2 = np.array(j3 - j2)
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        radians = np.arccos(np.clip(cos_angle, -1, 1))
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180:
            angle = 360 - angle
        return angle

    def draw_landmarks(self,image):
        #draw Circles on joints
        for joint in self.joints.values():
            cv2.circle(image,np.multiply(joint,self.frame_size).astype(int),3,(135, 53, 3),-1)
            cv2.circle(image,np.multiply(joint,self.frame_size).astype(int),6,(194, 99, 41),1)
        # draw lines between joints
        pairs = [['shoulder','hip'],['hip','knee'],['knee','ankle'],['heel','foot index'],['ankle','heel']]
        COLOR = (237, 185, 102)
        for pair in pairs:
            cv2.line(image,np.multiply(self.joints[pair[0]],self.frame_size).astype(int),
                     np.multiply(self.joints[pair[1]],self.frame_size).astype(int),COLOR,1,cv2.LINE_AA)

    def show_reps_on_screen(self, image, rep_angle, down_thresh, up_thresh):
        if(rep_angle < down_thresh and self.stage == "up"):
            self.stage = "down"
        elif(rep_angle > up_thresh and self.stage == "down"):
            self.reps += 1
            self.stage = "up"
        cv2.putText(image, f"Reps: {self.reps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    def extract_joints(self, landmarks):
        pass

    def feedback(self, image):
        pass

    def rep_angle(self):
        return 0

    def process_frame(self):
        mp_pose = mp.solutions.pose
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break
                aspect_ratio = frame.shape[1] / frame.shape[0]
                frame = cv2.resize(frame, (int(900 * aspect_ratio), 900))
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    self.extract_joints(landmarks)
                    self.draw_landmarks(image)
                    self.feedback(image)
                    rep_angle = self.rep_angle()
                    if self.exercise_type == 'Squat':
                        self.show_reps_on_screen(image, rep_angle, 25, 30)
                    elif self.exercise_type == 'Push-up':
                        self.show_reps_on_screen(image, rep_angle, 70, 170)
                    elif self.exercise_type == 'Pull-up':
                        self.show_reps_on_screen(image, rep_angle, 80, 140)
                cv2.imshow(f'{self.exercise_type} Analysis', image)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
        self.cap.release()
        cv2.destroyAllWindows()
