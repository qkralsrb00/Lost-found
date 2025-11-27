import streamlit as st
from PIL import Image
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

# 이미지 저장 루트
IMAGE_ROOT = "C:/2학년/2학기/김규동/img"

# Streamlit UI
st.title("분실물 확인")
selected_date = st.date_input("날짜 선택", datetime.now())

date_str = selected_date.strftime("%Y-%m-%d")
folder_path = os.path.join(IMAGE_ROOT, date_str)

# 이미지 리스트 초기화
image_files = []

# 파일 변경 감지 핸들러
class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        global image_files
        if event.is_directory:
            return
        if event.src_path.lower().endswith((".png", ".jpg", ".jpeg")):
            image_files.append(event.src_path)
            st.experimental_rerun()  # 새 이미지 생기면 갱신

# Watchdog 설정
observer = Observer()
if os.path.exists(folder_path):
    event_handler = ImageHandler()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()

# 해당 날짜 폴더가 없거나 비어있으면 안내
if not os.path.exists(folder_path):
    st.info("선택한 날짜에는 이미지가 없습니다.")
else:
    image_files = sorted(
        [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
    )
    if not image_files:
        st.info("선택한 날짜에는 이미지가 없습니다.")
    else:
        # 지갑 이미지 먼저
        wallet_images = [f for f in image_files if "wallet" in f.lower()]
        other_images = [f for f in image_files if "wallet" not in f.lower()]

        st.subheader("지갑 이미지")
        for img_path in wallet_images:
            img = Image.open(img_path)
            st.image(img, caption=os.path.basename(img_path))

        st.subheader("기타 이미지")
        for img_path in other_images:
            img = Image.open(img_path)
            st.image(img, caption=os.path.basename(img_path))

# 앱 종료 시 observer 정리
def stop_observer():
    observer.stop()
    observer.join()

st.on_session_end(stop_observer)
