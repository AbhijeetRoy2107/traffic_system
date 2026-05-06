import supervision as sv
import cv2
import os

from modules.core.frame_data import (
    FrameData
)

# =========================================================
# CORE
# =========================================================
from modules.core.detector import (
    Detector
)

from modules.core.tracker import (
    Tracker
)

from modules.core.trajectory import (
    TrajectoryManager
)

from modules.core.stage_manager import (
    StageManager
)

# =========================================================
# STAGES
# =========================================================
from modules.core.stages.detection_stage import (
    DetectionStage
)

from modules.core.stages.tracking_stage import (
    TrackingStage
)

from modules.core.stages.spatial_stage import (
    SpatialStage
)

from modules.core.stages.analytics_stage import (
    AnalyticsStage
)

from modules.core.stages.counting_stage import (
    CountingStage
)

from modules.core.stages.violation_stage import (
    ViolationStage
)

from modules.core.stages.engine_stage import (
    EngineStage
)

from modules.core.stages.event_stage import (
    EventStage
)

from modules.core.stages.visualization_stage import (
    VisualizationStage
)

# =========================================================
# ANALYTICS
# =========================================================
from modules.analytics.speed import (
    SpeedEstimator
)

# =========================================================
# SPATIAL
# =========================================================
from modules.spatial.zone_logic import (
    ZoneLogic
)

from modules.spatial.homography import (
    HomographyManager
)

from modules.spatial.roi_loader import (
    load_rois
)

# =========================================================
# RULES / EVENTS
# =========================================================
from modules.rules.rule_engine import (
    RuleEngine
)

from modules.events.event_manager import (
    EventManager
)

# =========================================================
# ENGINES
# =========================================================
from modules.engines.engine_registry import (
    EngineRegistry
)

from modules.engines.accident.accident_engine import (
    RuleBasedAccidentEngine
)

# =========================================================
# VISUALIZATION
# =========================================================
from modules.visualization.label_builder import (
    LabelBuilder
)

from modules.visualization.birdeye import (
    BirdEyeVisualizer
)

# =========================================================
# LOGGER
# =========================================================
from utils.logger import (
    setup_logger
)

# =========================================================
# CONFIG
# =========================================================
from config.config import (

    BIRD_EYE_WIDTH,

    BIRD_EYE_HEIGHT,

    ENABLE_DETECTION,

    ENABLE_TRACKING,

    ENABLE_SPATIAL,

    ENABLE_ANALYTICS,

    ENABLE_COUNTING,

    ENABLE_VIOLATIONS,

    ENABLE_EVENTS,

    ENABLE_VISUALIZATION,

    ENABLE_BIRDEYE,

    ENABLE_ACCIDENT_ENGINE
)


