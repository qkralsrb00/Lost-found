# Camera.py
import sys
import cv2
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from datetime import datetime
from zoneinfo import ZoneInfo
import torch
import requests

# 환경 설정
SAVE_ROOT = "C:/2학년/2학기/김규동/img"  # 로컬 저장 경로
YOLO_MODEL_PATH = "C:/Users/pjh06/OneDrive/바탕 화면/김규동/runs/detect/wallet_detector6/weights/best.pt"
STREAMLIT_UPLOAD_URL = "http://localhost:8501/upload"  # Streamlit 업로드 엔드포인트

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("카메라 촬영 + 지갑 판정")
        self.resize(640, 520)

        # 버튼
        self.btn_capture = QPushButton("사진 찍기")
        self.btn_capture.clicked.connect(self.capture_image)

        # 이미지 표시
        self.label = QLabel()
        self.label.setFixedSize(640, 480)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_capture)
        self.setLayout(layout)

        # 카메라
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("카메라 열기 실패")
            sys.exit()

        self.timer_id = self.startTimer(30)

        # YOLO 모델 로드
        self.model = torch.hub.load('ultralytics/yolov8', 'custom', path=YOLO_MODEL_PATH, source='local')
        self.model.conf = 0.5  # 최소 신뢰도

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
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")
        save_dir = os.path.join(SAVE_ROOT, date_str)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{time_str}.png")

        cv2.imencode(".png", frame)[1].tofile(save_path)
        print(f"[저장 완료] {save_path}")

        # YOLO 지갑 판정
        results = self.model(frame)
        is_wallet = False
        if len(results[0].boxes) > 0:
            for i, cls in enumerate(results[0].boxes.cls.cpu().numpy()):
                if int(cls) == 0:  # 지갑 클래스
                    is_wallet = True
                    break

        # Streamlit 서버 업로드
        self.upload_to_streamlit(save_path, is_wallet)

    def upload_to_streamlit(self, image_path, is_wallet):
        try:
            with open(image_path, "rb") as f:
                files = {"file": f}
                data = {"is_wallet": str(is_wallet)}
                response = requests.post(STREAMLIT_UPLOAD_URL, files=files, data=data)
                if response.status_code == 200:
                    print(f"[Streamlit 업로드 완료] 지갑={is_wallet}")
                else:
                    print(f"[Streamlit 업로드 실패] 상태코드={response.status_code}")
        except Exception as e:
            print(f"[Streamlit 업로드 오류] {e}")

    def closeEvent(self, event):
        self.cap.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
