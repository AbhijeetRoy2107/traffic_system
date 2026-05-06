import numpy as np
import cv2
import json
import os


class HomographyManager:

    def __init__(self, video_path):

        self.transforms = {}

        filename = os.path.basename(video_path)
        path = "homography/homography_data.json"

        if not os.path.exists(path):
            return

        data = json.load(open(path))

        if filename not in data:
            return

        for item in data[filename]:
            label = item["label"]

            src = np.array(item["src"], dtype=np.float32)
            dst = np.array(item["dst"], dtype=np.float32)

            H = cv2.getPerspectiveTransform(src, dst)

            self.transforms[label] = H

    def to_world(self, point, zone):

        if zone not in self.transforms:
            return None

        H = self.transforms[zone]

        pt = np.array([[point]], dtype=np.float32)
        world = cv2.perspectiveTransform(pt, H)

        return world[0][0]
