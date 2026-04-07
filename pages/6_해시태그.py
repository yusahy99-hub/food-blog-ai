import os
import base64
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="해시태그 생성", page_icon="#️⃣")
st.markdown('<style>.stMainBlockContainer{max-width:720px;margin:0 auto}</style>', unsafe_allow_html=True)

st.title("#️⃣ 해시태그 생성기")
st.caption("사진이나 키워드로 인스타/블로그 해시태그를 자동 생성합니다")

default_key = os.environ.get("GROQ_API_KEY", "")
try:
    default_key = default_key or st.secrets.get("GROQ_API_KEY", "")
except Exception:
    pass

platform = st.selectbox("플랫폼", ["인스타그램", "네이버 블로그", "둘 다"])

col1, col2 = st.columns(2)
with col1:
    food_type = st.text_input("음식 종류", placeholder="예: 족발, 파스타, 스시")
with col2:
    location = st.text_input("지역", placeholder="예: 성수동, 강남, 홍대")

uploaded = st.file_uploader("사진 업로드 (선택)", type=["jpg", "jpeg", "png", "webp"])

if st.button("#️⃣ 해시태그 생성", type="primary", use_container_width=True):
    if not default_key:
        st.error("API Key가 설정되지 않았습니다.")
    elif not food_type and not uploaded:
        st.error("음식 종류를 입력하거나 사진을 업로드해주세요.")
    else:
        content = []
        if uploaded:
            uploaded.seek(0)
            data = base64.standard_b64encode(uploaded.read()).decode("utf-8")
            content.append({"type": "image_url", "image_url": {"url": f"data:{uploaded.type};base64,{data}"}})

        platform_guide = {
            "인스타그램": "인스타그램용 해시태그 30개. 인기 태그 + 중간 인기 태그 + 니치 태그를 골고루 섞어서.",
            "네이버 블로그": "네이버 블로그용 태그 15개. 검색 유입이 잘 되는 키워드 중심으로.",
            "둘 다": "인스타그램용 해시태그 30개와 네이버 블로그용 태그 15개를 구분해서.",
        }

        prompt = f"""맛집 블로거/인플루언서를 위한 해시태그를 생성해주세요.

음식: {food_type or '사진 참고'}
지역: {location or '미지정'}
플랫폼: {platform_guide[platform]}

## 규칙
- 한국어 해시태그 위주 (영어 5개 이내 섞기)
- 인기도 순으로 정렬
- # 붙여서 출력
- 카테고리별로 나눠서 출력 (맛집, 음식, 지역, 분위기 등)
- 복사하기 편하게 한 줄에 쭉 나열하는 버전도 마지막에 포함
"""
        content.append({"type": "text", "text": prompt})

        with st.spinner("해시태그 생성 중..."):
            try:
                client = Groq(api_key=default_key)
                resp = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=2048,
                )
                result = resp.choices[0].message.content
                st.divider()
                st.markdown(result)
                st.text_area("복사용", result, height=200, label_visibility="collapsed")
            except Exception as e:
                st.error(f"오류: {e}")
