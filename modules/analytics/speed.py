# modules/speed.py

import numpy as np
from collections import defaultdict, deque

from config.config import (
    SPEED_WINDOW_SIZE,
    SPEED_SMOOTHING_ALPHA,
    MIN_MOVEMENT_DISTANCE,
    MAX_REASONABLE_SPEED,
    MAX_TRAJECTORY_POINTS
)

class SpeedEstimator:

    def __init__(
        self,
        homography_manager,
        window_size=SPEED_WINDOW_SIZE,
        smoothing_alpha=SPEED_SMOOTHING_ALPHA,
        min_distance=MIN_MOVEMENT_DISTANCE,
        max_speed=MAX_REASONABLE_SPEED
    ):

        # =====================================================
        # HOMOGRAPHY
        # =====================================================
        self.homography = homography_manager

        # =====================================================
        # SPEED SETTINGS
        # =====================================================
        self.window_size = window_size

        # EMA smoothing factor
        self.alpha = smoothing_alpha

        # ignore tiny movement jitter
        self.min_distance = min_distance

        # clamp unrealistic spikes
        self.max_speed = max_speed

        # =====================================================
        # SPEED MEMORY
        # =====================================================
        self.smoothed_speeds = {}

        self.speed_history = defaultdict(
            lambda: deque(maxlen=MAX_TRAJECTORY_POINTS)
        )

    # =========================================================
    # EMA SMOOTHING
    # =========================================================
    def smooth_speed(
        self,
        tracker_id,
        speed
    ):

        if tracker_id not in self.smoothed_speeds:

            self.smoothed_speeds[
                tracker_id
            ] = speed

            return speed

        prev = self.smoothed_speeds[
            tracker_id
        ]

        smoothed = (
            self.alpha * speed
            + (1 - self.alpha) * prev
        )

        self.smoothed_speeds[
            tracker_id
        ] = smoothed

        return smoothed

    # =========================================================
    # COMPUTE SPEED
    # =========================================================
    def compute_speed(
        self,
        tracker_id,
        traj,
        zone
    ):

        if zone is None:
            return None

        positions = traj["positions"]
        timestamps = traj["timestamps"]

        # =====================================================
        # NEED ENOUGH HISTORY
        # =====================================================
        if len(positions) < self.window_size:
            return None

        # =====================================================
        # LONGER TEMPORAL WINDOW
        # =====================================================
        p1 = positions[-self.window_size]
        p2 = positions[-1]

        t1 = timestamps[-self.window_size]
        t2 = timestamps[-1]

        dt = t2 - t1

        if dt <= 0:
            return None

        # =====================================================
        # IMAGE -> WORLD
        # =====================================================
        w1 = self.homography.to_world(
            p1,
            zone
        )

        w2 = self.homography.to_world(
            p2,
            zone
        )

        if w1 is None or w2 is None:
            return None

        # =====================================================
        # DISTANCE
        # =====================================================
        dist = np.linalg.norm(
            np.array(w2) - np.array(w1)
        )

        # =====================================================
        # IGNORE TINY JITTER
        # =====================================================
        if dist < self.min_distance:
            return None

        # =====================================================
        # RAW SPEED
        # =====================================================
        speed_mps = dist / dt

        speed_kmph = speed_mps * 3.6

        # =====================================================
        # CLAMP INSANE VALUES
        # =====================================================
        speed_kmph = min(
            speed_kmph,
            self.max_speed
        )

        # =====================================================
        # STORE HISTORY
        # =====================================================
        self.speed_history[
            tracker_id
        ].append(speed_kmph)

        # =====================================================
        # EMA SMOOTHING
        # =====================================================
        smoothed_speed = self.smooth_speed(
            tracker_id,
            speed_kmph
        )

        return round(
            smoothed_speed,
            1
        )