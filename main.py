import streamlit as st
from PIL import Image
import os
from datetime import datetime, timezone, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time

# 한국 표준시
KST = timezone(timedelta(hours=9))

# 이미지 폴더 루트
IMG_ROOT = "C:/2학년/2학기/김규동/img"

st.title("분실물 확인")

# 날짜 선택
selected_date = st.date_input("날짜 선택", datetime.now(tz=KST).date())
date_str = selected_date.strftime("%Y-%m-%d")
folder_path = os.path.join(IMG_ROOT, date_str)

# 사진 목록 관리
images = []

def load_images():
    global images
    images = []
    if os.path.exists(folder_path):
        for fname in sorted(os.listdir(folder_path)):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                # PIL로 이미지 열기 (한글 경로 가능)
                img_path = os.path.join(folder_path, fname)
                try:
                    img = Image.open(img_path)
                    images.append((fname, img))
                except:
                    continue
    else:
        images = []

load_images()

# 사진 없으면 안내
if not images:
    st.info("선택한 날짜에는 분실물이 없습니다.")
else:
    # 지갑 사진 먼저 보여주기
    # 여기서는 파일명에 'wallet' 들어가면 지갑이라고 가정
    wallet_images = [img for img in images if "wallet" in img[0].lower()]
    other_images = [img for img in images if "wallet" not in img[0].lower()]

    for fname, img in wallet_images + other_images:
        st.image(img, caption=fname, use_column_width=True)

# Watchdog으로 폴더 변화 감지
class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        # 새 파일이 생기면 Streamlit 다시 실행
        if event.src_path.lower().endswith((".png", ".jpg", ".jpeg")):
            st.experimental_rerun()

observer = Observer()
event_handler = ImageHandler()
observer.schedule(event_handler, folder_path if os.path.exists(folder_path) else IMG_ROOT, recursive=False)

def start_observer():
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

thread = threading.Thread(target=start_observer, daemon=True)
thread.start()
