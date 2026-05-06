from collections import defaultdict
from modules.core.stages.base_stage import (
    BaseStage
)

class CountingStage(BaseStage):

    def __init__(self):

        self.total_counts = defaultdict(int)

        self.unique_ids = defaultdict(set)

    # =====================================================
    # PROCESS
    # =====================================================
    def process(
        self,
        frame_data
    ):

        detections = frame_data.detections

        if len(detections) == 0:

            return frame_data

        for i, tracker_id in enumerate(
            detections.tracker_id
        ):

            zone = frame_data.zones.get(
                tracker_id
            )

            if zone is None:
                continue

            if tracker_id not in self.unique_ids[
                zone
            ]:

                self.unique_ids[
                    zone
                ].add(tracker_id)

                self.total_counts[
                    zone
                ] += 1

        frame_data.metadata[
            "counts"
        ] = dict(
            self.total_counts
        )

        return frame_data