import torch
from ultralytics import YOLO
from utils import get_model_path

class PyTorchDetector:
    def __init__(self, model_path=None):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Model path'i otomatik belirle
        if model_path is None:
            model_path = get_model_path()
        
        try:
            self.model = YOLO(model_path)
            self.model.to(self.device)
            print(f"[MODEL] {model_path} yüklendi ({self.device})")
        except Exception as e:
            print(f"[MODEL HATASI] Model yüklenemedi: {e}")
            raise

    def detect(self, image):
        try:
            results = self.model(image)
            detections = []
            for r in results:
                boxes = r.boxes.xyxy.cpu().numpy()
                scores = r.boxes.conf.cpu().numpy()
                classes = r.boxes.cls.cpu().numpy()
                for (box, score, cls) in zip(boxes, scores, classes):
                    x1, y1, x2, y2 = box.astype(int)
                    detections.append({
                        'bbox': (x1, y1, x2, y2),
                        'score': float(score),
                        'class': self.model.names[int(cls)]
                    })
            return detections
        except Exception as e:
            print(f"[DETECTION HATASI] : {e}")
            return []