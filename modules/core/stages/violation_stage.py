from modules.core.stages.base_stage import (
    BaseStage
)


# =========================================================
# VIOLATION STAGE
# =========================================================
class ViolationStage(BaseStage):

    def __init__(

        self,

        rule_engine
    ):

        self.rule_engine = (
            rule_engine
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

        frame_data.violations = []

        if len(detections) == 0:

            return frame_data

        for i, tracker_id in enumerate(

            detections.tracker_id
        ):

            class_id = (
                detections.class_id[i]
            )

            zone = frame_data.zones.get(
                tracker_id
            )

            speed = frame_data.speeds.get(
                tracker_id
            )

            # =============================================
            # RULE ENGINE
            # =============================================
            violations = (
                self.rule_engine.check(

                    tracker_id=tracker_id,

                    class_id=class_id,

                    zone=zone,

                    speed=speed
                )
            )

            # =============================================
            # STANDARDIZED VIOLATION FORMAT
            # =============================================
            for violation in violations:

                frame_data.violations.append({

                    "tracker_id":
                        tracker_id,

                    "event_type":
                        violation,

                    "zone":
                        zone,

                    "speed":
                        speed
                })

        return frame_data