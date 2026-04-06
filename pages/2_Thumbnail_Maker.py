import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="썸네일 만들기", page_icon="🖼️", layout="wide")

st.title("🖼️ 썸네일 만들기")
st.caption("사진 + 가게 정보를 넣으면 블로그 썸네일을 자동 생성합니다!")

# --- 색상 프리셋 ---
COLOR_PRESETS = {
    "오렌지": {"accent": (255, 120, 30), "overlay": (0, 0, 0, 140)},
    "레드": {"accent": (220, 50, 50), "overlay": (0, 0, 0, 140)},
    "블루": {"accent": (40, 120, 220), "overlay": (0, 0, 0, 140)},
    "그린": {"accent": (40, 180, 100), "overlay": (0, 0, 0, 140)},
    "퍼플": {"accent": (140, 60, 220), "overlay": (0, 0, 0, 140)},
    "골드": {"accent": (210, 170, 50), "overlay": (0, 0, 0, 150)},
    "화이트 미니멀": {"accent": (255, 255, 255), "overlay": (0, 0, 0, 100)},
}


def load_font(size):
    """시스템 폰트 로드"""
    font_paths = [
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansKR-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def create_thumbnail(image, store_name, store_location, label_text, accent_color, overlay_color):
    """썸네일 생성"""
    width, height = 1280, 720
    thumb = image.copy().resize((width, height), Image.LANCZOS)

    # 오버레이
    overlay = Image.new("RGBA", (width, height), overlay_color)
    thumb = thumb.convert("RGBA")
    thumb = Image.alpha_composite(thumb, overlay)

    draw = ImageDraw.Draw(thumb)
    title_font = load_font(72)
    sub_font = load_font(36)
    small_font = load_font(28)

    # --- 상단 라벨 ---
    label_bbox = draw.textbbox((0, 0), label_text, font=sub_font)
    label_w = label_bbox[2] - label_bbox[0]
    label_h = label_bbox[3] - label_bbox[1]
    label_x = (width - label_w) // 2
    label_y = 200
    pad = 16
    draw.rounded_rectangle(
        [label_x - pad * 2, label_y - pad, label_x + label_w + pad * 2, label_y + label_h + pad],
        radius=8, fill=(*accent_color, 220)
    )
    draw.text((label_x, label_y), label_text, fill="white", font=sub_font)

    # --- 가게 이름 ---
    # 긴 이름 줄바꿈 처리
    max_width = width - 160
    lines = []
    current_line = ""
    for char in store_name:
        test = current_line + char
        bbox = draw.textbbox((0, 0), test, font=title_font)
        if bbox[2] - bbox[0] > max_width and current_line:
            lines.append(current_line)
            current_line = char
        else:
            current_line = test
    if current_line:
        lines.append(current_line)

    title_y = 300
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_w = bbox[2] - bbox[0]
        line_x = (width - line_w) // 2
        draw.text((line_x + 3, title_y + 3), line, fill=(0, 0, 0, 180), font=title_font)
        draw.text((line_x, title_y), line, fill="white", font=title_font)
        title_y += bbox[3] - bbox[1] + 10

    # --- 위치 정보 ---
    if store_location:
        loc_text = f"📍 {store_location}"
        loc_bbox = draw.textbbox((0, 0), loc_text, font=sub_font)
        loc_w = loc_bbox[2] - loc_bbox[0]
        loc_x = (width - loc_w) // 2
        loc_y = title_y + 30
        draw.text((loc_x, loc_y), loc_text, fill=(255, 255, 255, 220), font=sub_font)

    # --- 하단 구분선 ---
    line_y = 560
    line_w = 120
    draw.rounded_rectangle(
        [(width // 2 - line_w, line_y), (width // 2 + line_w, line_y + 4)],
        radius=2, fill=(*accent_color, 200)
    )

    return thumb.convert("RGB")


# --- 입력 ---
col1, col2 = st.columns(2)
with col1:
    store_name = st.text_input("가게 이름", placeholder="예: 을지로 골목식당")
with col2:
    store_location = st.text_input("위치", placeholder="예: 서울 을지로3가역 근처")

col3, col4 = st.columns(2)
with col3:
    label_text = st.text_input("라벨 문구", value="맛집 리뷰",
                               placeholder="예: 맛집 리뷰, 솔직 후기, 데이트 맛집")
with col4:
    color_name = st.selectbox("색상 테마", list(COLOR_PRESETS.keys()))

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
        preset = COLOR_PRESETS[color_name]

        thumbnail = create_thumbnail(
            image, store_name, store_location, label_text,
            preset["accent"], preset["overlay"]
        )

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
