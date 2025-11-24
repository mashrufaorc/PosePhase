import yaml, argparse
from core.video_file_stream import VideoFileStream
from core.session_runner import SessionRunner


def load_cfg():
    with open("config/thresholds.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="path to input mp4")
    ap.add_argument("--output", required=True, help="path to annotated mp4")
    ap.add_argument("--summary", default="reports/video_summary.json")
    ap.add_argument("--no-window", action="store_true")
    ap.add_argument("--exercise", default=None, choices=["squat","pushup","lunge"])
    args = ap.parse_args()

    cfg = load_cfg()
    runner = SessionRunner(cfg)
    stream = VideoFileStream(args.input)

    runner.run(
        stream,
        mode="video",
        output_path=args.output,
        save_summary_path=args.summary,
        show_window=not args.no_window,
        forced_exercise=args.exercise
    )

    print("Annotated video saved to:", args.output)
    print("Summary saved to:", args.summary)


if __name__ == "__main__":
    main()
