import io
import base64
import zipfile
import streamlit as st
from PIL import Image


st.markdown("""
<style>
    .stMainBlockContainer { max-width: 800px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("📱 캐러셀 만들기")
st.caption("인스타그램 캐러셀(슬라이드) 게시물을 만들어보세요")

# --- 색상 테마 ---
THEMES = {
    "오렌지": {"bg": "#FF6B35", "text": "#FFFFFF", "accent": "#FFE0CC"},
    "블루": {"bg": "#1A73E8", "text": "#FFFFFF", "accent": "#D0E4FF"},
    "블랙": {"bg": "#1A1A1A", "text": "#FFFFFF", "accent": "#444444"},
    "화이트": {"bg": "#FFFFFF", "text": "#1A1A1A", "accent": "#F0F0F0"},
    "핑크": {"bg": "#E91E63", "text": "#FFFFFF", "accent": "#FCE4EC"},
    "그린": {"bg": "#2E7D32", "text": "#FFFFFF", "accent": "#C8E6C9"},
}

# --- 폰트 목록 ---
FONTS = {
    "Noto Sans KR": "Noto+Sans+KR",
    "Black Han Sans": "Black+Han+Sans",
    "Nanum Gothic": "Nanum+Gothic",
    "Nanum Myeongjo": "Nanum+Myeongjo",
    "Do Hyeon": "Do+Hyeon",
    "Jua": "Jua",
    "Gugi": "Gugi",
}


def image_to_data_uri(img: Image.Image) -> str:
    """PIL Image를 data URI로 변환"""
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"


def build_slide_html(
    img: Image.Image,
    text: str,
    slide_num: int,
    total: int,
    theme: dict,
    font_name: str,
    font_param: str,
) -> str:
    """단일 슬라이드 HTML 생성 (1080x1080)"""
    data_uri = image_to_data_uri(img)

    text_html = ""
    if text.strip():
        text_html = f"""
        <div style="
            position: absolute;
            bottom: 80px;
            left: 40px;
            right: 40px;
            background: rgba(0,0,0,0.55);
            color: #FFFFFF;
            padding: 24px 28px;
            border-radius: 12px;
            font-size: 36px;
            line-height: 1.5;
            word-break: keep-all;
            text-align: center;
        ">{text}</div>
        """

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family={font_param}:wght@400;700;900&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1080px;
    height: 1080px;
    font-family: '{font_name}', sans-serif;
    overflow: hidden;
    position: relative;
    background: {theme['bg']};
  }}
  .slide-image {{
    width: 1080px;
    height: 1080px;
    object-fit: cover;
  }}
  .page-badge {{
    position: absolute;
    top: 28px;
    right: 28px;
    background: {theme['bg']};
    color: {theme['text']};
    font-size: 24px;
    font-weight: 700;
    padding: 8px 18px;
    border-radius: 20px;
    opacity: 0.9;
  }}
</style>
</head>
<body>
  <img class="slide-image" src="{data_uri}" alt="slide {slide_num}">
  {text_html}
  <div class="page-badge">{slide_num}/{total}</div>
</body>
</html>"""


# --- UI ---
col_theme, col_font = st.columns(2)
with col_theme:
    theme_name = st.selectbox("색상 테마", list(THEMES.keys()))
with col_font:
    font_name = st.selectbox("폰트", list(FONTS.keys()))

theme = THEMES[theme_name]
font_param = FONTS[font_name]

st.divider()

uploaded_files = st.file_uploader(
    "사진 업로드 (여러 장 → 슬라이드 순서대로)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
)

if uploaded_files:
    total = len(uploaded_files)
    st.info(f"총 **{total}장** 슬라이드")

    # 각 사진마다 텍스트 입력
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
        slides_html = []

        st.subheader("미리보기")
        preview_cols = st.columns(min(total, 4))

        for i, f in enumerate(uploaded_files):
            f.seek(0)
            img = Image.open(f).convert("RGB")

            # 정사각형 크롭 (중앙 기준)
            w, h = img.size
            if w != h:
                side = min(w, h)
                left = (w - side) // 2
                top = (h - side) // 2
                img = img.crop((left, top, left + side, top + side))
            img = img.resize((1080, 1080), Image.LANCZOS)

            html = build_slide_html(
                img, texts[i], i + 1, total, theme, font_name, font_param
            )
            slides_html.append((f"slide_{i+1:02d}.html", html))

            # 미리보기 (축소)
            with preview_cols[i % 4]:
                st.components.v1.html(html, height=270, width=270, scrolling=False)
                st.caption(f"슬라이드 {i+1}/{total}")

        st.divider()

        # ZIP 다운로드
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, html in slides_html:
                zf.writestr(name, html.encode("utf-8"))

        st.download_button(
            label=f"📥 전체 다운로드 (ZIP, {total}장 HTML)",
            data=zip_buf.getvalue(),
            file_name="carousel_slides.zip",
            mime="application/zip",
            use_container_width=True,
        )

        # 개별 다운로드
        with st.expander("개별 다운로드"):
            for name, html in slides_html:
                st.download_button(
                    label=f"📥 {name}",
                    data=html.encode("utf-8"),
                    file_name=name,
                    mime="text/html",
                    key=f"dl_{name}",
                )
