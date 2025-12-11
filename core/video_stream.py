import cv2, time

class VideoStream:
    def __init__(self, cam_id=0, width=1280, height=720):
        # Camera device index (0 = default webcam)
        self.cam_id = cam_id

        # Desired capture resolution
        self.width = width
        self.height = height

        # VideoCapture handle
        self.cap = None

        # Timestamps for computing frame-to-frame duration
        self.last_ts = None
        self.dt = 0.0  # Time difference between frames

    def start(self):
        # Initialize webcam stream
        self.cap = cv2.VideoCapture(self.cam_id)

        # Apply requested resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Store initial timestamp for timing calculations
        self.last_ts = time.time()
        return self

    def readFrame(self):
        # If the camera stream is not active, no frame can be returned
        if self.cap is None:
            return None

        # Grab the next frame from the webcam
        ok, frame = self.cap.read()
        if not ok:
            # End of stream or capture failure
            return None

        # Compute time difference between consecutive frames
        now = time.time()
        self.dt = now - self.last_ts
        self.last_ts = now

        return frame

    def stop(self):
        # Release webcam resources when active
        if self.cap:
            self.cap.release()

        self.cap = None

        # Close any OpenCV-created windows
        cv2.destroyAllWindows()
