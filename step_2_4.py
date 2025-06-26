import streamlit as st

import qrcode
from PIL import Image
import io
import socket

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from pathlib import Path
from step_1 import OUT_DIR  # 이전에 작성한 모듈을 불러옵니다.
from step_2_3 import OUT_2_3, read_text_and_draw_line, read_text_from_image
from liv_helper import translate_libre

# --- 이후에 QR 코드 생성 및 스트림릿 출력 ---

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

local_ip = get_local_ip()
app_url = f"http://{local_ip}:8501"

qr = qrcode.make(app_url)
buf = io.BytesIO()
qr.save(buf, format="PNG")
buf.seek(0)

st.title("✌ 인식률 체크 문자 인식 웹 앱")
st.markdown("### 📱 스마트폰으로 아래 QR코드를 스캔하여 접속하세요")
st.image(buf)
st.markdown(f"또는 아래 URL을 입력하세요: `{app_url}`")

uploaded = st.file_uploader("인식할 이미지를 선택하세요.")
if uploaded is not None:
    tmp_path = OUT_DIR / f"{Path(__file__).stem}.tmp"
    tmp_path.write_bytes(uploaded.getvalue())

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("원본 이미지")
        st.image(tmp_path.as_posix())
    with col_right:
        st.subheader("문자 인식 결과")
        with st.spinner(text="문자를 인식하는 중입니다..."):
            read_text_and_draw_line(tmp_path)
        st.image(OUT_2_3.as_posix())

    st.subheader("📝 인식된 텍스트 및 번역 결과")
    with st.spinner("텍스트를 번역하는 중입니다..."):
        texts = read_text_from_image(tmp_path)
        if texts:
            full_text = " ".join(texts)
            translated = translate_libre(full_text, source="en", target="ko")
            st.markdown(f"**🔹 {full_text}**<br/>➡️ {translated}", unsafe_allow_html=True)
        else:
            st.info("문자를 인식하지 못했습니다.")
