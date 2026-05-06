import torch
from ultralytics import YOLO
from config.config import (
    MODEL_PATH,
    IMG_SIZE,
    DEVICE
)


class Detector:
    def __init__(self):
        
        if DEVICE == "cuda" and torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

        self.model = YOLO(MODEL_PATH)

        # ✅ force model to device
        self.model.to(self.device)
        self.model.fuse()
        
        # frame count
        self.frame_count = 0
        
        # use half precision only on GPU
        self.half = self.device == "cuda"

        print(f"[Detector] Using device: {self.device}")

    def detect(self, frame):
        self.frame_count += 1
        result = self.model(
            frame,
            device=self.device,
            imgsz=IMG_SIZE,
            half=self.half,
            verbose=False
        )[0]

        return result