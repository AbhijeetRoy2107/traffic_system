import json
import os


def load_rois(video_path):

    filename = os.path.basename(
        video_path
    )

    path = "roi/roi_data.json"

    if not os.path.exists(path):
        return []

    try:

        with open(path, "r") as f:

            data = json.load(f)

        return data.get(
            filename,
            []
        )

    except Exception:

        return []