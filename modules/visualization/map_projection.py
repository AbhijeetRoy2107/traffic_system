import numpy as np


# =========================================================
# GLOBAL VISUAL MAP PROJECTION
# =========================================================
class GlobalMapProjection:

    def __init__(self):

        # =================================================
        # VISUAL LANE OFFSETS
        # =================================================
        self.zone_offsets = {

            "lane_1": (-4, 0),
            "lane_2": (0, 0),
            "lane_3": (4, 0),
            "lane_4": (8, 0),
            "lane_5": (12, 0),

            "lane 1": (-4, 0),
            "lane 2": (0, 0),
            "lane 3": (4, 0),
            "lane 4": (8, 0),
            "lane 5": (12, 0),

            "sidewalk": (-8, 0)
        }

    # =====================================================
    # PROJECT POINT
    # =====================================================
    def project_point(

        self,

        world_point,

        zone
    ):

        if world_point is None:
            return None

        x, y = world_point

        offset_x, offset_y = (
            self.zone_offsets.get(
                zone,
                (0, 0)
            )
        )

        return np.array([

            x + offset_x,

            y + offset_y
        ])

    # =====================================================
    # PROJECT TRAJECTORY
    # =====================================================
    def project_trajectory(

        self,

        trajectory,

        zone
    ):

        projected = []

        for point in trajectory:

            projected_point = (
                self.project_point(
                    point,
                    zone
                )
            )

            if projected_point is not None:

                projected.append(
                    projected_point
                )

        return projected