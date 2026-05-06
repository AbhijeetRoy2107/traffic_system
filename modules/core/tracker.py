# modules/tracker.py

import supervision as sv


class Tracker:
    def __init__(self, fps):
        self.tracker = sv.ByteTrack(
            frame_rate=fps
        )

    def update(self, detections):
        return self.tracker.update_with_detections(detections)