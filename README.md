This application provides real-time analysis of Squats, Push-ups, and Pull-ups using MediaPipe Pose, OpenCV, and a Tkinter GUI.
Select the exercise and input source (webcam or video file) and receive instant feedback and rep counts.

## Installation

### Prerequisites
- Python 3.8 or higher
- Conda or pip package manager

### Setup

1. Clone or download this repository
```powershell
git clone https://github.com/mashrufaorc/PosePhase.git
```
2. Navigate to the project directory:
   ```powershell
   cd PosePhase
   ```
3. Install required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```powershell
python main.py
```

1. Launch the GUI
2. Select your exercise (Squat, Push-up, or Pull-up)
3. Choose input source:
   - **Webcam (0)**: Real-time analysis from your camera
   - **Video File**: Upload a video file for analysis
4. The application will display pose landmarks and rep counts
5. Press **'q'** to exit the analysis window

## Architecture

- **`exercise_modules/`** - Modular per-exercise analysis (SquatAnalyser, PushupAnalyser, PullupAnalyser)
- **`feedback/`** - Biomechanical feedback and form correction logic
- **`pose_estimation/`** - MediaPipe Pose extraction and joint calculation
- **`ui/`** - Tkinter GUI interface
- **`main.py`** - Application entry point

## Features

- Real-time pose detection using MediaPipe
- Exercise-specific rep counting
- Visual feedback on form
- Support for webcam and video file inputs
- Rep count display on screen
