import streamlit as st
import json
import os
from PIL import Image
from datetime import datetime

st.title("지갑 사진 모니터링")

# 날짜 선택
selected_date = st.date_input("날짜 선택")

status_file = "status.json"
if os.path.exists(status_file):
    with open(status_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 선택한 날짜 필터링
    filtered = [d for d in data if d["timestamp"].startswith(selected_date.strftime("%Y-%m-%d"))]

    # 지갑 먼저
    filtered.sort(key=lambda x: not x["wallet"])

    for item in filtered:
        st.write(f"{item['timestamp']} - {'Wallet' if item['wallet'] else 'Other'}")
        img = Image.open(item["filepath"])
        st.image(img, use_column_width=True)
