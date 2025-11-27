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

# ----------------- 프로젝트 기준 디렉토리 -----------------
BASE_DIR = Path(__file__).parent
STATUS_FILE = BASE_DIR / "status.json"
IMG_DIR = BASE_DIR / "img"

# ----------------- 상태 저장 -----------------
status_data = []

def load_status():
    """status.json 파일 읽기"""
    global status_data
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                status_data = json.load(f)
        except json.JSONDecodeError:
            st.error("status.json 읽기 실패: JSON 형식 오류")
    else:
        status_data = []

# ----------------- Watchdog 이벤트 -----------------
class StatusHandler(FileSystemEventHandler):
    """status.json 및 이미지 변경 감지"""
    def on_modified(self, event):
        if event.src_path.endswith("status.json") or event.src_path.endswith(".png"):
            load_status()

# ----------------- Watchdog 스레드 -----------------
def start_watcher():
    event_handler = StatusHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(BASE_DIR), recursive=True)
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

# 중앙 정렬 타이틀
st.markdown("<h1 style='text-align: center;'>📅 분실물 조회 시스템</h1>", unsafe_allow_html=True)

# 오늘 날짜 기준 한국 시간
today_kst = datetime.now(KST).date()
selected_date = st.date_input("날짜 선택", value=today_kst)

# ----------------- 필터링 -----------------
wallet_items = []
other_items = []

for item in status_data:
    try:
        ts = datetime.strptime(item["timestamp"], "%Y-%m-%d %H:%M:%S")
        ts_kst = KST.localize(ts)
        if ts_kst.date() == selected_date:
            if item.get("wallet", False):
                wallet_items.append(item)
            else:
                other_items.append(item)
    except Exception as e:
        st.warning(f"잘못된 timestamp 형식: {item.get('timestamp')} / {e}")

# ----------------- 출력 -----------------
if not wallet_items and not other_items:
    st.warning("해당 날짜에 등록된 분실물이 없습니다.")
else:
    if wallet_items:
        st.subheader("👜 지갑 이미지")
        for item in wallet_items:
            filepath = BASE_DIR / Path(item["filepath"].replace("\\", "/"))  # 역슬래시 처리
            if filepath.exists():
                st.image(filepath, caption=f"지갑 여부: {item['wallet']} / {item['timestamp']}")
            else:
                st.warning(f"파일이 존재하지 않음: {filepath}")

    if other_items:
        st.subheader("📦 기타 이미지")
        for item in other_items:
            filepath = BASE_DIR / Path(item["filepath"].replace("\\", "/"))
            if filepath.exists():
                st.image(filepath, caption=f"지갑 여부: {item['wallet']} / {item['timestamp']}")
            else:
                st.warning(f"파일이 존재하지 않음: {filepath}")
