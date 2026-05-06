class EngineStage:

    def __init__(

        self,

        accident_engine=None,

        emergency_engine=None,

        anpr_engine=None
    ):

        self.accident_engine = (
            accident_engine
        )

        self.emergency_engine = (
            emergency_engine
        )

        self.anpr_engine = (
            anpr_engine
        )

    # =====================================================
    # PROCESS
    # =====================================================
    def process(

        self,

        frame,

        frame_data,

        trajectory_manager,

        zone_logic
    ):

        detections = frame_data.detections

        # =================================================
        # ACCIDENT ENGINE
        # =================================================
        if self.accident_engine is not None:

            accidents = (
                self.accident_engine.detect(

                    detections=detections,

                    trajectories=trajectory_manager,

                    zone_logic=zone_logic
                )
            )

            frame_data.accidents = (
                accidents
            )

        # =================================================
        # EMERGENCY VEHICLE ENGINE
        # =================================================
        if self.emergency_engine is not None:

            emergency_events = (
                self.emergency_engine.detect(

                    frame,

                    detections
                )
            )

            frame_data.metadata[
                "emergency_events"
            ] = emergency_events

        # =================================================
        # ANPR ENGINE
        # =================================================
        if self.anpr_engine is not None:

            anpr_results = (
                self.anpr_engine.detect(

                    frame,

                    detections
                )
            )

            frame_data.metadata[
                "anpr_results"
            ] = anpr_results

        return frame_data