import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import pytz

# -------------------------
# 한국 표준시
# -------------------------
KST = pytz.timezone("Asia/Seoul")

# -------------------------
# 경로
# -------------------------
BASE_DIR = Path(__file__).parent
STATUS_FILE = BASE_DIR / "status.json"

# -------------------------
# 상태 로딩
# -------------------------
def load_status():
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("JSON 형식 오류")
            return []
    return []

# -------------------------
# Streamlit 설정
# -------------------------
st.set_page_config(page_title="대건고 분실물 찾기", layout="wide")
st.markdown("<h1 style='text-align: center;'>📅 대건고 분실물 조회</h1>", unsafe_allow_html=True)

# -------------------------
# 화면 전환 상태 관리
# -------------------------
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "daily"  # daily / all

def switch_to_all():
    st.session_state.view_mode = "all"

def switch_to_daily():
    st.session_state.view_mode = "daily"

# -------------------------
# 날짜 선택
# -------------------------
today_kst = datetime.now(KST).date()
selected_date = st.date_input("날짜 선택", value=today_kst)

# -------------------------
# 데이터 로딩
# -------------------------
status_data = load_status()

# 날짜별 분류
wallet_items = []
other_items = []

for item in status_data:
    try:
        ts = datetime.strptime(item["timestamp"], "%Y-%m-%d %H:%M:%S")
        ts_kst = KST.localize(ts)
        if st.session_state.view_mode == "daily":
            if ts_kst.date() != selected_date:
                continue
        if item.get("wallet", False):
            wallet_items.append(item)
        else:
            other_items.append(item)
    except Exception as e:
        st.warning(f"잘못된 timestamp 형식: {item.get('timestamp')} / {e}")

# -------------------------
# 화면 출력
# -------------------------
if st.session_state.view_mode == "daily":
    st.subheader(f"📅 {selected_date} 분실물 목록")
    st.button("📂 전체 목록 보기", on_click=switch_to_all)
else:
    st.subheader("📂 전체 분실물 목록")
    st.button("⬅ 날짜별 보기", on_click=switch_to_daily)

# -------------------------
# 지갑 이미지 먼저
# -------------------------
if wallet_items:
    st.subheader("👛 지갑 이미지")
    for item in wallet_items:
        filepath = BASE_DIR / Path(item["filepath"].replace("\\", "/"))
        if filepath.exists():
            st.image(filepath, caption=f"지갑 여부: {item['wallet']} / {item['timestamp']}")
        else:
            st.warning(f"파일이 존재하지 않음: {filepath}")

# -------------------------
# 기타 이미지
# -------------------------
if other_items:
    st.subheader("📦 기타 이미지")
    for item in other_items:
        filepath = BASE_DIR / Path(item["filepath"].replace("\\", "/"))
        if filepath.exists():
            st.image(filepath, caption=f"지갑 여부: {item['wallet']} / {item['timestamp']}")
        else:
            st.warning(f"파일이 존재하지 않음: {filepath}")

# -------------------------
# 오늘/전체 모두 없는 경우
# -------------------------
if not wallet_items and not other_items:
    st.info("해당 날짜에 등록된 분실물이 없습니다.")
