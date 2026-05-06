import cv2
import numpy as np

from modules.visualization.map_projection import (
    GlobalMapProjection
)

class BirdEyeVisualizer:

    def __init__(
        self,
        width=1200,
        height=900,
        scale=30,
        offset_x=500,
        offset_y=100,
        show_grid=True
    ):

        self.width = width
        self.height = height

        self.scale = scale

        self.offset_x = offset_x
        self.offset_y = offset_y

        self.show_grid = show_grid

        self.bg_color = (30, 30, 30)

        self.grid_color = (55, 55, 55)

        self.text_color = (255, 255, 255)

        # =================================================
        # ROI COLORS
        # =================================================
        self.roi_colors = [

            (0, 180, 255),
            (0, 255, 180),
            (255, 180, 0),
            (180, 0, 255),
            (255, 80, 80)
        ]
        self.map_projection = (
            GlobalMapProjection()
        )

    # =====================================================
    # CREATE EMPTY CANVAS
    # =====================================================
    def create_canvas(self):

        canvas = np.full(
            (
                self.height,
                self.width,
                3
            ),
            self.bg_color,
            dtype=np.uint8
        )

        if self.show_grid:

            spacing = 50

            for x in range(0, self.width, spacing):

                cv2.line(
                    canvas,
                    (x, 0),
                    (x, self.height),
                    self.grid_color,
                    1
                )

            for y in range(0, self.height, spacing):

                cv2.line(
                    canvas,
                    (0, y),
                    (self.width, y),
                    self.grid_color,
                    1
                )

        return canvas

    # =====================================================
    # WORLD -> CANVAS
    # =====================================================
    def world_to_canvas(self, world_point):

        wx, wy = world_point

        x = int(wx * self.scale)

        y = int(wy * self.scale)

        x += self.offset_x

        # normal Y orientation
        y += self.offset_y

        return x, y

    # =====================================================
    # DRAW ROI LABEL ONLY
    # =====================================================
    def draw_roi(

        self,

        canvas,

        roi,

        homography,

        color=(0, 180, 255)
    ):

        points = roi.get(
            "points",
            []
        )

        zone_name = roi.get(
            "label",
            "ZONE"
        )

        if len(points) < 3:
            return

        world_pts = []

        # =================================================
        # IMAGE -> WORLD
        # =================================================
        for pt in points:

            world_pt = homography.to_world(
                tuple(pt),
                zone_name
            )
            
            world_pt = self.map_projection.project_point(

                world_pt,

                zone_name
            )

            if world_pt is None:
                continue

            x, y = self.world_to_canvas(
                world_pt
            )

            world_pts.append([x, y])

        if len(world_pts) < 3:
            return

        polygon = np.array(
            world_pts,
            dtype=np.int32
        )
        
        # =================================================
        # THIN ROI BORDER
        # =================================================
        cv2.polylines(

            canvas,

            [polygon],

            isClosed=True,

            color=color,

            thickness=1
        )       

        # =================================================
        # CENTROID
        # =================================================
        centroid = np.mean(
            polygon,
            axis=0
        ).astype(int)

        # =================================================
        # SMALL MARKER
        # =================================================
        cv2.circle(

            canvas,

            tuple(centroid),

            6,

            color,

            -1
        )

        # =================================================
        # LABEL
        # =================================================
        cv2.putText(

            canvas,

            zone_name,

            (
                centroid[0] + 10,
                centroid[1]
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            color,

            2
        )

    # =====================================================
    # DRAW OBJECT
    # =====================================================
    def draw_object(
        self,
        canvas,
        world_point,
        tracker_id,
        speed=None,
        color=(0, 255, 0)
    ):

        if world_point is None:
            return

        x, y = self.world_to_canvas(
            world_point
        )

        if (
            x < 0
            or x >= self.width
            or y < 0
            or y >= self.height
        ):
            return

        cv2.circle(
            canvas,
            (x, y),
            6,
            color,
            -1
        )

        label = f"#{tracker_id}"

        if speed is not None:
            label += f" | {int(speed)} km/h"

        cv2.putText(
            canvas,
            label,
            (x + 10, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.text_color,
            1
        )

    # =====================================================
    # DRAW TRAJECTORY
    # =====================================================
    def draw_trajectory(
        self,
        canvas,
        world_points,
        color=(255, 100, 0)
    ):

        if len(world_points) < 2:
            return

        pts = []

        # =============================================
        # ONLY RECENT TRAJECTORY
        # =============================================
        recent_points = world_points[-8:]

        for pt in recent_points:

            if pt is None:
                continue

            x, y = self.world_to_canvas(pt)

            pts.append((x, y))

        if len(pts) < 2:
            return

        for i in range(1, len(pts)):

            cv2.line(
                canvas,
                pts[i - 1],
                pts[i],
                color,
                2
            )

    # =====================================================
    # MAIN RENDER
    # =====================================================
    def render(

        self,

        objects,

        rois=None,

        homography=None
    ):

        canvas = self.create_canvas()

        # =================================================
        # DRAW ROI LABELS
        # =================================================
        if (

            rois is not None
            and homography is not None
        ):

            for i, roi in enumerate(rois):

                color = self.roi_colors[
                    i % len(self.roi_colors)
                ]

                self.draw_roi(

                    canvas=canvas,

                    roi=roi,

                    homography=homography,

                    color=color
                )

        # =================================================
        # DRAW OBJECTS
        # =================================================
        for obj in objects:

            self.draw_object(

                canvas=canvas,

                world_point=obj.get("world"),

                tracker_id=obj.get("id"),

                speed=obj.get("speed"),

                color=obj.get(
                    "color",
                    (0, 255, 0)
                )
            )

            self.draw_trajectory(

                canvas=canvas,

                world_points=obj.get(
                    "trajectory",
                    []
                ),

                color=obj.get(
                    "color",
                    (255, 100, 0)
                )
            )

        return canvas