import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from datetime import datetime, timezone, timedelta
from PyQt5.QtCore import QTimer
import os
import json
from ultralytics import YOLO
import subprocess
import time
# YOLO 모델 로드 (지갑 단일 클래스)
model = YOLO("model/best.pt")  # 학습한 best.pt 경로

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("카메라 촬영")
        self.resize(640, 520)

        self.btn_capture = QPushButton("사진 찍기")
        self.btn_capture.clicked.connect(self.capture_image)

        self.label = QLabel()
        self.label.setFixedSize(640, 480)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_capture)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("카메라 열기 실패")
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

        # 한국 표준시
        kst = datetime.now(timezone(timedelta(hours=9)))
        date_str = kst.strftime("%Y-%m-%d")
        time_str = kst.strftime("%H-%M-%S")

        save_dir = os.path.join(self.save_root, date_str)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{time_str}.png")
        cv2.imencode(".png", frame)[1].tofile(save_path)

        # YOLO로 지갑 여부 판단
        results = model.predict(frame, conf=0.4)
        wallet_present = False
        if results and len(results[0].boxes) > 0:
            wallet_present = True

        # 상태 저장
        status = {"filepath": save_path, "wallet": wallet_present, "timestamp": kst.strftime("%Y-%m-%d %H:%M:%S")}
        if os.path.exists(self.status_file):
            with open(self.status_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
        data.append(status)
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"사진 저장 완료: {save_path}, 지갑 여부: {wallet_present}")

        # ------------------- 3초 후 Git 자동 업로드 -------------------
        # QTimer.singleShot(3000, lambda: self.git_push())
        time.sleep(3)
        self.git_push()

    def git_push(self):
        try:
            repo_root = os.path.dirname(os.path.abspath(__file__))  # 프로젝트 루트

            subprocess.run(["git", "add", "."], cwd=repo_root)
            subprocess.run(["git", "commit", "-m", "자동 업로드 사진"], cwd=repo_root)
            subprocess.run(["git", "push"], cwd=repo_root)

            print("Git push 완료!")
        except Exception as e:
            print(f"Git push 중 오류 발생: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
