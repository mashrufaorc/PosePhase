import cv2, time

class VideoStream:
    def __init__(self, cam_id=0, width=1280, height=720):
        self.cam_id = cam_id
        self.width = width
        self.height = height
        self.cap = None
        self.last_ts = None
        self.dt = 0.0

    def start(self):
        self.cap = cv2.VideoCapture(self.cam_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.last_ts = time.time()
        return self

    def readFrame(self):
        if self.cap is None:
            return None
        ok, frame = self.cap.read()
        if not ok:
            return None
        now = time.time()
        self.dt = now - self.last_ts
        self.last_ts = now
        return frame

    def stop(self):
        if self.cap:
            self.cap.release()
        self.cap = None
        cv2.destroyAllWindows()
