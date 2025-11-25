import streamlit as st
import os
from datetime import datetime
from PIL import Image

selected_date = st.date_input("분실물 습득 날짜", datetime.today())

folder_path = os.path.join("img", selected_date.strftime("%Y-%m-%d"))

if os.path.exists(folder_path):
    img_files = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

    if img_files:
        st.write(f"총 {len(img_files)}개의 분실물 발견")

        for img_file in img_files:
            img_path = os.path.join(folder_path, img_file)
            image = Image.open(img_path)
            st.image(image, caption=img_file, use_column_width=True)
    else:
        st.warning("선택한 날짜에는 분실물이 없습니다.")
else:
    st.warning("선택한 날짜에는 분실물이 없습니다.")
