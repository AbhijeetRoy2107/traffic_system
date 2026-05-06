from config.config import (
    MAX_TRAJECTORY_POINTS
)


class AnalyticsStage:

    def __init__(
        self,
        trajectory_manager,
        speed_estimator,
        homography
    ):

        self.trajectory = trajectory_manager

        self.speed_estimator = speed_estimator

        self.homography = homography

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

        # =================================================
        # PROCESS TRACKS
        # =================================================
        for tracker_id in detections.tracker_id:

            zone = frame_data.zones.get(
                tracker_id
            )

            # =============================================
            # TRAJECTORY
            # =============================================
            traj = self.trajectory.get_trajectory(
                tracker_id
            )

            if traj is None:
                continue

            # =============================================
            # SPEED
            # =============================================
            speed = self.speed_estimator.compute_speed(

                tracker_id,

                traj,

                zone
            )

            frame_data.speeds[
                tracker_id
            ] = speed

            # =============================================
            # WORLD TRAJECTORY
            # =============================================
            world_traj = []

            for pos in traj["positions"]:

                wp = self.homography.to_world(
                    pos,
                    zone
                )

                if wp is not None:

                    world_traj.append(
                        wp
                    )

            # =============================================
            # STORE
            # =============================================
            if "world_trajectories" not in frame_data.metadata:

                frame_data.metadata[
                    "world_trajectories"
                ] = {}

            frame_data.metadata[
                "world_trajectories"
            ][tracker_id] = world_traj[
                -MAX_TRAJECTORY_POINTS:
            ]

        return frame_data