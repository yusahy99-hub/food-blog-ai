import os
import io
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

load_dotenv()

st.set_page_config(page_title="맛집 블로그 AI", page_icon="🍽️", layout="wide")

# --- 스타일 ---
st.markdown("""
<style>
    .stMainBlockContainer { max-width: 900px; margin: 0 auto; }
    .blog-output {
        background: #fafafa;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #eee;
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)


def create_thumbnail(image, store_name, store_location=""):
    """업로드된 사진으로 블로그 썸네일 생성"""
    # 썸네일 크기 (16:9 비율)
    width, height = 1280, 720
    thumb = image.copy().resize((width, height), Image.LANCZOS)

    # 어둡게 오버레이
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 140))
    thumb = thumb.convert("RGBA")
    thumb = Image.alpha_composite(thumb, overlay)

    draw = ImageDraw.Draw(thumb)

    # 폰트 설정 (시스템 폰트 사용 시도)
    font_paths = [
        "C:/Windows/Fonts/malgunbd.ttf",     # 맑은 고딕 Bold
        "C:/Windows/Fonts/malgun.ttf",        # 맑은 고딕
        "/usr/share/fonts/truetype/noto/NotoSansKR-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]

    title_font = None
    sub_font = None
    for fp in font_paths:
        try:
            title_font = ImageFont.truetype(fp, 72)
            sub_font = ImageFont.truetype(fp, 36)
            break
        except (OSError, IOError):
            continue

    if title_font is None:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    # 상단 라벨
    label = "맛집 리뷰"
    label_bbox = draw.textbbox((0, 0), label, font=sub_font)
    label_w = label_bbox[2] - label_bbox[0]
    label_x = (width - label_w) // 2
    label_y = 200

    # 라벨 배경 (주황색 바)
    pad = 16
    draw.rounded_rectangle(
        [label_x - pad * 2, label_y - pad, label_x + label_w + pad * 2, label_y + (label_bbox[3] - label_bbox[1]) + pad],
        radius=8, fill=(255, 120, 30, 220)
    )
    draw.text((label_x, label_y), label, fill="white", font=sub_font)

    # 가게 이름 (가운데)
    title_bbox = draw.textbbox((0, 0), store_name, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (width - title_w) // 2
    title_y = 300

    # 텍스트 그림자
    draw.text((title_x + 3, title_y + 3), store_name, fill=(0, 0, 0, 180), font=title_font)
    draw.text((title_x, title_y), store_name, fill="white", font=title_font)

    # 위치 정보
    if store_location:
        loc_text = f"📍 {store_location}"
        loc_bbox = draw.textbbox((0, 0), loc_text, font=sub_font)
        loc_w = loc_bbox[2] - loc_bbox[0]
        loc_x = (width - loc_w) // 2
        loc_y = 420
        draw.text((loc_x, loc_y), loc_text, fill=(255, 255, 255, 220), font=sub_font)

    # 하단 구분선
    line_y = 520
    line_w = 120
    draw.rounded_rectangle(
        [(width // 2 - line_w, line_y), (width // 2 + line_w, line_y + 4)],
        radius=2, fill=(255, 120, 30, 200)
    )

    return thumb.convert("RGB")


# --- 사이드바: API 키 ---
with st.sidebar:
    st.header("설정")
    default_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
    api_key = st.text_input("Google Gemini API Key", value=default_key, type="password",
                            help="aistudio.google.com/apikey 에서 발급받으세요")

    st.divider()
    st.subheader("글 스타일")
    tone = st.selectbox("톤 선택", ["친근하고 캐주얼한", "감성적이고 세련된", "유머러스한", "정보 중심의 깔끔한"])
    length = st.selectbox("글 길이", ["짧게 (SNS용)", "보통 (블로그용)", "길게 (상세 리뷰)"])

# --- 메인 ---
st.title("🍽️ 맛집 블로그 AI")
st.caption("사진을 올리면 맛집 블로거처럼 글을 써드립니다!")

col1, col2 = st.columns(2)

with col1:
    store_name = st.text_input("가게 이름", placeholder="예: 을지로 골목식당")

with col2:
    store_location = st.text_input("위치", placeholder="예: 서울 을지로3가역 근처")

uploaded_files = st.file_uploader(
    "음식/공간 사진 업로드",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

# 업로드된 사진 미리보기
if uploaded_files:
    cols = st.columns(min(len(uploaded_files), 5))
    for i, file in enumerate(uploaded_files):
        with cols[i % 5]:
            st.image(file, use_container_width=True)

# --- 블로그 생성 ---
if st.button("✍️ 블로그 글 생성", type="primary", use_container_width=True):
    if not api_key:
        st.error("사이드바에서 API Key를 입력해주세요.")
    elif not uploaded_files:
        st.error("사진을 최소 1장 업로드해주세요.")
    elif not store_name:
        st.error("가게 이름을 입력해주세요.")
    else:
        # 이미지를 PIL로 변환
        images = []
        for file in uploaded_files:
            file.seek(0)
            images.append(Image.open(file))

        length_guide = {
            "짧게 (SNS용)": "300자 내외로 짧고 임팩트 있게",
            "보통 (블로그용)": "800~1200자 정도로 적당히",
            "길게 (상세 리뷰)": "1500~2000자로 상세하게",
        }

        location_info = f"\n- 위치: {store_location}" if store_location else ""

        prompt = f"""당신은 한국의 인기 맛집 블로거입니다.
아래 정보를 바탕으로 블로그 포스팅을 작성해주세요.

## 가게 정보
- 가게 이름: {store_name}{location_info}

## 작성 가이드
- 톤: {tone} 말투로 작성
- 분량: {length_guide[length]}
- 첨부된 사진들을 분석하여 음식의 비주얼, 맛의 추정, 분위기 등을 생생하게 묘사
- 자연스러운 맛집 블로그 형식 (제목, 소개, 음식 설명, 총평 포함)
- 적절한 이모지 사용
- 해시태그 5~10개를 마지막에 포함

## 주의사항
- 사진에 보이는 음식/공간을 기반으로만 작성 (없는 내용 지어내지 않기)
- 과장되지 않으면서도 매력적으로 표현
- 한국 맛집 블로그 특유의 생동감 있는 문체 사용
"""

        with st.spinner("블로그 글을 작성 중입니다..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content([prompt] + images)
                result = response.text

                # --- 썸네일 생성 ---
                st.divider()
                st.subheader("🖼️ 썸네일")
                thumbnail = create_thumbnail(images[0], store_name, store_location)
                st.image(thumbnail, use_container_width=True)

                # 썸네일 다운로드
                buf = io.BytesIO()
                thumbnail.save(buf, format="JPEG", quality=95)
                st.download_button(
                    label="썸네일 다운로드",
                    data=buf.getvalue(),
                    file_name=f"{store_name}_썸네일.jpg",
                    mime="image/jpeg",
                )

                # --- 블로그 글 ---
                st.divider()
                st.subheader("📝 생성된 블로그 글")
                st.markdown(f'<div class="blog-output">{result}</div>', unsafe_allow_html=True)

                # 복사 버튼
                st.text_area("텍스트 복사용", result, height=200, label_visibility="collapsed")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
