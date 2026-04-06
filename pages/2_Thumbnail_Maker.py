import io
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="썸네일 만들기", page_icon="🖼️", layout="wide")

st.title("🖼️ 썸네일 만들기")
st.caption("사진 + 가게 정보를 넣으면 블로그 썸네일을 자동 생성합니다!")

FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "NotoSansKR-Bold.ttf")

# --- 색상 프리셋 ---
COLOR_PRESETS = {
    "오렌지": (255, 120, 30),
    "레드": (220, 50, 50),
    "블루": (40, 120, 220),
    "그린": (40, 180, 100),
    "퍼플": (140, 60, 220),
    "골드": (210, 170, 50),
    "화이트": (255, 255, 255),
}


def load_font(size):
    """프로젝트 내장 한글 폰트 로드"""
    paths = [
        FONT_PATH,
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
    ]
    for fp in paths:
        try:
            return ImageFont.truetype(fp, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def create_thumbnail(image, store_name, store_location, subtitle, accent_color):
    """레퍼런스 스타일 썸네일 - 하단 좌측 배치, 그라데이션"""
    width, height = 1080, 1080
    thumb = image.copy().resize((width, height), Image.LANCZOS).convert("RGBA")

    # --- 하단 그라데이션 오버레이 (아래쪽만 어둡게) ---
    gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)
    for y in range(height // 3, height):
        progress = (y - height // 3) / (height - height // 3)
        alpha = int(220 * progress)
        gradient_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    thumb = Image.alpha_composite(thumb, gradient)

    draw = ImageDraw.Draw(thumb)

    # 폰트
    name_font = load_font(64)
    subtitle_font = load_font(30)
    tag_font = load_font(26)

    # 좌측 하단 기준
    margin_left = 60
    bottom_y = height - 80

    # --- 1. 가게 이름 (맨 아래, 크게) ---
    name_bbox = draw.textbbox((0, 0), store_name, font=name_font)
    name_h = name_bbox[3] - name_bbox[1]
    name_y = bottom_y - name_h
    draw.text((margin_left + 2, name_y + 2), store_name, fill=(0, 0, 0, 180), font=name_font)
    draw.text((margin_left, name_y), store_name, fill="white", font=name_font)

    # --- 2. 설명 문구 (가게 이름 위) ---
    if subtitle:
        sub_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_h = sub_bbox[3] - sub_bbox[1]
        sub_y = name_y - sub_h - 18
        draw.text((margin_left + 1, sub_y + 1), subtitle, fill=(0, 0, 0, 150), font=subtitle_font)
        draw.text((margin_left, sub_y), subtitle, fill="white", font=subtitle_font)
        tag_bottom = sub_y
    else:
        tag_bottom = name_y

    # --- 3. 위치 태그 (컬러 박스) ---
    if store_location:
        tag_bbox = draw.textbbox((0, 0), store_location, font=tag_font)
        tag_w = tag_bbox[2] - tag_bbox[0]
        tag_h = tag_bbox[3] - tag_bbox[1]
        tag_pad_x = 20
        tag_pad_y = 10
        tag_y = tag_bottom - tag_h - tag_pad_y * 2 - 20

        # 태그 배경
        text_color = "white" if accent_color != (255, 255, 255) else "black"
        draw.rounded_rectangle(
            [margin_left, tag_y,
             margin_left + tag_w + tag_pad_x * 2, tag_y + tag_h + tag_pad_y * 2],
            radius=6,
            fill=(*accent_color, 230)
        )
        draw.text((margin_left + tag_pad_x, tag_y + tag_pad_y),
                  store_location, fill=text_color, font=tag_font)

    return thumb.convert("RGB")


# --- 입력 ---
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
    st.image(uploaded_file, caption="원본 사진", use_container_width=True)

# --- 생성 ---
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

        # 다운로드
        buf = io.BytesIO()
        thumbnail.save(buf, format="JPEG", quality=95)
        st.download_button(
            label="📥 썸네일 다운로드",
            data=buf.getvalue(),
            file_name=f"{store_name}_썸네일.jpg",
            mime="image/jpeg",
            use_container_width=True,
        )
