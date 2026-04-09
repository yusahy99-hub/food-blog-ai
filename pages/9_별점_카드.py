import io
import os
import glob
import urllib.request
import base64
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


st.markdown('<style>.stMainBlockContainer{max-width:720px;margin:0 auto}</style>', unsafe_allow_html=True)

st.title("⭐ 별점 카드")
st.caption("맛/서비스/분위기/가성비 별점을 입력하면 예쁜 평가 카드를 만들어줍니다")

THEMES = {
    "다크": {"bg": (26, 26, 46), "card": (22, 33, 62), "accent": (233, 69, 96), "text": (255, 255, 255)},
    "라이트": {"bg": (248, 249, 250), "card": (255, 255, 255), "accent": (255, 107, 53), "text": (34, 34, 34)},
    "네이비": {"bg": (10, 22, 40), "card": (26, 39, 68), "accent": (255, 215, 0), "text": (255, 255, 255)},
    "민트": {"bg": (232, 245, 233), "card": (255, 255, 255), "accent": (16, 185, 129), "text": (34, 34, 34)},
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


store_name = st.text_input("가게 이름", placeholder="예: 광장족발")
one_line = st.text_input("한줄평", placeholder="예: 성수동에서 족발 먹으면 여기!")

col1, col2 = st.columns(2)
with col1:
    taste = st.slider("맛", 0.0, 5.0, 4.0, 0.5)
    service = st.slider("서비스", 0.0, 5.0, 4.0, 0.5)
with col2:
    mood = st.slider("분위기", 0.0, 5.0, 4.0, 0.5)
    value = st.slider("가성비", 0.0, 5.0, 4.0, 0.5)

col3, col4 = st.columns(2)
with col3:
    theme_name = st.selectbox("테마", list(THEMES.keys()))
with col4:
    uploaded = st.file_uploader("배경 사진 (선택)", type=["jpg", "jpeg", "png", "webp"])

theme = THEMES[theme_name]
avg = round((taste + service + mood + value) / 4, 1)


def draw_stars(draw, x, y, score, accent, empty_color, star_size):
    """별점을 그려주는 함수"""
    f = get_font(star_size)
    full = int(score)
    half = 1 if score - full >= 0.5 else 0
    empty = 5 - full - half

    cx = x
    for _ in range(full):
        draw.text((cx, y), "★", fill=accent, font=f)
        bbox = draw.textbbox((cx, y), "★", font=f)
        cx = bbox[2] + 2
    if half:
        draw.text((cx, y), "★", fill=accent, font=f)
        bbox = draw.textbbox((cx, y), "★", font=f)
        cx = bbox[2] + 2
    for _ in range(empty):
        draw.text((cx, y), "★", fill=empty_color, font=f)
        bbox = draw.textbbox((cx, y), "★", font=f)
        cx = bbox[2] + 2
    return cx


def build_card(sz=1080):
    img = Image.new("RGB", (sz, sz), theme["bg"])

    # 배경 사진이 있으면 어둡게 오버레이
    if uploaded:
        uploaded.seek(0)
        bg = Image.open(uploaded).convert("RGB")
        # 중앙 크롭
        w, h = bg.size
        ratio = max(sz / w, sz / h)
        bg = bg.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        nw, nh = bg.size
        left, top = (nw - sz) // 2, (nh - sz) // 2
        bg = bg.crop((left, top, left + sz, top + sz))
        # 어둡게
        dark = Image.new("RGB", (sz, sz), (0, 0, 0))
        img = Image.blend(bg, dark, 0.6)

    draw = ImageDraw.Draw(img)
    tc = theme["text"]
    ac = theme["accent"]
    empty_c = (*tc[:3], 50) if len(tc) == 3 else (tc[0], tc[1], tc[2], 50)

    # 카드 배경 영역
    card_margin = int(sz * 0.08)
    card_padding = int(sz * 0.04)
    card_x1, card_y1 = card_margin, int(sz * 0.2)
    card_x2, card_y2 = sz - card_margin, int(sz * 0.85)

    if uploaded:
        # 반투명 카드 배경 (blur 효과 대신 반투명 사각형)
        overlay = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=20, fill=(0, 0, 0, 140))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)
        tc = (255, 255, 255)
        empty_c = (255, 255, 255, 50)
    else:
        card_color = theme["card"]
        draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=20, fill=card_color)

    cx = card_x1 + card_padding
    cy = card_y1 + card_padding

    # 가게 이름
    title_font = get_font(int(sz * 0.05))
    draw.text((cx, cy), store_name or "가게 이름", fill=tc, font=title_font)
    cy += int(sz * 0.06)

    # 한줄평
    if one_line:
        sub_font = get_font(int(sz * 0.022))
        sub_c = (*tc[:3],) if len(tc) == 3 else tc
        draw.text((cx, cy), one_line, fill=sub_c, font=sub_font)
    cy += int(sz * 0.045)

    # 별점 행
    label_font = get_font(int(sz * 0.025))
    star_size = int(sz * 0.032)
    row_height = int(sz * 0.055)

    for label, score in [("맛", taste), ("서비스", service), ("분위기", mood), ("가성비", value)]:
        draw.text((cx, cy + 4), label, fill=tc, font=label_font)
        draw_stars(draw, cx + int(sz * 0.1), cy, score, ac, empty_c, star_size)
        # 점수
        score_font = get_font(int(sz * 0.025))
        score_text = str(score)
        sb = draw.textbbox((0, 0), score_text, font=score_font)
        draw.text((card_x2 - card_padding - (sb[2] - sb[0]), cy + 4), score_text, fill=tc, font=score_font)
        cy += row_height

    # 구분선
    cy += int(sz * 0.01)
    line_color = (*tc[:3],) if len(tc) == 3 else tc
    draw.line([(cx, cy), (card_x2 - card_padding, cy)], fill=line_color, width=1)
    cy += int(sz * 0.02)

    # 총점
    avg_label_font = get_font(int(sz * 0.025))
    draw.text((cx, cy + int(sz * 0.015)), "총점", fill=tc, font=avg_label_font)
    avg_font = get_font(int(sz * 0.065))
    avg_text = str(avg)
    ab = draw.textbbox((0, 0), avg_text, font=avg_font)
    draw.text((card_x2 - card_padding - (ab[2] - ab[0]), cy), avg_text, fill=ac, font=avg_font)

    return img


if store_name:
    st.divider()
    st.subheader("미리보기")
    card = build_card(1080)
    st.image(card, use_container_width=True)

    buf = io.BytesIO()
    card.save(buf, format="PNG")
    safe_name = store_name.replace('"', '').replace("'", "")
    st.download_button(
        "📥 별점 카드 다운로드 (PNG)",
        buf.getvalue(),
        f"{safe_name}_별점카드.png",
        "image/png",
        use_container_width=True,
    )