# =========================================================
# PIPELINE
# =========================================================
class Pipeline:

    def __init__(

        self,

        video_info,

        video_path
    ):

        self.video_info = video_info

        self.video_path = video_path

        # =====================================================
        # LOGGER
        # =====================================================
        self.logger = setup_logger()

        self.logger.info(
            "Initializing pipeline..."
        )

        # =====================================================
        # CORE
        # =====================================================
        self.detector = Detector()

        self.tracker = Tracker(
            video_info.fps
        )

        self.trajectory = (
            TrajectoryManager()
        )

        # =====================================================
        # STAGE MANAGER
        # =====================================================
        self.stage_manager = (
            StageManager()
        )

        # =====================================================
        # SPATIAL
        # =====================================================
        self.homography = (
            HomographyManager(
                video_path
            )
        )

        self.logger.info(
            "Homography manager initialized"
        )

        self.rois = load_rois(
            video_path
        )

        self.logger.info(
            f"Loaded {len(self.rois)} ROIs"
        )

        self.zone_logic = ZoneLogic(
            self.rois
        )

        # =====================================================
        # ANALYTICS
        # =====================================================
        self.speed_estimator = (
            SpeedEstimator(
                self.homography
            )
        )

        # =====================================================
        # RULES / EVENTS
        # =====================================================
        self.rule_engine = (
            RuleEngine()
        )

        self.event_manager = (
            EventManager()
        )

        # =====================================================
        # ENGINE REGISTRY
        # =====================================================
        self.engine_registry = (
            EngineRegistry()
        )

        if ENABLE_ACCIDENT_ENGINE:

            self.engine_registry.register(

                "accident",

                RuleBasedAccidentEngine()
            )

        # =====================================================
        # VISUALIZATION
        # =====================================================
        self.label_builder = (
            LabelBuilder(
                mode="clean"
            )
        )

        self.birdeye = (
            BirdEyeVisualizer()
        )

        self.thickness = (
            sv.calculate_optimal_line_thickness(
                video_info.resolution_wh
            )
        )

        self.text_scale = (
            sv.calculate_optimal_text_scale(
                video_info.resolution_wh
            )
        )

        self.box_annotator = (
            sv.BoxAnnotator(
                thickness=self.thickness
            )
        )

        self.label_annotator = (
            sv.LabelAnnotator(
                text_scale=self.text_scale
            )
        )

        # =====================================================
        # REGISTER STAGES
        # =====================================================

        if ENABLE_DETECTION:

            self.stage_manager.register(

                "detection",

                DetectionStage(
                    self.detector
                )
            )

        if ENABLE_TRACKING:

            self.stage_manager.register(

                "tracking",

                TrackingStage(

                    self.tracker,

                    self.trajectory
                )
            )

        if ENABLE_SPATIAL:

            self.stage_manager.register(

                "spatial",

                SpatialStage(

                    self.rois,

                    self.zone_logic,

                    self.homography
                )
            )

        if ENABLE_ANALYTICS:

            self.stage_manager.register(

                "analytics",

                AnalyticsStage(

                    self.trajectory,

                    self.speed_estimator,

                    self.homography
                )
            )

        if ENABLE_COUNTING:

            self.stage_manager.register(

                "counting",

                CountingStage()
            )

        if ENABLE_VIOLATIONS:

            self.stage_manager.register(

                "violations",

                ViolationStage(
                    self.rule_engine
                )
            )

        # =====================================================
        # ENGINE STAGE
        # =====================================================
        self.stage_manager.register(

            "engines",

            EngineStage(

                engine_registry=(
                    self.engine_registry
                )
            )
        )

        # =====================================================
        # EVENT STAGE
        # =====================================================
        if ENABLE_EVENTS:

            self.stage_manager.register(

                "events",

                EventStage(
                    self.event_manager
                )
            )

        # =====================================================
        # VISUALIZATION
        # =====================================================
        if ENABLE_VISUALIZATION:

            self.visualization_stage = (
                VisualizationStage(

                    video_info=video_info,

                    trajectory_manager=(
                        self.trajectory
                    ),

                    label_builder=(
                        self.label_builder
                    ),

                    birdeye=self.birdeye,

                    box_annotator=(
                        self.box_annotator
                    ),

                    label_annotator=(
                        self.label_annotator
                    ),

                    rois=self.rois
                )
            )

        # =====================================================
        # BIRD-EYE OUTPUT
        # =====================================================
        self.bird_writer = None

        if ENABLE_BIRDEYE:

            bird_path = os.path.join(

                "outputs",

                os.path.basename(
                    video_path
                ).replace(

                    ".mp4",

                    "_birdeye.mp4"
                )
            )

            self.bird_writer = (
                cv2.VideoWriter(

                    bird_path,

                    cv2.VideoWriter_fourcc(
                        *"mp4v"
                    ),

                    video_info.fps,

                    (
                        BIRD_EYE_WIDTH,

                        BIRD_EYE_HEIGHT
                    )
                )
            )

        # =====================================================
        # ACCIDENT DISPLAY
        # =====================================================
        self.accident_display_timer = 0

        self.accident_display_duration = 40

        self.logger.info(
            "Pipeline initialized successfully"
        )

    # =====================================================
    # MAIN PROCESS
    # =====================================================
    def process_frame(
        self,
        frame
    ):

        frame_data = FrameData()

        # =====================================================
        # STAGE EXECUTION
        # =====================================================
        for stage_name, stage in (

            self.stage_manager.get_stages()
        ):

            # =================================================
            # DETECTION
            # =================================================
            if stage_name == "detection":

                frame_data = stage.process(

                    frame,

                    frame_data
                )

            # =================================================
            # ENGINE STAGE
            # =================================================
            elif stage_name == "engines":

                frame_data = stage.process(

                    frame=frame,

                    frame_data=frame_data,

                    trajectory_manager=(
                        self.trajectory
                    ),

                    zone_logic=(
                        self.zone_logic
                    )
                )

            # =================================================
            # NORMAL STAGES
            # =================================================
            else:

                frame_data = stage.process(
                    frame_data
                )

        # =====================================================
        # ACCIDENT DISPLAY TIMER
        # =====================================================
        accidents = frame_data.engines.get(
            "accident",
            []
        )

        if accidents:

            self.accident_display_timer = (
                self.accident_display_duration
            )

        # =====================================================
        # VISUALIZATION
        # =====================================================
        annotated = frame.copy()

        if ENABLE_VISUALIZATION:

            annotated, bird_frame = (
                self.visualization_stage.process(

                    frame=frame,

                    frame_data=frame_data,

                    accident_display_timer=(
                        self.accident_display_timer
                    )
                )
            )

            # =================================================
            # WRITE BIRD-EYE
            # =================================================
            if (
                ENABLE_BIRDEYE
                and self.bird_writer is not None
            ):

                self.bird_writer.write(
                    bird_frame
                )

        # =====================================================
        # ACCIDENT TIMER UPDATE
        # =====================================================
        if self.accident_display_timer > 0:

            self.accident_display_timer -= 1

        # =====================================================
        # RETURN
        # =====================================================
        return annotated, frame_data

    # =====================================================
    # RELEASE
    # =====================================================
    def release(self):

        if self.bird_writer is not None:

            self.bird_writer.release()

        self.logger.info(
            "Pipeline released"
        )