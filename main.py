import argparse
import os
from tqdm import tqdm
from utils.video_utils import get_video, get_video_writer
from modules.pipeline import Pipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Traffic System - Stage 1")

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input video"
    )

    return parser.parse_args()


def generate_output_path(input_path):
    # Extract filename without extension
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)

    # Ensure outputs folder exists
    os.makedirs("outputs", exist_ok=True)

    # Create new filename
    output_filename = f"{name}_processed{ext}"

    return os.path.join("outputs", output_filename)


def main():
    args = parse_args()

    input_path = args.input
    output_path = generate_output_path(input_path)

    print(f"Input: {input_path}")
    print(f"Output: {output_path}")

    video_info, frames = get_video(input_path)
    pipeline = Pipeline(video_info, input_path)

    with get_video_writer(output_path, video_info) as sink:
        for frame in tqdm(frames, total=video_info.total_frames):
            annotated_frame, _ = pipeline.process_frame(frame)
            sink.write_frame(annotated_frame)

if __name__ == "__main__":
    main()