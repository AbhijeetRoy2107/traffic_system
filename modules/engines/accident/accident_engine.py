import numpy as np
import supervision as sv
from collections import defaultdict

from modules.engines.base_engine import (
    BaseEngine
)


class RuleBasedAccidentEngine(BaseEngine):

    def __init__(self):

        self.pair_state = defaultdict(lambda: {
            "prev_dist": None,
            "frames": 0
        })

        # stricter than before
        self.distance_threshold = 40
        self.confirm_frames = 3

    def detect(self,detections,trajectories,zone_logic,frame=None,**kwargs):

        events = []

        if len(detections) < 2:
            return events

        points = detections.get_anchors_coordinates(
            anchor=sv.Position.BOTTOM_CENTER
        )

        for i in range(len(detections)):
            id1 = int(detections.tracker_id[i])

            for j in range(i + 1, len(detections)):
                id2 = int(detections.tracker_id[j])

                pair_key = tuple(sorted([id1, id2]))
                state = self.pair_state[pair_key]

                p1 = np.array(points[i])
                p2 = np.array(points[j])

                dist = np.linalg.norm(p1 - p2)

                # ignore noise / overlap
                if dist < 15:
                    continue

                prev_dist = state["prev_dist"]

                # require clear approach
                approaching = False
                if prev_dist is not None and (prev_dist - dist) > 3:
                    approaching = True

                state["prev_dist"] = dist

                # stricter condition
                if dist < self.distance_threshold and approaching:
                    state["frames"] += 1
                else:
                    state["frames"] = 0

                if state["frames"] >= self.confirm_frames:

                    zone = zone_logic.get_zone(tuple(p1))

                    events.append({
                        "type": "POSSIBLE_ACCIDENT",
                        "objects": [id1, id2],
                        "zone": zone
                    })

                    state["frames"] = 0

        return events