import io
import zipfile
import streamlit as st
from PIL import Image

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
st.caption("사진을 올리면 배경을 자동으로 제거합니다 (누끼 따기)")

# rembg 설치 여부 확인
try:
    from rembg import remove
    rembg_available = True
except ImportError:
    rembg_available = False

if not rembg_available:
    st.warning("이 기능은 로컬 환경에서만 사용 가능합니다.")
    st.info("로컬에서 사용하려면: `pip install rembg onnxruntime` 설치 후 실행하세요.")
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
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                output_bytes = remove(img_bytes.read())
                result_img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

            with col_result:
                st.markdown("**배경 제거**")
                st.image(result_img, use_container_width=True)

            out_name = f"{f.name.rsplit('.', 1)[0]}_nobg.png"
            buf = io.BytesIO()
            result_img.save(buf, format="PNG")
            results.append((out_name, buf.getvalue()))

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
