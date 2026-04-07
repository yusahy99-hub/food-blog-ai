import io
import os
import zipfile
import requests
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="배경 제거", page_icon="✂️")

from auth import check_password
if not check_password():
    st.stop()

st.markdown("""
<style>
    .stMainBlockContainer { max-width: 720px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("✂️ 배경 제거")
st.caption("사진을 올리면 배경을 자동으로 제거합니다 (누끼 따기, 월 50장 무료)")


def get_removebg_key():
    key = os.environ.get("REMOVEBG_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("REMOVEBG_API_KEY", "")
        except Exception:
            pass
    return key


def remove_bg(image_bytes, api_key):
    """remove.bg API로 배경 제거"""
    resp = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": ("image.png", image_bytes, "image/png")},
        data={"size": "auto"},
        headers={"X-Api-Key": api_key},
    )
    if resp.status_code == 200:
        return resp.content
    else:
        raise Exception(f"remove.bg 오류 ({resp.status_code}): {resp.json().get('errors', [{}])[0].get('title', '알 수 없는 오류')}")


api_key = get_removebg_key()

if not api_key:
    st.warning("remove.bg API Key가 필요합니다.")
    st.markdown("""
    **무료 API 키 발급 방법:**
    1. [remove.bg](https://www.remove.bg/api) 접속
    2. 회원가입 (무료)
    3. API Key 복사
    4. Streamlit Cloud Secrets 또는 .env에 추가:
    ```
    REMOVEBG_API_KEY = "발급받은키"
    ```
    **무료 월 50장** 사용 가능합니다.
    """)
    st.stop()

uploaded_files = st.file_uploader(
    "사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
)

if uploaded_files:
    if st.button("✂️ 배경 제거 실행", type="primary", use_container_width=True):
        results = []

        for f in uploaded_files:
            f.seek(0)
            img = Image.open(f).convert("RGBA")

            st.divider()
            st.subheader(f.name)

            col_orig, col_result = st.columns(2)
            with col_orig:
                st.markdown("**원본**")
                st.image(img, use_container_width=True)

            with st.spinner(f"{f.name} 배경 제거 중..."):
                try:
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="PNG")
                    output_bytes = remove_bg(img_bytes.getvalue(), api_key)
                    result_img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

                    with col_result:
                        st.markdown("**배경 제거**")
                        st.image(result_img, use_container_width=True)

                    out_name = f"{f.name.rsplit('.', 1)[0]}_nobg.png"
                    buf = io.BytesIO()
                    result_img.save(buf, format="PNG")
                    results.append((out_name, buf.getvalue()))
                except Exception as e:
                    with col_result:
                        st.error(f"오류: {e}")

        if results:
            st.divider()
            if len(results) == 1:
                name, data = results[0]
                st.download_button("📥 다운로드 (PNG)", data, name, "image/png",
                                   use_container_width=True)
            else:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for name, data in results:
                        zf.writestr(name, data)
                st.download_button(f"📥 전체 다운로드 (ZIP, {len(results)}장)",
                                   zip_buf.getvalue(), "nobg_photos.zip", "application/zip",
                                   use_container_width=True)

                with st.expander("개별 다운로드"):
                    for name, data in results:
                        st.download_button(f"📥 {name}", data, name, "image/png",
                                           key=f"dl_{name}")
