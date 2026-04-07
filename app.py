import os
import base64
from datetime import datetime
import streamlit as st
import anthropic
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="블로그 글쓰기 AI", page_icon="✍️", layout="wide")

from auth import check_password
if not check_password():
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

.stMainBlockContainer { max-width: 780px; margin: 0 auto; }

/* 히어로 섹션 */
.hero {
    text-align: center;
    padding: 2rem 0 1rem;
}
.hero h1 {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 2.4rem;
    font-weight: 900;
    background: linear-gradient(135deg, #FF6B35, #FF4F6F);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.hero p {
    color: #888;
    font-size: 1rem;
}

/* 섹션 라벨 */
.section-label {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: #FF6B35;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.6rem;
    margin-top: 1.5rem;
}

/* 블로그 출력 */
.blog-output {
    background: #fafafa;
    padding: 2rem 2.2rem;
    border-radius: 16px;
    border: 1px solid #eee;
    line-height: 2;
    font-size: 1.02rem;
    font-family: 'Noto Sans KR', sans-serif;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

/* 구분선 */
.styled-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #ddd, transparent);
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)


def get_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            pass
    return key


# --- 히어로 ---
st.markdown("""
<div class="hero">
    <h1>맛집 블로그 글쓰기 AI</h1>
    <p>사진을 올리면 맛집 블로거처럼 글을 써드립니다</p>
</div>
""", unsafe_allow_html=True)

# --- 가게 정보 ---
st.markdown('<div class="section-label">가게 정보</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    store_name = st.text_input("가게 이름", placeholder="예: 을지로 골목식당", label_visibility="collapsed")
with col2:
    store_location = st.text_input("위치", placeholder="예: 서울 을지로3가역 근처", label_visibility="collapsed")

# --- 글 스타일 ---
st.markdown('<div class="section-label">글 스타일</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    tone = st.selectbox("톤 선택", ["친근하고 캐주얼한", "감성적이고 세련된", "유머러스한", "정보 중심의 깔끔한"],
                        label_visibility="collapsed")
with col4:
    length = st.selectbox("글 길이", ["짧게 (SNS용)", "보통 (블로그용)", "길게 (상세 리뷰)"],
                          label_visibility="collapsed")

# --- 사진 업로드 ---
st.markdown('<div class="section-label">사진 업로드</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "음식/공간 사진 업로드",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

if uploaded_files:
    cols = st.columns(min(len(uploaded_files), 5))
    for i, file in enumerate(uploaded_files):
        with cols[i % 5]:
            st.image(file, use_container_width=True)

st.markdown("")

# --- 생성 버튼 ---
if st.button("✍️ 블로그 글 생성", type="primary", use_container_width=True):
    api_key = get_api_key()
    if not api_key:
        st.error("API Key가 설정되지 않았습니다.")
    elif not uploaded_files:
        st.error("사진을 최소 1장 업로드해주세요.")
    elif not store_name:
        st.error("가게 이름을 입력해주세요.")
    else:
        image_contents = []
        for file in uploaded_files:
            file.seek(0)
            data = base64.standard_b64encode(file.read()).decode("utf-8")
            media_type = file.type or "image/jpeg"
            image_contents.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": data,
                },
            })

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

        messages_content = image_contents + [{"type": "text", "text": prompt}]

        with st.spinner("블로그 글을 작성 중입니다..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": messages_content}],
                )
                result = response.content[0].text

                # 히스토리에 저장
                if "blog_history" not in st.session_state:
                    st.session_state.blog_history = []
                st.session_state.blog_history.append({
                    "store_name": store_name,
                    "location": store_location,
                    "text": result,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

                st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)
                st.markdown("### 📝 생성된 블로그 글")
                st.markdown(f'<div class="blog-output">{result}</div>', unsafe_allow_html=True)
                st.markdown("")
                st.text_area("텍스트 복사용", result, height=200, label_visibility="collapsed")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
