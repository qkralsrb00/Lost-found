import sys
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from datetime import datetime, timezone, timedelta
from PyQt5.QtCore import QTimer

import json
from ultralytics import YOLO
import subprocess
import time
model = YOLO("model/best.pt") 

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("분실물 촬영")
        self.resize(640, 520)

        self.btn_capture = QPushButton("사진 찍기")
        self.btn_capture.clicked.connect(self.capture_image)

        self.label = QLabel()
        self.label.setFixedSize(640, 480)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_capture)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(2)
        if not self.cap.isOpened():
            raise RuntimeError("카메라 없음")
            sys.exit()

        self.timer_id = self.startTimer(30)
        self.save_root = "img"
        self.status_file = "status.json"

    def timerEvent(self, event):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qt_image))

    def capture_image(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        kst = datetime.now(timezone(timedelta(hours=9)))
        date_str = kst.strftime("%Y-%m-%d")
        time_str = kst.strftime("%H-%M-%S")

        save_dir = os.path.join(self.save_root, date_str)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{time_str}.png")
        cv2.imencode(".png", frame)[1].tofile(save_path)

        results = model.predict(frame, conf=0.05)
        wallet_present = False
        if results and len(results[0].boxes) > 0:
            wallet_present = True

        status = {"filepath": save_path, "wallet": wallet_present, "timestamp": kst.strftime("%Y-%m-%d %H:%M:%S")}
        if os.path.exists(self.status_file):
            with open(self.status_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
        data.append(status)
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


        # QTimer.singleShot(3000, lambda: self.git_push())
        time.sleep(3)
        self.git_push()

    def git_push(self):
        try:
            repo_root = os.path.dirname(os.path.abspath(__file__))

            subprocess.run(["git", "add", "."], cwd=repo_root)
            subprocess.run(["git", "commit", "-m", "upload img"], cwd=repo_root)
            subprocess.run(["git", "push"], cwd=repo_root)


        except Exception as e:
            print(e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())


