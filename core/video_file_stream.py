import cv2

class VideoFileStream:
    def __init__(self, path: str):
        self.path = path
        self.cap = None
        self.fps = None
        self.w = None
        self.h = None
        self.total_frames = None

    def start(self):
        self.cap = cv2.VideoCapture(self.path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video: {self.path}")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return self

    def readFrame(self):
        if self.cap is None:
            return None
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame

    def stop(self):
        if self.cap:
            self.cap.release()
        self.cap = None
