class EventStage:

    def __init__(

        self,

        event_manager
    ):

        self.event_manager = (
            event_manager
        )

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

            violations = []

            if hasattr(
                frame_data,
                "violations"
            ):

                violations = [

                    v for v in frame_data.violations

                    if v.get(
                        "tracker_id"
                    ) == tracker_id
                ]

            self.event_manager.update(

                tracker_id=tracker_id,

                violations=violations,

                zone=zone
            )

        return frame_data