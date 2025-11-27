import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from datetime import datetime
import os
import subprocess  # Git 명령 실행용

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("카메라 촬영")
        self.resize(640, 520)

        # 버튼
        self.btn_capture = QPushButton("사진 찍기")
        self.btn_capture.clicked.connect(self.capture_image)

        # 이미지 표시
        self.label = QLabel()
        self.label.setFixedSize(640, 480)

        # 레이아웃
        layout = QVBoxLayout()
        layout.addWidget(self.label)        
        layout.addWidget(self.btn_capture)
        self.setLayout(layout)

        # 카메라 열기
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("카메라 열기 실패")
            sys.exit()

        # 화면 업데이트
        self.timer_id = self.startTimer(30)  

        # 사진 저장 루트
        self.save_root = "C:/2학년/2학기/김규동/img"

        # Git 저장소 루트
        self.git_root = "C:/2학년/2학기/김규동"  # 여기 Git 저장소 루트로 변경

    def timerEvent(self, event):
        ret, frame = self.cap.read()
        if ret:
            # BGR → RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qt_image))

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H-%M-%S")
            save_dir = os.path.join(self.save_root, date_str)
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f"{time_str}.png")

            # 한글 경로 안전하게 저장
            cv2.imencode(".png", frame)[1].tofile(save_path)
            print(f"사진 저장 완료: {save_path}")

    def closeEvent(self, event):
        self.cap.release()

        # 🔹 Git 자동 업로드
        try:
            subprocess.run(["git", "add", "."], cwd=self.git_root, check=True)
            subprocess.run(["git", "commit", "-m", "자동 업로드 사진"], cwd=self.git_root, check=True)
            subprocess.run(["git", "push"], cwd=self.git_root, check=True)
            print("Git에 자동 푸시 완료")
        except subprocess.CalledProcessError as e:
            print("Git 자동 푸시 실패:", e)

        super().closeEvent(event)


# 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
