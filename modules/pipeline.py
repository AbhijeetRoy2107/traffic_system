# modules/pipeline.py

import supervision as sv
import numpy as np
import cv2
import json
import os

from modules.zone_logic import ZoneLogic
from modules.speed import SpeedEstimator
from modules.trajectory import TrajectoryManager
from modules.detector import Detector
from modules.tracker import Tracker
from modules.rule_engine import RuleEngine
from modules.label_builder import LabelBuilder
from modules.events.event_manager import EventManager
from modules.engines.accident_engine import RuleBasedAccidentEngine
from modules.homography import HomographyManager

from config.config import (
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    ALLOWED_CLASSES
)


# =========================================================
# ROI LOADING
# =========================================================
def load_rois(video_path):

    filename = os.path.basename(video_path)

    if not os.path.exists("roi/roi_data.json"):
        return []

    try:
        with open("roi/roi_data.json", "r") as f:
            data = json.load(f)

        return data.get(filename, [])

    except Exception:
        return []


# =========================================================
# POINT IN POLYGON
# =========================================================
def point_in_polygon(point, polygon):

    return cv2.pointPolygonTest(
        polygon,
        point,
        False
    ) >= 0


# =========================================================
# PIPELINE
# =========================================================
class Pipeline:

    def __init__(self, video_info, video_path):

        # =====================================================
        # CORE MODULES
        # =====================================================
        self.detector = Detector()

        self.tracker = Tracker(
            video_info.fps
        )

        self.trajectory = TrajectoryManager()

        # =====================================================
        # HOMOGRAPHY + SPEED
        # =====================================================
        self.homography = HomographyManager(
            video_path
        )

        self.speed_estimator = SpeedEstimator(
            self.homography
        )

        # =====================================================
        # SPATIAL LOGIC
        # =====================================================
        self.rois = load_rois(video_path)

        self.zone_logic = ZoneLogic(
            self.rois
        )

        # =====================================================
        # RULES / EVENTS
        # =====================================================
        self.rule_engine = RuleEngine()

        self.event_manager = EventManager()

        self.accident_engine = RuleBasedAccidentEngine()

        # =====================================================
        # LABELS
        # =====================================================
        self.label_builder = LabelBuilder(
            mode="clean"
        )

        # =====================================================
        # VISUALIZATION
        # =====================================================
        self.thickness = sv.calculate_optimal_line_thickness(
            video_info.resolution_wh
        )

        self.text_scale = sv.calculate_optimal_text_scale(
            video_info.resolution_wh
        )

        self.box_annotator = sv.BoxAnnotator(
            thickness=self.thickness
        )

        self.label_annotator = sv.LabelAnnotator(
            text_scale=self.text_scale
        )

        # =====================================================
        # ACCIDENT DISPLAY
        # =====================================================
        self.accident_display_timer = 0
        self.accident_display_duration = 40

    # =========================================================
    # MAIN PROCESS
    # =========================================================
    def process_frame(self, frame):

        # =====================================================
        # DETECTION
        # =====================================================
        result = self.detector.detect(frame)

        detections = sv.Detections.from_ultralytics(
            result
        )

        # =====================================================
        # FILTERING
        # =====================================================
        detections = detections[
            (detections.confidence > CONFIDENCE_THRESHOLD)
            &
            (np.isin(
                detections.class_id,
                ALLOWED_CLASSES
            ))
        ]

        detections = detections.with_nms(
            IOU_THRESHOLD
        )

        # =====================================================
        # ROI FILTERING
        # =====================================================
        if len(detections) > 0 and self.rois:

            points = detections.get_anchors_coordinates(
                anchor=sv.Position.BOTTOM_CENTER
            )

            mask = []

            for pt in points:

                inside = False

                for roi in self.rois:

                    if "points" not in roi:
                        continue

                    polygon = np.array(
                        roi["points"]
                    )

                    if point_in_polygon(
                        tuple(pt),
                        polygon
                    ):
                        inside = True
                        break

                mask.append(inside)

            detections = detections[
                np.array(mask)
            ]

        # =====================================================
        # TRACKING
        # =====================================================
        detections = self.tracker.update(
            detections
        )

        # =====================================================
        # TRAJECTORY UPDATE
        # =====================================================
        self.trajectory.update(
            detections
        )

        # =====================================================
        # ACCIDENT DETECTION
        # =====================================================
        accident_events = self.accident_engine.detect(
            detections=detections,
            trajectories=self.trajectory,
            zone_logic=self.zone_logic
        )

        if accident_events:

            print(
                "ACCIDENT:",
                accident_events
            )

            self.accident_display_timer = (
                self.accident_display_duration
            )

        for event in accident_events:

            self.event_manager.update(
                tracker_id=int(
                    event["objects"][0]
                ),
                violations=[
                    event["type"]
                ],
                zone=event["zone"]
            )

        # =====================================================
        # LABELS
        # =====================================================
        labels = []

        if len(detections) > 0:

            points = detections.get_anchors_coordinates(
                anchor=sv.Position.BOTTOM_CENTER
            )

            for i, tracker_id in enumerate(
                detections.tracker_id
            ):

                # =============================================
                # OBJECT POINT
                # =============================================
                pt = tuple(points[i])

                # =============================================
                # FIND ZONE
                # =============================================
                zone = self.zone_logic.get_zone(
                    pt
                )

                # =============================================
                # TRAJECTORY
                # =============================================
                traj = self.trajectory.get_trajectory(
                    tracker_id
                )

                # =============================================
                # SPEED
                # =============================================
                speed = None

                if traj is not None:

                    speed = self.speed_estimator.compute_speed(
                        tracker_id,
                        traj,
                        zone
                    )

                # =============================================
                # CLASS
                # =============================================
                class_id = detections.class_id[i]

                # =============================================
                # RULE CHECKING
                # =============================================
                violations = self.rule_engine.check(
                    tracker_id=tracker_id,
                    class_id=class_id,
                    zone=zone,
                    speed=speed
                )

                # =============================================
                # EVENT UPDATE
                # =============================================
                self.event_manager.update(
                    tracker_id=tracker_id,
                    violations=violations,
                    zone=zone
                )

                # =============================================
                # LABEL BUILD
                # =============================================
                label = self.label_builder.build(
                    tracker_id=tracker_id,
                    zone=zone,
                    speed=speed,
                    violations=violations
                )

                labels.append(label)

        # =====================================================
        # DRAWING
        # =====================================================
        annotated = frame.copy()

        annotated = self.box_annotator.annotate(
            scene=annotated,
            detections=detections
        )

        annotated = self.label_annotator.annotate(
            scene=annotated,
            detections=detections,
            labels=labels
        )

        # =====================================================
        # TRAJECTORIES
        # =====================================================
        self.draw_trajectories(
            annotated,
            detections
        )

        # =====================================================
        # ACCIDENT TEXT
        # =====================================================
        if self.accident_display_timer > 0:

            cv2.putText(
                annotated,
                "ACCIDENT DETECTED",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 0, 255),
                3
            )

            self.accident_display_timer -= 1

        # =====================================================
        # ROI DRAWING
        # =====================================================
        for roi in self.rois:

            if "points" not in roi:
                continue

            pts = np.array(
                roi["points"]
            )

            annotated = sv.draw_polygon(
                scene=annotated,
                polygon=pts,
                color=sv.Color(0, 255, 0),
                thickness=self.thickness
            )

            if "label" in roi and len(pts) > 0:

                x, y = pts[0]

                cv2.putText(
                    annotated,
                    roi["label"],
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

        return annotated, detections

    # =========================================================
    # TRACK COLOR
    # =========================================================
    def get_color(self, tracker_id):

        np.random.seed(
            int(tracker_id) % 10000
        )

        return tuple(
            int(x)
            for x in np.random.randint(
                0,
                255,
                3
            )
        )

    # =========================================================
    # DRAW TRAJECTORIES
    # =========================================================
    def draw_trajectories(
        self,
        frame,
        detections
    ):

        for tracker_id in detections.tracker_id:

            traj = self.trajectory.get_trajectory(
                tracker_id
            )

            if traj is None:
                continue

            points = traj["positions"]

            if points is None or len(points) < 2:
                continue

            points = list(points)[-20:]

            color = self.get_color(
                tracker_id
            )

            for i in range(1, len(points)):

                p1 = tuple(
                    map(
                        int,
                        points[i - 1]
                    )
                )

                p2 = tuple(
                    map(
                        int,
                        points[i]
                    )
                )

                cv2.line(
                    frame,
                    p1,
                    p2,
                    color,
                    2
                )