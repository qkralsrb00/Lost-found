import streamlit as st
import time
import json
from datetime import datetime
import pytz
from pathlib import Path

KST = pytz.timezone("Asia/Seoul")
STATUS_FILE = "status.json"

def load_status():
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 자동 재로드
reload_interval = 3  # 초 단위
last_reload = 0

if 'status_data' not in st.session_state:
    st.session_state.status_data = load_status()

# 강제 재로드
if time.time() - last_reload > reload_interval:
    st.session_state.status_data = load_status()
    last_reload = time.time()

# 선택 UI
today_kst = datetime.now(KST).date()
selected_date = st.date_input("날짜 선택", value=today_kst)

# 필터링
wallet_items = []
other_items = []

for item in st.session_state.status_data:
    ts = datetime.strptime(item["timestamp"], "%Y-%m-%d %H:%M:%S")
    ts_kst = KST.localize(ts)
    if ts_kst.date() == selected_date:
        if item["wallet"]:
            wallet_items.append(item)
        else:
            other_items.append(item)

# 출력
if wallet_items:
    st.subheader("👜 지갑 이미지")
    for item in wallet_items:
        st.image(str(Path(item["filepath"].replace("\\", "/"))),
                 caption=f"지갑 여부: {item['wallet']} / {item['timestamp']}")
if other_items:
    st.subheader("📦 기타 이미지")
    for item in other_items:
        st.image(str(Path(item["filepath"].replace("\\", "/"))),
                 caption=f"지갑 여부: {item['wallet']} / {item['timestamp']}")
