from modules.core.stages.base_stage import (
    BaseStage
)


class EngineStage(BaseStage):

    def __init__(

        self,

        engine_registry
    ):

        self.engine_registry = (
            engine_registry
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

        engines = (
            self.engine_registry.get_all()
        )

        for engine_name, engine in engines.items():

            results = engine.detect(

                detections=detections,

                trajectories=trajectory_manager,

                zone_logic=zone_logic,

                frame=frame
            )

            frame_data.engines[
                engine_name
            ] = results

        return frame_data