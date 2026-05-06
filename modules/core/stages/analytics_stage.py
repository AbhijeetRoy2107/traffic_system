import supervision as sv

from modules.core.stages.base_stage import (
    BaseStage
)

from modules.shared.schemas import (
    EventType
)


# =========================================================
# ANALYTICS STAGE
# =========================================================
class AnalyticsStage(BaseStage):

    def __init__(

        self,

        trajectory_manager,

        speed_estimator,

        homography,

        congestion_analyzer=None
    ):

        self.trajectory_manager = (
            trajectory_manager
        )

        self.speed_estimator = (
            speed_estimator
        )

        self.homography = homography

        self.congestion_analyzer = (
            congestion_analyzer
        )
        # =====================================================
        # WORLD TRAJECTORIES
        # =====================================================
        self.world_trajectories = {}

    # =====================================================
    # PROCESS
    # =====================================================
    def process(

        self,

        frame_data
    ):

        detections = (
            frame_data.detections
        )

        speeds = {}

        world_positions = {}

        # =================================================
        # EMPTY CHECK
        # =================================================
        if len(detections) == 0:

            frame_data.speeds = speeds

            frame_data.world_positions = (
                world_positions
            )

            return frame_data

        # =================================================
        # TRACKER CHECK
        # =================================================
        if detections.tracker_id is not None:

            anchors = (
                detections.get_anchors_coordinates(
                    anchor=sv.Position.BOTTOM_CENTER
                )
            )

            for tracker_id, anchor in zip(

                detections.tracker_id,

                anchors
            ):

                zone = frame_data.zones.get(
                    tracker_id
                )

                # =========================================
                # WORLD POSITION
                # =========================================
                world_point = (
                    self.homography.to_world(
                        tuple(anchor),
                        zone
                    )
                )

                world_positions[
                    tracker_id
                ] = world_point

                # =========================================
                # WORLD TRAJECTORY HISTORY
                # =========================================
                if tracker_id not in (
                    self.world_trajectories
                ):

                    self.world_trajectories[
                        tracker_id
                    ] = []

                # =========================================
                # APPEND NEW POINT
                # =========================================
                self.world_trajectories[
                    tracker_id
                ].append(
                    world_point
                )

                # =========================================
                # LIMIT HISTORY
                # =========================================
                self.world_trajectories[
                    tracker_id
                ] = self.world_trajectories[
                    tracker_id
                ][-50:]
                
                # =========================================
                # TRAJECTORY
                # =========================================
                trajectory = (
                    self.trajectory_manager
                    .get_trajectory(tracker_id)
                )

                # =========================================
                # SPEED
                # =========================================
                speed = None

                if trajectory is not None:

                    speed = (
                        self.speed_estimator.compute_speed(

                            tracker_id=tracker_id,

                            traj=trajectory,

                            zone=zone
                        )
                    )

                speeds[
                    tracker_id
                ] = speed

        # =================================================
        # STORE
        # =================================================
        frame_data.speeds = speeds

        frame_data.world_positions = (
            world_positions
        )
        
        frame_data.metadata[
            "world_trajectories"
        ] = self.world_trajectories

        # =================================================
        # CONGESTION ANALYTICS
        # =================================================
        if self.congestion_analyzer is not None:

            congestion_results = []

            # =============================================
            # GROUP TRACKERS BY ZONE
            # =============================================
            zone_trackers = {}

            for tracker_id, zone in (

                frame_data.zones.items()
            ):

                if zone is None:

                    continue

                if zone not in zone_trackers:

                    zone_trackers[
                        zone
                    ] = []

                zone_trackers[
                    zone
                ].append(
                    tracker_id
                )

            # =============================================
            # ANALYZE EACH ZONE
            # =============================================
            for zone_name, tracker_ids in (

                zone_trackers.items()
            ):

                result = (
                    self.congestion_analyzer.update(

                        zone_name=zone_name,

                        tracker_ids=tracker_ids,

                        speeds=speeds
                    )
                )

                congestion_results.append(
                    result
                )

                # =========================================
                # CONGESTION EVENT
                # =========================================
                if result["congested"]:

                    frame_data.events.append({

                        "event_type":
                            EventType.CONGESTION,

                        "zone":
                            zone_name,

                        "severity":
                            "warning",

                        "source":
                            "congestion_analytics",

                        "metadata": {

                            "vehicle_count":
                                result[
                                    "vehicle_count"
                                ],

                            "average_speed":
                                result[
                                    "average_speed"
                                ]
                        }
                    })

            frame_data.metadata[
                "congestion"
            ] = congestion_results

        return frame_data