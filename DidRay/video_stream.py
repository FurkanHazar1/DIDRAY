import cv2
import time
import os
import pygame
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
from detector_pt import PyTorchDetector
from utils import get_alarm_path

# Tehlike seviyeleri ve renkler
DANGER_LEVELS = {
    'Çok Yüksek': ['Gun'],
    'Yüksek': ['Folding_Knife', 'Straight_Knife'],
    'Orta': ['Multi-tool_Knife', 'Utility_Knife'],
    'Düşük': ['Pliers', 'Scissor', 'Wrench']
}

LEVEL_COLORS = {
    'Çok Yüksek': (255, 0, 255),
    'Yüksek': (0, 0, 255),
    'Orta': (0, 165, 255),
    'Düşük': (0, 255, 0)
}

def get_danger_level(class_name):
    for level, classes in DANGER_LEVELS.items():
        if class_name in classes:
            return level
    return 'Düşük'

class VideoStreamThread(QThread):
    frame_updated = pyqtSignal(object)
    detection_updated = pyqtSignal(list)

    def __init__(self, model_path=None, db_manager=None, operator=None, role=None, source=0):
        super().__init__()
        self.detector = PyTorchDetector(model_path)
        self.source = source
        self.running = True
        self.db = db_manager
        self.last_saved = 0
        self.paused = False
        self.alarm_playing = False
        self.operator = operator
        self.role = role
        self.alarm_sound = None
        self.alarm_channel = None

        # Alarm sistemi - güvenli yükleme
        try:
            pygame.mixer.init()
            alarm_path = get_alarm_path()
            if alarm_path and os.path.exists(alarm_path):
                self.alarm_sound = pygame.mixer.Sound(alarm_path)
                self.alarm_channel = pygame.mixer.Channel(1)
                print(f"[ALARM] Ses dosyası yüklendi: {alarm_path}")
            else:
                print("[ALARM] Ses dosyası bulunamadı - sessiz modda çalışacak")
        except Exception as e:
            print(f"[ALARM HATASI] Ses sistemi başlatılamadı: {e}")

    def pause(self):
        self.paused = True
        self.stop_alarm()

    def resume(self):
        self.paused = False

    def start_alarm(self):
        if not self.alarm_playing and not self.paused and self.alarm_sound and self.alarm_channel:
            try:
                self.alarm_channel.play(self.alarm_sound, loops=-1)
                self.alarm_playing = True
            except Exception as e:
                print("[ALARM BAŞLATMA HATASI]", e)

    def stop_alarm(self):
        if self.alarm_playing and self.alarm_channel:
            try:
                self.alarm_channel.stop()
                self.alarm_playing = False
            except Exception as e:
                print("[ALARM DURDURMA HATASI]", e)

    def run(self):
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            print("[HATA] Video açılamadı.")
            return

        while self.running and cap.isOpened():
            if self.paused:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret:
                break

            img = frame.copy()
            detections = self.detector.detect(frame)

            bboxes = []
            confidences = []
            class_names = []

            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                cls_name = det['class']
                conf = det['score']

                bboxes.append([x1, y1, x2, y2])
                confidences.append(conf)
                class_names.append(cls_name)

                level = get_danger_level(cls_name)
                color = LEVEL_COLORS[level]

                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(img, f"{cls_name} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Kritik nesne kontrolü
            kritik_var = any(get_danger_level(cls) == "Çok Yüksek" for cls in class_names)
            if kritik_var and not self.paused:
                self.start_alarm()
            else:
                self.stop_alarm()

            self.detection_updated.emit(detections)
            self.frame_updated.emit(img)

            # Kaydetme
            now = time.time()
            if detections and (now - self.last_saved > 5):
                self.last_saved = now
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"results/video_frame_{timestamp}.jpg"
                os.makedirs("results", exist_ok=True)
                cv2.imwrite(save_path, img)

                if self.db:
                    self.db.insert_detection(
                        classes=class_names,
                        image_path=save_path,
                        mode="video",
                        bboxes=bboxes,
                        confidences=confidences,
                        operator=self.operator,
                        role=self.role
                    )
                    self.db.add_log(self.operator, f"Video tespiti kaydedildi: {class_names}")

        cap.release()
        self.stop_alarm()

    def stop(self):
        self.running = False
        self.stop_alarm()
        self.quit()
        self.wait()