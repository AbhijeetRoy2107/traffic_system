import argparse
import os

from tqdm import tqdm

from utils.video_utils import (
    get_video,
    get_video_writer
)

from modules.core.pipeline import Pipeline


# =========================================================
# ARGUMENTS
# =========================================================
def parse_args():

    parser = argparse.ArgumentParser(
        description="Traffic System"
    )

    parser.add_argument(

        "--input",

        type=str,

        required=True,

        help="Path to input video"
    )

    return parser.parse_args()


# =========================================================
# OUTPUT PATH
# =========================================================
def generate_output_path(input_path):

    filename = os.path.basename(
        input_path
    )

    name, ext = os.path.splitext(
        filename
    )

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    output_filename = (
        f"{name}_processed{ext}"
    )

    return os.path.join(
        "outputs",
        output_filename
    )


# =========================================================
# MAIN
# =========================================================
def main():

    args = parse_args()

    input_path = args.input

    output_path = generate_output_path(
        input_path
    )

    print(f"Input: {input_path}")

    print(f"Output: {output_path}")

    # =====================================================
    # VIDEO
    # =====================================================
    video_info, frames = get_video(
        input_path
    )

    # =====================================================
    # PIPELINE
    # =====================================================
    pipeline = Pipeline(
        video_info,
        input_path
    )

    # =====================================================
    # OUTPUT VIDEO
    # =====================================================
    with get_video_writer(
        output_path,
        video_info
    ) as sink:

        for frame in tqdm(

            frames,

            total=video_info.total_frames
        ):

            annotated_frame, _ = (
                pipeline.process_frame(
                    frame
                )
            )

            sink.write_frame(
                annotated_frame
            )

    # =====================================================
    # RELEASE EXTRA WRITERS
    # =====================================================
    pipeline.release()

    print("\nProcessing complete")

    print(
        "\nGenerated files:"
    )

    print(output_path)

    print(
        output_path.replace(
            ".mp4",
            "_birdeye.mp4"
        )
    )


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":

    main()