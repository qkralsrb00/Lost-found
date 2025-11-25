import streamlit as st
import os
from datetime import datetime
from PIL import Image

# 1️⃣ Streamlit 달력 위젯
selected_date = st.date_input("사진을 보고 싶은 날짜 선택", datetime.today())

# 2️⃣ 선택된 날짜 폴더 경로
folder_path = os.path.join("img", selected_date.strftime("%Y-%m-%d"))

if os.path.exists(folder_path):
    # 3️⃣ 폴더 안의 모든 이미지 파일 가져오기
    img_files = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

    if img_files:
        st.write(f"총 {len(img_files)}장 이미지 발견")

        # 4️⃣ 이미지 순서대로 표시
        for img_file in img_files:
            img_path = os.path.join(folder_path, img_file)
            image = Image.open(img_path)
            st.image(image, caption=img_file, use_column_width=True)
    else:
        st.warning("선택한 날짜 폴더에는 이미지가 없습니다.")
else:
    st.warning("선택한 날짜 폴더가 존재하지 않습니다.")
