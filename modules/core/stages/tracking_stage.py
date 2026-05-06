class TrackingStage:

    def __init__(
        self,
        tracker,
        trajectory_manager
    ):

        self.tracker = tracker

        self.trajectory = trajectory_manager

    # =====================================================
    # PROCESS
    # =====================================================
    def process(
        self,
        frame_data
    ):

        detections = frame_data.detections

        # =================================================
        # TRACKER UPDATE
        # =================================================
        detections = self.tracker.update(
            detections
        )

        frame_data.detections = detections

        # =================================================
        # TRACKED IDS
        # =================================================
        if len(detections) > 0:

            frame_data.tracked_objects = (
                detections.tracker_id.tolist()
            )

        else:

            frame_data.tracked_objects = []

        # =================================================
        # TRAJECTORY UPDATE
        # =================================================
        self.trajectory.update(
            detections
        )

        return frame_data