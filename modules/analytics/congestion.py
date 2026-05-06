from collections import deque

from modules.shared.schemas import (
    EventType
)


# =========================================================
# CONGESTION ANALYZER
# =========================================================
class CongestionAnalyzer:

    def __init__(

        self,

        vehicle_threshold=8,

        speed_threshold=10,

        persistence_frames=30
    ):

        # =================================================
        # CONFIG
        # =================================================
        self.vehicle_threshold = (
            vehicle_threshold
        )

        self.speed_threshold = (
            speed_threshold
        )

        self.persistence_frames = (
            persistence_frames
        )

        # =================================================
        # ZONE HISTORY
        # =================================================
        self.zone_history = {}

    # =====================================================
    # UPDATE
    # =====================================================
    def update(

        self,

        zone_name,

        tracker_ids,

        speeds
    ):

        # =================================================
        # INIT HISTORY
        # =================================================
        if zone_name not in self.zone_history:

            self.zone_history[
                zone_name
            ] = deque(

                maxlen=self.persistence_frames
            )

        # =================================================
        # VEHICLE COUNT
        # =================================================
        vehicle_count = len(
            tracker_ids
        )

        # =================================================
        # AVG SPEED
        # =================================================
        zone_speeds = []

        for tracker_id in tracker_ids:

            speed = speeds.get(
                tracker_id
            )

            if speed is not None:

                zone_speeds.append(
                    speed
                )

        avg_speed = 0

        if zone_speeds:

            avg_speed = (

                sum(zone_speeds)
                / len(zone_speeds)
            )

        # =================================================
        # CONGESTION CHECK
        # =================================================
        congested = (

            vehicle_count >= (
                self.vehicle_threshold
            )

            and

            avg_speed <= (
                self.speed_threshold
            )
        )

        # =================================================
        # STORE HISTORY
        # =================================================
        self.zone_history[
            zone_name
        ].append(
            congested
        )

        # =================================================
        # PERSISTENCE CHECK
        # =================================================
        history = self.zone_history[
            zone_name
        ]

        persistent_congestion = (

            len(history)
            == self.persistence_frames

            and

            all(history)
        )

        # =================================================
        # RESULT
        # =================================================
        return {

            "zone": zone_name,

            "vehicle_count":
                vehicle_count,

            "average_speed":
                round(avg_speed, 2),

            "congested":
                persistent_congestion,

            "event_type":
                EventType.CONGESTION
                if persistent_congestion
                else None
        }