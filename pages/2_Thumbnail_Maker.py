import io
import os
import urllib.request
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="썸네일 만들기", page_icon="🖼️")

st.markdown("""
<style>
    .stMainBlockContainer { max-width: 700px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("🖼️ 썸네일 만들기")
st.caption("사진 + 가게 정보를 넣으면 블로그 썸네일을 자동 생성합니다!")

@st.cache_resource
def get_font_path():
    """한글 폰트 확보 - 모든 환경 대응"""
    import glob
    candidates = [
        # Windows
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        # Streamlit Cloud (packages.txt로 설치됨)
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        # 프로젝트 내
        os.path.join(os.getcwd(), "fonts", "NotoSansKR-Bold.ttf"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # glob으로 noto cjk 폰트 찾기
    found = glob.glob("/usr/share/fonts/**/Noto*CJK*", recursive=True)
    if found:
        return found[0]
    # 최후의 수단: 다운로드
    import tempfile
    fp = os.path.join(tempfile.gettempdir(), "NotoSansKR-Bold.ttf")
    if not os.path.exists(fp):
        urllib.request.urlretrieve(
            "https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR-Bold.ttf", fp
        )
    return fp


FONT_PATH = get_font_path()

COLOR_PRESETS = {
    "오렌지": (255, 120, 30),
    "레드": (220, 50, 50),
    "블루": (40, 120, 220),
    "그린": (40, 180, 100),
    "퍼플": (140, 60, 220),
    "골드": (210, 170, 50),
    "화이트": (255, 255, 255),
}


def font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except (OSError, IOError):
        return ImageFont.load_default()


def create_thumbnail(image, store_name, store_location, subtitle, accent_color):
    W, H = 1080, 1080
    thumb = image.copy().resize((W, H), Image.LANCZOS).convert("RGBA")

    # --- 하단 그라데이션 ---
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    start = H // 3
    for y in range(start, H):
        a = int(240 * ((y - start) / (H - start)) ** 1.2)
        gd.line([(0, y), (W, y)], fill=(0, 0, 0, min(a, 240)))
    thumb = Image.alpha_composite(thumb, grad)

    draw = ImageDraw.Draw(thumb)

    name_font = font(78)
    sub_font = font(32)
    tag_font = font(26)

    ml = 65  # margin left
    bottom = H - 85

    # === 1. 가게 이름 (맨 아래, 크게) ===
    max_w = W - ml * 2
    lines = []
    cur = ""
    for ch in store_name:
        t = cur + ch
        bb = draw.textbbox((0, 0), t, font=name_font)
        if bb[2] - bb[0] > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = t
    if cur:
        lines.append(cur)

    cy = bottom
    for line in reversed(lines):
        bb = draw.textbbox((0, 0), line, font=name_font)
        lh = bb[3] - bb[1]
        cy -= lh
        draw.text((ml + 3, cy + 3), line, fill=(0, 0, 0, 200), font=name_font)
        draw.text((ml, cy), line, fill="white", font=name_font)
        cy -= 6

    name_top = cy

    # === 2. 설명 문구 (가게 이름 위) ===
    if subtitle:
        sb = draw.textbbox((0, 0), subtitle, font=sub_font)
        sh = sb[3] - sb[1]
        sy = name_top - sh - 16
        draw.text((ml + 2, sy + 2), subtitle, fill=(0, 0, 0, 160), font=sub_font)
        draw.text((ml, sy), subtitle, fill="white", font=sub_font)
        above = sy
    else:
        above = name_top

    # === 3. 위치 태그 (컬러 둥근 박스) ===
    if store_location:
        tb = draw.textbbox((0, 0), store_location, font=tag_font)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
        px, py = 24, 12
        ty = above - th - py * 2 - 24

        tc = "white" if accent_color != (255, 255, 255) else "black"
        draw.rounded_rectangle(
            [ml, ty, ml + tw + px * 2, ty + th + py * 2],
            radius=8, fill=(*accent_color, 240)
        )
        draw.text((ml + px, ty + py), store_location, fill=tc, font=tag_font)

        bracket_top = ty
    else:
        bracket_top = above

    # === 4. 꺾쇠 장식 라인 (레퍼런스 스타일) ===
    line_color = (255, 255, 255, 180)
    line_w = 3
    corner_len = 40
    bx = ml - 20
    by = bracket_top - 20

    # ㄴ자 위쪽 꺾쇠 (왼쪽 위 코너)
    draw.line([(bx, by + corner_len), (bx, by)], fill=line_color, width=line_w)
    draw.line([(bx, by), (bx + corner_len, by)], fill=line_color, width=line_w)

    return thumb.convert("RGB")


# --- UI ---
col1, col2 = st.columns(2)
with col1:
    store_name = st.text_input("가게 이름", placeholder="예: 광장족발")
with col2:
    store_location = st.text_input("위치 태그", placeholder="예: 성수")

col3, col4 = st.columns(2)
with col3:
    subtitle = st.text_input("설명 문구", placeholder="예: 성수동 직장인 추천 아들아들 족발맛집")
with col4:
    color_name = st.selectbox("태그 색상", list(COLOR_PRESETS.keys()))

uploaded_file = st.file_uploader("배경 사진 업로드", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file:
    st.image(uploaded_file, caption="원본 사진", width=350)

if st.button("🖼️ 썸네일 생성", type="primary", use_container_width=True):
    if not store_name:
        st.error("가게 이름을 입력해주세요.")
    elif not uploaded_file:
        st.error("배경 사진을 업로드해주세요.")
    else:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        accent = COLOR_PRESETS[color_name]
        thumbnail = create_thumbnail(image, store_name, store_location, subtitle, accent)

        st.divider()
        st.subheader("완성된 썸네일")
        st.image(thumbnail, use_container_width=True)

        buf = io.BytesIO()
        thumbnail.save(buf, format="JPEG", quality=95)
        st.download_button(
            label="📥 썸네일 다운로드",
            data=buf.getvalue(),
            file_name=f"{store_name}_썸네일.jpg",
            mime="image/jpeg",
            use_container_width=True,
        )
