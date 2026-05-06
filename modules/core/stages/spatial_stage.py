import numpy as np
import supervision as sv
import cv2
from modules.core.stages.base_stage import (
    BaseStage
)

class SpatialStage(BaseStage):

    def __init__(
        self,
        rois,
        zone_logic,
        homography
    ):

        self.rois = rois

        self.zone_logic = zone_logic

        self.homography = homography

    # =====================================================
    # POINT IN POLYGON
    # =====================================================
    def point_in_polygon(
        self,
        point,
        polygon
    ):

        return cv2.pointPolygonTest(
            polygon,
            point,
            False
        ) >= 0

    # =====================================================
    # ROI FILTERING
    # =====================================================
    def filter_by_roi(
        self,
        detections
    ):

        if len(detections) == 0:
            return detections

        if not self.rois:
            return detections

        points = detections.get_anchors_coordinates(
            anchor=sv.Position.BOTTOM_CENTER
        )

        mask = []

        for pt in points:

            inside = False

            for roi in self.rois:

                polygon = np.array(
                    roi["points"]
                )

                if self.point_in_polygon(
                    tuple(pt),
                    polygon
                ):

                    inside = True
                    break

            mask.append(inside)

        detections = detections[
            np.array(mask)
        ]

        return detections

    # =====================================================
    # PROCESS
    # =====================================================
    def process(
        self,
        frame_data
    ):

        detections = frame_data.detections

        # =================================================
        # ROI FILTER
        # =================================================
        detections = self.filter_by_roi(
            detections
        )

        frame_data.detections = detections

        # =================================================
        # SPATIAL PROCESSING
        # =================================================
        if len(detections) == 0:

            return frame_data

        points = detections.get_anchors_coordinates(
            anchor=sv.Position.BOTTOM_CENTER
        )

        for i, tracker_id in enumerate(
            detections.tracker_id
        ):

            pt = tuple(points[i])

            # =============================================
            # ZONE
            # =============================================
            zone = self.zone_logic.get_zone(
                pt
            )

            frame_data.zones[
                tracker_id
            ] = zone

            # =============================================
            # WORLD POSITION
            # =============================================
            world_point = self.homography.to_world(
                pt,
                zone
            )

            frame_data.world_positions[
                tracker_id
            ] = world_point

        return frame_data