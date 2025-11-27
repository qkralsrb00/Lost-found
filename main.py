import streamlit as st
from datetime import datetime
from pathlib import Path
from PIL import Image

# 업로드 이미지 저장 루트
UPLOAD_ROOT = Path("C:/2학년/2학기/김규동/img_streamlit")

st.set_page_config(page_title="지갑 이미지 뷰어", layout="wide")

# 업로드 처리
uploaded_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])
is_wallet = st.radio("지갑 여부", options=["True", "False"], index=1)

if uploaded_file:
    date_str = datetime.now().strftime("%Y-%m-%d")
    save_dir = UPLOAD_ROOT / date_str
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / uploaded_file.name
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # 지갑 여부 파일로 저장
    wallet_flag_path = save_dir / f"{uploaded_file.name}.wallet"
    with open(wallet_flag_path, "w") as f:
        f.write(is_wallet)

# 달력으로 날짜 선택
selected_date = st.date_input("날짜 선택", datetime.now())
date_folder = UPLOAD_ROOT / selected_date.strftime("%Y-%m-%d")

images = []
wallet_images = []
if date_folder.exists():
    for file in date_folder.iterdir():
        if file.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            flag_file = file.with_suffix(file.suffix + ".wallet")
            is_wallet_img = flag_file.exists() and flag_file.read_text() == "True"
            if is_wallet_img:
                wallet_images.append(file)
            else:
                images.append(file)

# 지갑 이미지는 항상 상단에
st.write("### 지갑 이미지")
for img_path in wallet_images:
    st.image(Image.open(img_path), use_column_width=True)

st.write("### 기타 이미지")
for img_path in images:
    st.image(Image.open(img_path), use_column_width=True)
