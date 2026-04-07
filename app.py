import os
import base64
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="맛집 블로그 AI", page_icon="🍽️", layout="wide")

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


def get_api_key():
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass
    return key


# --- 사이드바 ---
with st.sidebar:
    st.header("글 스타일")
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

if uploaded_files:
    cols = st.columns(min(len(uploaded_files), 5))
    for i, file in enumerate(uploaded_files):
        with cols[i % 5]:
            st.image(file, use_container_width=True)

# --- 블로그 생성 ---
if st.button("✍️ 블로그 글 생성", type="primary", use_container_width=True):
    api_key = get_api_key()
    if not api_key:
        st.error("API Key가 설정되지 않았습니다.")
    elif not uploaded_files:
        st.error("사진을 최소 1장 업로드해주세요.")
    elif not store_name:
        st.error("가게 이름을 입력해주세요.")
    else:
        all_image_contents = []
        for file in uploaded_files:
            file.seek(0)
            data = base64.standard_b64encode(file.read()).decode("utf-8")
            media_type = file.type or "image/jpeg"
            all_image_contents.append({
                "type": "image_url",
                "image_url": {"url": f"data:{media_type};base64,{data}"},
            })

        length_guide = {
            "짧게 (SNS용)": "300자 내외로 짧고 임팩트 있게",
            "보통 (블로그용)": "800~1200자 정도로 적당히",
            "길게 (상세 리뷰)": "1500~2000자로 상세하게",
        }

        location_info = f"\n- 위치: {store_location}" if store_location else ""

        with st.spinner("블로그 글을 작성 중입니다..."):
            try:
                client = Groq(api_key=api_key)

                if len(all_image_contents) > 5:
                    descriptions = []
                    chunks = [all_image_contents[i:i+5] for i in range(0, len(all_image_contents), 5)]
                    for chunk in chunks:
                        analyze_prompt = f"이 사진들은 '{store_name}' 가게의 음식/공간 사진입니다. 각 사진에 보이는 음식, 재료, 플레이팅, 분위기 등을 한국어로 상세히 묘사해주세요."
                        chunk_content = chunk + [{"type": "text", "text": analyze_prompt}]
                        resp = client.chat.completions.create(
                            model="meta-llama/llama-4-scout-17b-16e-instruct",
                            messages=[{"role": "user", "content": chunk_content}],
                            max_tokens=2048,
                        )
                        descriptions.append(resp.choices[0].message.content)

                    combined = "\n\n".join(descriptions)
                    final_prompt = f"""당신은 한국의 인기 맛집 블로거입니다.
아래 사진 분석 결과와 가게 정보를 바탕으로 블로그 포스팅을 작성해주세요.

## 가게 정보
- 가게 이름: {store_name}{location_info}

## 사진 분석 결과
{combined}

## 작성 가이드
- 톤: {tone} 말투로 작성
- 분량: {length_guide[length]}
- 자연스러운 맛집 블로그 형식 (제목, 소개, 음식 설명, 총평 포함)
- 적절한 이모지 사용
- 해시태그 5~10개를 마지막에 포함

## 주의사항
- 사진 분석 결과를 기반으로만 작성 (없는 내용 지어내지 않기)
- 과장되지 않으면서도 매력적으로 표현
- 한국 맛집 블로그 특유의 생동감 있는 문체 사용
"""
                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{"role": "user", "content": final_prompt}],
                        max_tokens=4096,
                    )
                    result = response.choices[0].message.content
                else:
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
                    messages_content = all_image_contents + [{"type": "text", "text": prompt}]
                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{"role": "user", "content": messages_content}],
                        max_tokens=4096,
                    )
                    result = response.choices[0].message.content

                st.divider()
                st.subheader("📝 생성된 블로그 글")
                st.markdown(f'<div class="blog-output">{result}</div>', unsafe_allow_html=True)
                st.text_area("텍스트 복사용", result, height=200, label_visibility="collapsed")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
