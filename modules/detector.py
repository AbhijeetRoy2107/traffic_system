import torch
from ultralytics import YOLO
from config.config import MODEL_PATH, IMG_SIZE


class Detector:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = YOLO(MODEL_PATH)

        # ✅ force model to device
        self.model.to(self.device)

        # use half precision only on GPU
        self.half = self.device == "cuda"

        print(f"[Detector] Using device: {self.device}")

    def detect(self, frame):
        result = self.model(
            frame,
            device=self.device,
            imgsz=IMG_SIZE,
            half=self.half,
            verbose=False
        )[0]

        return result