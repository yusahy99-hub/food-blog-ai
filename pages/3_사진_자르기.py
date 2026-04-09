import io
import zipfile
import streamlit as st
from PIL import Image


st.markdown("""
<style>
    .stMainBlockContainer { max-width: 800px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("✂️ 사진 자르기")
st.caption("사진을 올리면 블로그/인스타 업로드용으로 통일된 사이즈로 잘라줍니다")

# 사이즈 프리셋
PRESETS = {
    "인스타 정사각형 (1:1)": {"size": (1080, 1080), "ratio": (1, 1)},
    "인스타 세로 (4:5)": {"size": (1080, 1350), "ratio": (4, 5)},
    "인스타 가로 (1.91:1)": {"size": (1080, 566), "ratio": (1.91, 1)},
    "인스타 스토리/릴스 (9:16)": {"size": (1080, 1920), "ratio": (9, 16)},
    "블로그 가로 (16:9)": {"size": (1280, 720), "ratio": (16, 9)},
    "블로그 세로 (3:4)": {"size": (960, 1280), "ratio": (3, 4)},
    "블로그 정사각형 (1:1)": {"size": (1200, 1200), "ratio": (1, 1)},
}


def center_crop(img, target_ratio):
    """중앙 기준으로 비율에 맞게 자르기"""
    w, h = img.size
    rw, rh = target_ratio

    target_aspect = rw / rh
    current_aspect = w / h

    if current_aspect > target_aspect:
        # 가로가 넓음 → 좌우 자르기
        new_w = int(h * target_aspect)
        left = (w - new_w) // 2
        box = (left, 0, left + new_w, h)
    else:
        # 세로가 넓음 → 상하 자르기
        new_h = int(w / target_aspect)
        top = (h - new_h) // 2
        box = (0, top, w, top + new_h)

    return img.crop(box)


def process_image(img, preset):
    """비율로 자르고 → 목표 사이즈로 리사이즈"""
    cropped = center_crop(img, preset["ratio"])
    return cropped.resize(preset["size"], Image.LANCZOS)


# --- UI ---
preset_name = st.selectbox("사이즈 선택", list(PRESETS.keys()))
preset = PRESETS[preset_name]
st.info(f"출력 사이즈: **{preset['size'][0]} x {preset['size'][1]}px** (비율 {preset['ratio'][0]}:{preset['ratio'][1]})")

uploaded_files = st.file_uploader(
    "사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

if uploaded_files:
    st.divider()

    # 원본 미리보기
    st.subheader("원본")
    cols = st.columns(min(len(uploaded_files), 4))
    for i, f in enumerate(uploaded_files):
        with cols[i % 4]:
            st.image(f, use_container_width=True, caption=f.name)

    # 자르기 실행
    if st.button("✂️ 자르기", type="primary", use_container_width=True):
        st.divider()
        st.subheader("결과")

        cropped_images = []
        result_cols = st.columns(min(len(uploaded_files), 4))

        for i, f in enumerate(uploaded_files):
            f.seek(0)
            img = Image.open(f).convert("RGB")
            result = process_image(img, preset)
            cropped_images.append((f.name, result))

            with result_cols[i % 4]:
                st.image(result, use_container_width=True, caption=f.name)

        st.divider()

        # 개별 다운로드 + ZIP 다운로드
        if len(cropped_images) == 1:
            name, img = cropped_images[0]
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button(
                label=f"📥 다운로드",
                data=buf.getvalue(),
                file_name=f"cropped_{name.rsplit('.', 1)[0]}.jpg",
                mime="image/jpeg",
                use_container_width=True,
            )
        else:
            # ZIP으로 묶어서 다운로드
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for name, img in cropped_images:
                    img_buf = io.BytesIO()
                    img.save(img_buf, format="JPEG", quality=95)
                    fname = f"cropped_{name.rsplit('.', 1)[0]}.jpg"
                    zf.writestr(fname, img_buf.getvalue())

            st.download_button(
                label=f"📥 전체 다운로드 (ZIP, {len(cropped_images)}장)",
                data=zip_buf.getvalue(),
                file_name="cropped_photos.zip",
                mime="application/zip",
                use_container_width=True,
            )

            # 개별 다운로드
            with st.expander("개별 다운로드"):
                for name, img in cropped_images:
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=95)
                    st.download_button(
                        label=f"📥 {name}",
                        data=buf.getvalue(),
                        file_name=f"cropped_{name.rsplit('.', 1)[0]}.jpg",
                        mime="image/jpeg",
                        key=f"dl_{name}",
                    )
