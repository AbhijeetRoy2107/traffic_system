import cv2
import numpy as np
import supervision as sv

from config.config import (
    MAX_TRAJECTORY_POINTS
)

from modules.core.stages.base_stage import (
    BaseStage
)

class VisualizationStage(BaseStage):

    def __init__(

        self,

        video_info,

        trajectory_manager,

        label_builder,

        birdeye,

        box_annotator,

        label_annotator,

        rois
    ):

        self.video_info = video_info

        self.trajectory = trajectory_manager

        self.label_builder = label_builder

        self.birdeye = birdeye

        self.box_annotator = box_annotator

        self.label_annotator = label_annotator

        self.rois = rois

        self.thickness = (
            sv.calculate_optimal_line_thickness(
                video_info.resolution_wh
            )
        )

    # =====================================================
    # TRACK COLOR
    # =====================================================
    def get_color(
        self,
        tracker_id
    ):

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

    # =====================================================
    # DRAW TRAJECTORIES
    # =====================================================
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

            if len(points) < 2:
                continue

            points = list(points)[
                -MAX_TRAJECTORY_POINTS:
            ]

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

    # =====================================================
    # DRAW ROIS
    # =====================================================
    def draw_rois(
        self,
        frame
    ):

        for roi in self.rois:

            pts = np.array(
                roi["points"]
            )

            frame = sv.draw_polygon(

                scene=frame,

                polygon=pts,

                color=sv.Color(0, 255, 0),

                thickness=self.thickness
            )

            if len(pts) > 0:

                x, y = pts[0]

                cv2.putText(

                    frame,

                    roi["label"],

                    (x, y - 10),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.6,

                    (255, 255, 255),

                    2
                )

        return frame

    # =====================================================
    # PROCESS
    # =====================================================
    def process(

        self,

        frame,

        frame_data,

        accident_display_timer
    ):

        detections = frame_data.detections

        labels = []

        frame_data.bird_eye_objects = []

        # =================================================
        # PROCESS TRACKS
        # =================================================
        if len(detections) > 0:

            for i, tracker_id in enumerate(
                detections.tracker_id
            ):

                zone = frame_data.zones.get(
                    tracker_id
                )

                world_point = (
                    frame_data.world_positions.get(
                        tracker_id
                    )
                )

                speed = frame_data.speeds.get(
                    tracker_id
                )

                world_traj = frame_data.metadata[
                    "world_trajectories"
                ].get(
                    tracker_id,
                    []
                )

                color = self.get_color(
                    tracker_id
                )

                # =========================================
                # BIRD-EYE OBJECT
                # =========================================
                frame_data.bird_eye_objects.append({

                    "id": tracker_id,

                    "world": world_point,

                    "speed": speed,

                    "trajectory": world_traj,

                    "color": color
                })

                # =========================================
                # LABEL
                # =========================================
                label = self.label_builder.build(

                    tracker_id=tracker_id,

                    zone=zone,

                    speed=speed,

                    violations=[]
                )

                labels.append(label)

        # =================================================
        # BIRD-EYE
        # =================================================
        bird_frame = self.birdeye.render(

            frame_data.bird_eye_objects
        )

        # =================================================
        # NORMAL VISUALIZATION
        # =================================================
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

        self.draw_trajectories(

            annotated,

            detections
        )

        # =================================================
        # ACCIDENT DISPLAY
        # =================================================
        if accident_display_timer > 0:

            cv2.putText(

                annotated,

                "ACCIDENT DETECTED",

                (20, 50),

                cv2.FONT_HERSHEY_SIMPLEX,

                1.2,

                (0, 0, 255),

                3
            )

        # =================================================
        # DRAW ROIS
        # =================================================
        annotated = self.draw_rois(
            annotated
        )

        return annotated, bird_frame