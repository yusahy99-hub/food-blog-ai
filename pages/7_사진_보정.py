import io
import zipfile
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter

st.set_page_config(page_title="사진 보정", page_icon="🎨")
st.markdown('<style>.stMainBlockContainer{max-width:800px;margin:0 auto}</style>', unsafe_allow_html=True)

st.title("🎨 사진 보정 필터")
st.caption("맛집 사진 특화 필터로 음식을 더 맛있어 보이게!")

FILTERS = {
    "원본": {},
    "맛있는 따뜻한 톤": {"brightness": 1.08, "contrast": 1.12, "saturation": 1.25, "warmth": 15},
    "선명하게": {"brightness": 1.05, "contrast": 1.2, "saturation": 1.1, "sharpness": 2.0},
    "감성 카페": {"brightness": 1.1, "contrast": 0.95, "saturation": 0.85, "warmth": 10},
    "음식 색감 강조": {"brightness": 1.05, "contrast": 1.15, "saturation": 1.4, "warmth": 8},
    "어두운 무드": {"brightness": 0.85, "contrast": 1.25, "saturation": 1.1, "warmth": 5},
    "밝고 깨끗한": {"brightness": 1.2, "contrast": 1.05, "saturation": 1.05, "warmth": 0},
    "빈티지": {"brightness": 0.95, "contrast": 1.1, "saturation": 0.7, "warmth": 20},
}


def apply_warmth(img, amount):
    """따뜻한 톤 적용"""
    if amount == 0:
        return img
    r, g, b = img.split()
    r = r.point(lambda x: min(255, x + amount))
    b = b.point(lambda x: max(0, x - amount // 2))
    return Image.merge("RGB", (r, g, b))


def apply_filter(img, settings):
    if not settings:
        return img
    img = img.convert("RGB")
    if "brightness" in settings:
        img = ImageEnhance.Brightness(img).enhance(settings["brightness"])
    if "contrast" in settings:
        img = ImageEnhance.Contrast(img).enhance(settings["contrast"])
    if "saturation" in settings:
        img = ImageEnhance.Color(img).enhance(settings["saturation"])
    if "sharpness" in settings:
        img = ImageEnhance.Sharpness(img).enhance(settings["sharpness"])
    if "warmth" in settings:
        img = apply_warmth(img, settings["warmth"])
    return img


# --- 필터 선택 ---
filter_name = st.selectbox("필터 선택", list(FILTERS.keys()))

# 수동 조절
with st.expander("수동 조절"):
    mc1, mc2 = st.columns(2)
    with mc1:
        m_brightness = st.slider("밝기", 0.5, 1.5, 1.0, 0.05)
        m_contrast = st.slider("대비", 0.5, 1.5, 1.0, 0.05)
    with mc2:
        m_saturation = st.slider("채도", 0.0, 2.0, 1.0, 0.05)
        m_warmth = st.slider("따뜻한 톤", -20, 40, 0, 1)
    use_manual = m_brightness != 1.0 or m_contrast != 1.0 or m_saturation != 1.0 or m_warmth != 0

uploaded_files = st.file_uploader("사진 업로드 (여러 장 가능)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

if uploaded_files:
    if use_manual:
        settings = {"brightness": m_brightness, "contrast": m_contrast, "saturation": m_saturation, "warmth": m_warmth}
    else:
        settings = FILTERS[filter_name]

    st.divider()
    results = []

    for f in uploaded_files:
        f.seek(0)
        img = Image.open(f).convert("RGB")
        filtered = apply_filter(img, settings)
        results.append((f.name, filtered))

        st.subheader(f.name)
        c1, c2 = st.columns(2)
        with c1:
            st.image(img, caption="원본", use_container_width=True)
        with c2:
            st.image(filtered, caption=filter_name if not use_manual else "수동 조절", use_container_width=True)

    st.divider()
    if len(results) == 1:
        name, img = results[0]
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        st.download_button("📥 다운로드", buf.getvalue(),
                           f"filtered_{name.rsplit('.', 1)[0]}.jpg", "image/jpeg",
                           use_container_width=True)
    else:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, img in results:
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=95)
                zf.writestr(f"filtered_{name.rsplit('.', 1)[0]}.jpg", buf.getvalue())
        st.download_button(f"📥 전체 다운로드 (ZIP, {len(results)}장)",
                           zip_buf.getvalue(), "filtered.zip", "application/zip",
                           use_container_width=True)
