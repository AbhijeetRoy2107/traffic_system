import numpy as np
import cv2


class ZoneLogic:

    def __init__(self, rois):
        self.rois = rois

    def get_zone(self, point):
        """
        Returns first matching ROI label for a point
        """
        for roi in self.rois:
            if "points" not in roi:
                continue

            polygon = np.array(roi["points"])

            if cv2.pointPolygonTest(polygon, point, False) >= 0:
                return roi.get("label", None)

        return None

    def get_all_zones(self, point):
        """
        Returns all zones containing this point
        """
        zones = []

        for roi in self.rois:
            if "points" not in roi:
                continue

            polygon = np.array(roi["points"])

            if cv2.pointPolygonTest(polygon, point, False) >= 0:
                zones.append(roi.get("label", None))

        return zones