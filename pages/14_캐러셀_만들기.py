import io
import os
import glob
import zipfile
import urllib.request
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


st.markdown("""
<style>
    .stMainBlockContainer { max-width: 800px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("📱 캐러셀 만들기")
st.caption("인스타그램 캐러셀(슬라이드) 게시물을 만들어보세요")

# --- 색상 테마 ---
THEMES = {
    "오렌지": {"bg": (255, 107, 53), "text": (255, 255, 255)},
    "블루": {"bg": (26, 115, 232), "text": (255, 255, 255)},
    "블랙": {"bg": (26, 26, 26), "text": (255, 255, 255)},
    "화이트": {"bg": (255, 255, 255), "text": (26, 26, 26)},
    "핑크": {"bg": (233, 30, 99), "text": (255, 255, 255)},
    "그린": {"bg": (46, 125, 50), "text": (255, 255, 255)},
}

# --- 폰트 로드 ---
def _find_font():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        os.path.join(project_root, "fonts", "NotoSansKR-Bold.ttf"),
        os.path.join(os.getcwd(), "fonts", "NotoSansKR-Bold.ttf"),
        "C:/Windows/Fonts/malgunbd.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    found = glob.glob("/usr/share/fonts/**/Noto*CJK*", recursive=True)
    if found:
        return found[0]
    found = glob.glob("/usr/share/fonts/**/Noto*KR*", recursive=True)
    if found:
        return found[0]
    import tempfile
    fp = os.path.join(tempfile.gettempdir(), "NotoSansKR-Bold.ttf")
    if not os.path.exists(fp):
        urllib.request.urlretrieve(
            "https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR-Bold.ttf", fp)
    return fp

FONT_PATH = _find_font()


def get_font(size):
    try:
        if FONT_PATH.endswith(".ttc"):
            return ImageFont.truetype(FONT_PATH, size, index=0)
        return ImageFont.truetype(FONT_PATH, size)
    except (OSError, IOError):
        return ImageFont.load_default()


def center_crop_square(img, size=1080):
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    return img.resize((size, size), Image.LANCZOS)


def wrap_text(draw, text, font, max_width):
    """텍스트를 max_width에 맞게 줄바꿈"""
    lines = []
    for paragraph in text.split('\n'):
        words = list(paragraph)
        if not words:
            lines.append("")
            continue
        current = ""
        for ch in words:
            test = current + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width and current:
                lines.append(current)
                current = ch
            else:
                current = test
        if current:
            lines.append(current)
    return lines


def build_slide(img, text, slide_num, total, theme):
    """PIL로 단일 슬라이드 생성 (1080x1080)"""
    W = 1080
    canvas = center_crop_square(img, W).convert("RGBA")

    draw = ImageDraw.Draw(canvas)

    # 텍스트 오버레이
    if text.strip():
        text_font = get_font(36)
        padding = 28
        margin = 40
        max_text_w = W - margin * 2 - padding * 2

        lines = wrap_text(draw, text, text_font, max_text_w)
        line_height = 54
        text_block_h = len(lines) * line_height

        # 반투명 배경
        box_x1 = margin
        box_y1 = W - 80 - text_block_h - padding * 2
        box_x2 = W - margin
        box_y2 = W - 80

        overlay = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=12, fill=(0, 0, 0, 140))
        canvas = Image.alpha_composite(canvas, overlay)
        draw = ImageDraw.Draw(canvas)

        # 텍스트 그리기
        ty = box_y1 + padding
        for line in lines:
            lb = draw.textbbox((0, 0), line, font=text_font)
            lw = lb[2] - lb[0]
            tx = box_x1 + (box_x2 - box_x1 - lw) // 2
            draw.text((tx, ty), line, fill=(255, 255, 255), font=text_font)
            ty += line_height

    # 페이지 배지
    badge_font = get_font(24)
    badge_text = f"{slide_num}/{total}"
    bb = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    bx, by = W - 28 - bw - 18 * 2, 28

    badge_overlay = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge_overlay)
    bd.rounded_rectangle([bx, by, bx + bw + 36, by + bh + 16], radius=20,
                         fill=(*theme["bg"], 230))
    canvas = Image.alpha_composite(canvas, badge_overlay)
    draw = ImageDraw.Draw(canvas)
    draw.text((bx + 18, by + 8), badge_text, fill=theme["text"], font=badge_font)

    return canvas.convert("RGB")


# --- UI ---
theme_name = st.selectbox("색상 테마", list(THEMES.keys()))
theme = THEMES[theme_name]

st.divider()

uploaded_files = st.file_uploader(
    "사진 업로드 (여러 장 → 슬라이드 순서대로)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
)

if uploaded_files:
    total = len(uploaded_files)
    st.info(f"총 **{total}장** 슬라이드")

    texts = []
    for i, f in enumerate(uploaded_files):
        text = st.text_input(
            f"슬라이드 {i+1} 텍스트 (선택)",
            key=f"text_{i}_{f.name}",
            placeholder="텍스트를 입력하세요 (비워두면 사진만 표시)",
        )
        texts.append(text)

    st.divider()

    if st.button("📱 캐러셀 만들기", type="primary", use_container_width=True):
        slides = []

        st.subheader("미리보기")
        preview_cols = st.columns(min(total, 4))

        for i, f in enumerate(uploaded_files):
            f.seek(0)
            img = Image.open(f).convert("RGB")
            slide = build_slide(img, texts[i], i + 1, total, theme)
            slides.append((f"slide_{i+1:02d}.png", slide))

            with preview_cols[i % 4]:
                st.image(slide, use_container_width=True)
                st.caption(f"슬라이드 {i+1}/{total}")

        st.divider()

        # ZIP 다운로드
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, slide in slides:
                buf = io.BytesIO()
                slide.save(buf, format="PNG")
                zf.writestr(name, buf.getvalue())

        st.download_button(
            label=f"📥 전체 다운로드 (ZIP, {total}장 PNG)",
            data=zip_buf.getvalue(),
            file_name="carousel_slides.zip",
            mime="application/zip",
            use_container_width=True,
        )

        # 개별 다운로드
        with st.expander("개별 다운로드"):
            for name, slide in slides:
                buf = io.BytesIO()
                slide.save(buf, format="PNG")
                st.download_button(
                    label=f"📥 {name}",
                    data=buf.getvalue(),
                    file_name=name,
                    mime="image/png",
                    key=f"dl_{name}",
                )
