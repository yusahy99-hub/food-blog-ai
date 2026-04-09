import io
import os
import zipfile
import urllib.request
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


st.markdown("""
<style>
    .stMainBlockContainer { max-width: 720px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("💧 워터마크")
st.caption("사진에 블로그명/인스타 아이디 워터마크를 넣어줍니다")

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR-Bold.ttf"


@st.cache_resource
def get_font_path():
    if os.path.exists("C:/Windows/Fonts/malgunbd.ttf"):
        return "C:/Windows/Fonts/malgunbd.ttf"
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for p in [
        os.path.join(project_root, "fonts", "NotoSansKR-Bold.ttf"),
        os.path.join(os.getcwd(), "fonts", "NotoSansKR-Bold.ttf"),
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]:
        if os.path.exists(p):
            return p
    import glob
    found = glob.glob("/usr/share/fonts/**/Noto*CJK*", recursive=True)
    if found:
        return found[0]
    import tempfile
    fp = os.path.join(tempfile.gettempdir(), "NotoSansKR-Bold.ttf")
    if not os.path.exists(fp):
        urllib.request.urlretrieve(FONT_URL, fp)
    return fp


FONT_PATH = get_font_path()

POSITIONS = {
    "우하단": "br",
    "좌하단": "bl",
    "우상단": "tr",
    "좌상단": "tl",
    "중앙": "center",
}

# --- 입력 ---
watermark_text = st.text_input("워터마크 텍스트", placeholder="예: @my_food_blog")

col1, col2, col3 = st.columns(3)
with col1:
    position = st.selectbox("위치", list(POSITIONS.keys()))
with col2:
    opacity = st.slider("투명도", 10, 100, 40, 5)
with col3:
    font_size_pct = st.slider("크기 (%)", 2, 10, 4, 1)

uploaded_files = st.file_uploader(
    "사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)


def add_watermark(img, text, pos, opacity_pct, size_pct):
    img = img.convert("RGBA")
    w, h = img.size
    font_size = max(int(w * size_pct / 100), 16)

    try:
        if FONT_PATH.endswith(".ttc"):
            font = ImageFont.truetype(FONT_PATH, font_size, index=0)
        else:
            font = ImageFont.truetype(FONT_PATH, font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()

    txt_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    margin = int(w * 0.03)
    positions = {
        "br": (w - tw - margin, h - th - margin),
        "bl": (margin, h - th - margin),
        "tr": (w - tw - margin, margin),
        "tl": (margin, margin),
        "center": ((w - tw) // 2, (h - th) // 2),
    }
    x, y = positions[pos]

    alpha = int(255 * opacity_pct / 100)
    draw.text((x, y), text, fill=(255, 255, 255, alpha), font=font)

    return Image.alpha_composite(img, txt_layer).convert("RGB")


if uploaded_files and watermark_text:
    if st.button("💧 워터마크 적용", type="primary", use_container_width=True):
        pos_code = POSITIONS[position]
        results = []

        st.divider()
        st.subheader("결과")
        result_cols = st.columns(min(len(uploaded_files), 3))

        for i, f in enumerate(uploaded_files):
            f.seek(0)
            img = Image.open(f).convert("RGB")
            result = add_watermark(img, watermark_text, pos_code, opacity, font_size_pct)
            results.append((f.name, result))
            with result_cols[i % 3]:
                st.image(result, use_container_width=True)

        st.divider()
        if len(results) == 1:
            name, img = results[0]
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("📥 다운로드", buf.getvalue(),
                               f"wm_{name.rsplit('.', 1)[0]}.jpg", "image/jpeg",
                               use_container_width=True)
        else:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for name, img in results:
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=95)
                    zf.writestr(f"wm_{name.rsplit('.', 1)[0]}.jpg", buf.getvalue())
            st.download_button(
                f"📥 전체 다운로드 (ZIP, {len(results)}장)",
                zip_buf.getvalue(), "watermarked.zip", "application/zip",
                use_container_width=True)
