import numpy as np
import cv2

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions


class ModelAccidentEngine:

    def __init__(self):
        self.model = MobileNetV2(weights="imagenet")

        # threshold for "confusion"
        self.conf_threshold = 0.5

    def verify(self, frame, detections, candidates):

        confirmed_events = []

        for event in candidates:
            ids = event["objects"]

            # find boxes for these IDs
            idxs = [i for i, tid in enumerate(detections.tracker_id) if int(tid) in ids]

            if len(idxs) < 2:
                continue

            box1 = detections.xyxy[idxs[0]]
            box2 = detections.xyxy[idxs[1]]

            # combine boxes
            x1 = int(min(box1[0], box2[0]))
            y1 = int(min(box1[1], box2[1]))
            x2 = int(max(box1[2], box2[2]))
            y2 = int(max(box1[3], box2[3]))

            # add padding
            pad = 20
            x1 = max(0, x1 - pad)
            y1 = max(0, y1 - pad)
            x2 = min(frame.shape[1], x2 + pad)
            y2 = min(frame.shape[0], y2 + pad)

            crop = frame[y1:y2, x1:x2]

            if crop.size == 0:
                continue

            # preprocess
            crop = cv2.resize(crop, (224, 224))
            crop = np.expand_dims(crop, axis=0)
            crop = preprocess_input(crop)

            preds = self.model.predict(crop, verbose=0)

            top_pred = decode_predictions(preds, top=1)[0][0]
            confidence = float(top_pred[2])

            # DEBUG (optional)
            # print("Pred:", top_pred)

            # low confidence → unusual → accident
            if confidence < self.conf_threshold:
                confirmed_events.append({
                    "type": "CONFIRMED_ACCIDENT",
                    "objects": ids,
                    "zone": event["zone"]
                })

        return confirmed_events