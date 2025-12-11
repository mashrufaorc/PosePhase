import cv2

class VideoFileStream:
    def __init__(self, path: str):
        # File path for the video source
        self.path = path

        # VideoCapture handle (initialized in start())
        self.cap = None

        # Video properties extracted from the file
        self.fps = None
        self.w = None
        self.h = None
        self.total_frames = None

    def start(self):
        # Initialize OpenCV VideoCapture for the specified file
        self.cap = cv2.VideoCapture(self.path)

        # Ensure that the file was opened successfully
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video: {self.path}")

        # Extract frame rate (default to 30.0 if unavailable)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0

        # Extract frame dimensions
        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Total frame count in the file
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        return self

    def readFrame(self):
        # Return None if VideoCapture is not initialized
        if self.cap is None:
            return None

        # Read the next frame from the file
        ok, frame = self.cap.read()

        # Return None when the end of the file is reached or a read error occurs
        if not ok:
            return None

        return frame

    def stop(self):
        # Release VideoCapture resources when active
        if self.cap:
            self.cap.release()

        # Reset handle
        self.cap = None
