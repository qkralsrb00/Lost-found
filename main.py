import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import pytz

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time

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
        if event.src_path.endswith("status.json"):
            load_status()
        elif event.src_path.endswith(".png"):
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

# 백그라운드에서 watchdog 실행
threading.Thread(target=start_watcher, daemon=True).start()

st.title("📅 분실물 조회 시스템 (자동 업데이트)")

today_kst = datetime.now(KST).date()
selected_date = st.date_input("날짜 선택", value=today_kst)

# 필터링 & 정렬
filtered = [item for item in status_data if KST.localize(datetime.strptime(item["timestamp"], "%Y-%m-%d %H:%M:%S")).date() == selected_date]
filtered.sort(key=lambda x: not x["wallet"])

# 출력
if not filtered:
    st.warning("해당 날짜에 등록된 분실물이 없습니다.")
else:
    for item in filtered:
        st.image(str(Path(item["filepath"].replace("\\", "/"))), caption=f"지갑 여부: {item['wallet']} / {item['timestamp']}")
