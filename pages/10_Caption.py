import os
import base64
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="인스타 캡션", page_icon="📱")
st.markdown('<style>.stMainBlockContainer{max-width:720px;margin:0 auto}</style>', unsafe_allow_html=True)

st.title("📱 인스타 캡션 생성기")
st.caption("사진 올리면 인스타 감성 캡션을 바로 만들어줍니다")

default_key = os.environ.get("GROQ_API_KEY", "")
try:
    default_key = default_key or st.secrets.get("GROQ_API_KEY", "")
except Exception:
    pass

STYLES = {
    "감성적": "감성적이고 서정적인 톤. 짧은 문장, 여운 있게.",
    "유머러스": "재미있고 위트 있는 톤. 친구한테 말하듯이.",
    "힙한": "트렌디하고 힙한 톤. MZ세대 감성.",
    "먹방": "먹방 유튜버 스타일. 맛 표현 과장 OK.",
    "미니멀": "단어 3~5개만. 임팩트 있게.",
}

col1, col2 = st.columns(2)
with col1:
    store_name = st.text_input("가게 이름 (선택)", placeholder="예: 광장족발")
with col2:
    style = st.selectbox("캡션 스타일", list(STYLES.keys()))

col3, col4 = st.columns(2)
with col3:
    include_eng = st.checkbox("영어 캡션도 포함", value=True)
with col4:
    num_options = st.selectbox("캡션 개수", [3, 5, 10], index=0)

uploaded = st.file_uploader("음식 사진 업로드", type=["jpg", "jpeg", "png", "webp"])

if uploaded:
    st.image(uploaded, width=350)

if st.button("📱 캡션 생성", type="primary", use_container_width=True):
    if not default_key:
        st.error("API Key가 설정되지 않았습니다.")
    elif not uploaded:
        st.error("사진을 업로드해주세요.")
    else:
        uploaded.seek(0)
        data = base64.standard_b64encode(uploaded.read()).decode("utf-8")

        store_info = f"가게: {store_name}\n" if store_name else ""

        prompt = f"""인스타그램 맛집 캡션을 만들어주세요.

{store_info}스타일: {STYLES[style]}

## 규칙
- 한국어 캡션 {num_options}개 생성
{"- 각 한국어 캡션 밑에 영어 버전도 포함" if include_eng else ""}
- 사진에 보이는 음식을 기반으로 작성
- 이모지 적절히 사용
- 해시태그 5개씩 포함
- 각 캡션에 번호 붙이기
- 복사해서 바로 쓸 수 있게
"""

        content = [
            {"type": "image_url", "image_url": {"url": f"data:{uploaded.type};base64,{data}"}},
            {"type": "text", "text": prompt}
        ]

        with st.spinner("캡션 생성 중..."):
            try:
                client = Groq(api_key=default_key)
                resp = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=3000,
                )
                result = resp.choices[0].message.content
                st.divider()
                st.markdown(result)
                st.text_area("복사용", result, height=300, label_visibility="collapsed")
            except Exception as e:
                st.error(f"오류: {e}")
