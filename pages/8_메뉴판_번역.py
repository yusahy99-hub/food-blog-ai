import os
import base64
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="메뉴판 번역", page_icon="🌐")

from auth import check_password
if not check_password():
    st.stop()

st.markdown('<style>.stMainBlockContainer{max-width:720px;margin:0 auto}</style>', unsafe_allow_html=True)

st.title("🌐 메뉴판 번역")
st.caption("메뉴판 사진을 올리면 다국어로 번역 + 구글맵 리뷰용 텍스트도 생성합니다")

default_key = os.environ.get("GROQ_API_KEY", "")
try:
    default_key = default_key or st.secrets.get("GROQ_API_KEY", "")
except Exception:
    pass

lang = st.multiselect("번역 언어", ["영어", "일본어", "중국어 (간체)", "중국어 (번체)", "태국어", "베트남어"],
                      default=["영어", "일본어"])

store_name = st.text_input("가게 이름 (선택)", placeholder="구글맵 리뷰 생성 시 사용")

uploaded = st.file_uploader("메뉴판 사진 업로드", type=["jpg", "jpeg", "png", "webp"])

if uploaded:
    st.image(uploaded, caption="업로드된 메뉴판", width=400)

output_type = st.multiselect("출력 형식", ["메뉴 번역", "구글맵 리뷰 (복사용)", "인스타 캡션 (영어)"],
                              default=["메뉴 번역"])

if st.button("🌐 번역하기", type="primary", use_container_width=True):
    if not default_key:
        st.error("API Key가 설정되지 않았습니다.")
    elif not uploaded:
        st.error("메뉴판 사진을 업로드해주세요.")
    else:
        uploaded.seek(0)
        data = base64.standard_b64encode(uploaded.read()).decode("utf-8")

        lang_str = ", ".join(lang)
        store_info = f"\n가게 이름: {store_name}" if store_name else ""

        sections = []
        if "메뉴 번역" in output_type:
            sections.append(f"""## 1. 메뉴 번역
이 메뉴판의 모든 메뉴를 아래 형식으로 번역해주세요:
- 한국어 원문 | {lang_str} 번역 | 가격
표 형식으로 깔끔하게 정리해주세요.""")

        if "구글맵 리뷰 (복사용)" in output_type:
            sections.append(f"""## 2. 구글맵 리뷰 텍스트
{store_info}
이 메뉴판을 참고하여 외국인 관광객이 구글맵에 올릴 수 있는 영어 리뷰를 작성해주세요.
- 3~5줄 정도
- 메뉴 추천 포함
- 가격대 언급
- 별점 추천 (⭐ 이모지 사용)
- 복사해서 바로 붙여넣기 가능하게""")

        if "인스타 캡션 (영어)" in output_type:
            sections.append(f"""## 3. 인스타 캡션 (영어)
{store_info}
이 메뉴판의 음식을 기반으로 영어 인스타그램 캡션을 작성해주세요.
- 감성적이고 짧게 (2~3줄)
- 음식 이모지 사용
- 영어 해시태그 10개 포함""")

        prompt = f"""이 사진은 한국 음식점의 메뉴판입니다.
{chr(10).join(sections)}
"""

        content = [
            {"type": "image_url", "image_url": {"url": f"data:{uploaded.type};base64,{data}"}},
            {"type": "text", "text": prompt}
        ]

        with st.spinner("번역 중..."):
            try:
                client = Groq(api_key=default_key)
                resp = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=4096,
                )
                result = resp.choices[0].message.content
                st.divider()
                st.markdown(result)
                st.text_area("복사용", result, height=300, label_visibility="collapsed")
            except Exception as e:
                st.error(f"오류: {e}")
