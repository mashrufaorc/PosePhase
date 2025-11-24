import yaml
from core.video_stream import VideoStream
from core.session_runner import SessionRunner


def load_cfg():
    with open("config/thresholds.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    cfg = load_cfg()
    runner = SessionRunner(cfg)
    stream = VideoStream(cam_id=0)

    summary = runner.run(
        stream,
        mode="webcam",
        show_window=True,
        save_summary_path="reports/webcam_summary.json",
        forced_exercise=None  
    )
    print("Session summary:", summary)


if __name__ == "__main__":
    main()
