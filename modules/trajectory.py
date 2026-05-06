import time
from collections import deque
import supervision as sv

class TrajectoryManager:
    def __init__(self, max_history=30, max_missing_time=1.0):
        """
        max_history: number of frames to keep per object
        max_missing_time: seconds before removing stale objects
        """
        self.max_history = max_history
        self.max_missing_time = max_missing_time

        self.objects = {}  # tracker_id → state

    def update(self, detections):
        """
        Update trajectories with current detections
        """
        current_time = time.time()

        active_ids = set()

        for i, tracker_id in enumerate(detections.tracker_id):
            if tracker_id is None:
                continue

            active_ids.add(tracker_id)

            # get bottom-center point
            points = detections.get_anchors_coordinates(anchor=sv.Position.BOTTOM_CENTER)
            x, y = points[i]

            # initialize if new
            if tracker_id not in self.objects:
                self.objects[tracker_id] = {
                    "positions": deque(maxlen=self.max_history),
                    "timestamps": deque(maxlen=self.max_history),
                    "last_seen": current_time
                }

            obj = self.objects[tracker_id]

            obj["positions"].append((x, y))
            obj["timestamps"].append(current_time)
            obj["last_seen"] = current_time

        # remove stale objects
        self._cleanup(current_time)

    def _cleanup(self, current_time):
        """
        Remove objects not seen recently
        """
        to_delete = []

        for tracker_id, obj in self.objects.items():
            if current_time - obj["last_seen"] > self.max_missing_time:
                to_delete.append(tracker_id)

        for tracker_id in to_delete:
            del self.objects[tracker_id]

    def get_trajectory(self, tracker_id):
        """
        Returns trajectory (positions + timestamps)
        """
        if tracker_id not in self.objects:
            return None

        return self.objects[tracker_id]

    def get_all(self):
        """
        Returns all active trajectories
        """
        return self.objects