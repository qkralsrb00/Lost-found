# streamlit_wallet_viewer.py
import streamlit as st
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
import os
import cv2
import numpy as np
from datetime import datetime
import pytz

# YOLO 모델 로드 (예: yolov8)
from ultralytics import YOLO
model = YOLO("runs/detect/wallet_detector/weights/best.pt")  # 학습한 지갑 단일 클래스 모델

# 이미지 저장 폴더
IMG_ROOT = "C:/2학년/2학기/김규동/img"

# 지갑 사진 우선 리스트
wallet_images = []
other_images = []

# Streamlit UI
st.title("실시간 지갑 확인")
date_selected = st.date_input("날짜 선택", datetime.now().date())

container = st.empty()

# 폴더 감시용 이벤트 핸들러
class ImgHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith((".png", ".jpg", ".jpeg")):
            process_image(event.src_path)

# 이미지 처리
def process_image(path):
    img = cv2.imread(path)
    results = model(img)[0]

    # 지갑 단일 클래스 = class 0
    is_wallet = any(int(box.cls) == 0 for box in results.boxes)
    
    # 한국 표준시 기준 파일 시간
    tz = pytz.timezone("Asia/Seoul")
    file_time = datetime.fromtimestamp(os.path.getmtime(path), tz=tz)

    # 선택된 날짜와 맞는지 확인
    if file_time.date() != date_selected:
        return

    if is_wallet:
        wallet_images.insert(0, path)  # 맨 위
    else:
        other_images.append(path)      # 아래

# Watchdog 스레드
def start_watchdog():
    event_handler = ImgHandler()
    observer = Observer()
    observer.schedule(event_handler, IMG_ROOT, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Watchdog 별도 스레드 실행
threading.Thread(target=start_watchdog, daemon=True).start()

# Streamlit 갱신
while True:
    all_images = wallet_images + other_images
    with container.container():
        for img_path in all_images:
            st.image(img_path, use_column_width=True)
    time.sleep(1)
