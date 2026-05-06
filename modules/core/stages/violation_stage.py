from modules.core.stages.base_stage import (
    BaseStage
)
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

        detections = frame_data.detections

        frame_data.violations = []

        if len(detections) == 0:

            return frame_data

        for i, tracker_id in enumerate(
            detections.tracker_id
        ):

            class_id = detections.class_id[i]

            zone = frame_data.zones.get(
                tracker_id
            )

            speed = frame_data.speeds.get(
                tracker_id
            )

            violations = self.rule_engine.check(

                tracker_id=tracker_id,

                class_id=class_id,

                zone=zone,

                speed=speed
            )

            frame_data.violations.extend(
                violations
            )

        return frame_data