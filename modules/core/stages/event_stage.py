from modules.core.stages.base_stage import (
    BaseStage
)


# =========================================================
# EVENT STAGE
# =========================================================
class EventStage(BaseStage):

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

        detections = (
            frame_data.detections
        )

        if len(detections) == 0:

            return frame_data

        for violation in (

            frame_data.violations
        ):

            tracker_id = violation.get(
                "tracker_id"
            )

            event_type = violation.get(
                "event_type"
            )

            zone = violation.get(
                "zone"
            )

            speed = violation.get(
                "speed"
            )

            new_events = (
                self.event_manager.update(

                    tracker_id=tracker_id,

                    violations=[
                        event_type
                    ],

                    zone=zone,

                    source="rule_engine",

                    metadata={

                        "speed":
                            speed
                    }
                )
            )

            frame_data.events.extend(
                new_events
            )
            
        return frame_data