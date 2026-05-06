import supervision as sv
import numpy as np

from config.config import (
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    ALLOWED_CLASSES
)


class DetectionStage:

    def __init__(self, detector):

        self.detector = detector

    def process(
        self,
        frame,
        frame_data
    ):

        # =================================================
        # DETECTION
        # =================================================
        result = self.detector.detect(
            frame
        )

        detections = (
            sv.Detections.from_ultralytics(
                result
            )
        )

        # =================================================
        # FILTERING
        # =================================================
        detections = detections[
            (
                detections.confidence
                > CONFIDENCE_THRESHOLD
            )
            &
            (
                np.isin(
                    detections.class_id,
                    ALLOWED_CLASSES
                )
            )
        ]

        detections = detections.with_nms(
            IOU_THRESHOLD
        )

        # =================================================
        # STORE
        # =================================================
        frame_data.detections = detections

        return frame_data