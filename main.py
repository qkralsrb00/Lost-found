import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import pytz
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ----------------- 시간대 -----------------
KST = pytz.timezone("Asia/Seoul")

# ----------------- 상태 저장 -----------------
STATUS_FILE = "status.json"
status_data = []

def load_status():
    global status_data
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        status_data = json.load(f)

# ----------------- Watchdog 이벤트 -----------------
class StatusHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("status.json") or event.src_path.endswith(".png"):
            load_status()

# ----------------- Watchdog 스레드 -----------------
def start_watcher():
    event_handler = StatusHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# ----------------- Streamlit UI -----------------
load_status()
threading.Thread(target=start_watcher, daemon=True).start()
st.set_page_config(page_title="분실물 확인", layout="wide")
st.title("📅 분실물 조회 시스템")

today_kst = datetime.now(KST).date()
selected_date = st.date_input("날짜 선택", value=today_kst)

# 필터링
wallet_items = []
other_items = []

for item in status_data:
    ts = datetime.strptime(item["timestamp"], "%Y-%m-%d %H:%M:%S")
    ts_kst = KST.localize(ts)
    if ts_kst.date() == selected_date:
        if item["wallet"]:
            wallet_items.append(item)
        else:
            other_items.append(item)

# ----------------- 출력 -----------------
if not wallet_items and not other_items:
    st.info("해당 날짜에 등록된 분실물이 없습니다.")
else:
    if wallet_items:
        st.subheader("👜 지갑 이미지")
        for item in wallet_items:
            st.image(str(Path(item["filepath"].replace("\\", "/"))))
    if other_items:
        st.subheader("📦 기타 이미지")
        for item in other_items:
            st.image(str(Path(item["filepath"].replace("\\", "/"))))
