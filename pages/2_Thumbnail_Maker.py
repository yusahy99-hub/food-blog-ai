import base64
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="썸네일 만들기", page_icon="🖼️")

st.markdown("""
<style>
    .stMainBlockContainer { max-width: 720px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("🖼️ 썸네일 만들기")
st.caption("사진 + 가게 정보 입력 → 미리보기 확인 → 다운로드")

COLOR_PRESETS = {
    "오렌지": "#ff7820",
    "레드": "#dc3232",
    "블루": "#2878dc",
    "그린": "#28b464",
    "퍼플": "#8c3cdc",
    "골드": "#d2aa32",
    "블랙": "#222222",
}

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

accent = COLOR_PRESETS[color_name]

if uploaded_file and store_name:
    uploaded_file.seek(0)
    img_data = base64.standard_b64encode(uploaded_file.read()).decode("utf-8")
    media_type = uploaded_file.type or "image/jpeg"
    img_url = f"data:{media_type};base64,{img_data}"

    tag_html = ""
    if store_location:
        tag_html = f'<span class="tag" style="background:{accent};">{store_location}</span>'

    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<p class="subtitle">{subtitle}</p>'

    # 꺾쇠 장식
    bracket_html = '<div class="bracket"></div>'

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

.thumbnail {{
    position: relative;
    width: 540px;
    height: 540px;
    overflow: hidden;
    font-family: 'Noto Sans KR', sans-serif;
    background: #000;
}}

.thumbnail img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}

.overlay {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 65%;
    background: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.75) 60%, rgba(0,0,0,0.9) 100%);
}}

.text-area {{
    position: absolute;
    bottom: 40px;
    left: 36px;
    right: 36px;
}}

.bracket {{
    position: relative;
    margin-bottom: 14px;
    width: 36px;
    height: 36px;
    border-left: 3px solid rgba(255,255,255,0.7);
    border-top: 3px solid rgba(255,255,255,0.7);
}}

.tag {{
    display: inline-block;
    padding: 6px 18px;
    border-radius: 6px;
    color: white;
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 12px;
}}

.subtitle {{
    color: rgba(255,255,255,0.92);
    font-size: 18px;
    font-weight: 400;
    margin-bottom: 8px;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
}}

.store-name {{
    color: white;
    font-size: 42px;
    font-weight: 900;
    line-height: 1.2;
    text-shadow: 2px 2px 6px rgba(0,0,0,0.6);
}}
</style>
</head>
<body>
<div class="thumbnail" id="thumbnail">
    <img src="{img_url}" />
    <div class="overlay"></div>
    <div class="text-area">
        {bracket_html}
        {tag_html}
        {subtitle_html}
        <div class="store-name">{store_name}</div>
    </div>
</div>
</body>
</html>
"""

    st.divider()
    st.subheader("미리보기")
    components.html(html_content, height=560, scrolling=False)

    # --- 다운로드용 고해상도 HTML (1080x1080) ---
    download_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
.thumbnail {{
    position: relative;
    width: 1080px;
    height: 1080px;
    overflow: hidden;
    font-family: 'Noto Sans KR', sans-serif;
    background: #000;
}}
.thumbnail img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}
.overlay {{
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 65%;
    background: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.75) 60%, rgba(0,0,0,0.9) 100%);
}}
.text-area {{
    position: absolute;
    bottom: 80px;
    left: 70px;
    right: 70px;
}}
.bracket {{
    position: relative;
    margin-bottom: 28px;
    width: 70px;
    height: 70px;
    border-left: 5px solid rgba(255,255,255,0.7);
    border-top: 5px solid rgba(255,255,255,0.7);
}}
.tag {{
    display: inline-block;
    padding: 12px 36px;
    border-radius: 10px;
    color: white;
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 24px;
}}
.subtitle {{
    color: rgba(255,255,255,0.92);
    font-size: 36px;
    font-weight: 400;
    margin-bottom: 16px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}}
.store-name {{
    color: white;
    font-size: 84px;
    font-weight: 900;
    line-height: 1.2;
    text-shadow: 3px 3px 8px rgba(0,0,0,0.6);
}}
</style>
</head>
<body>
<div class="thumbnail">
    <img src="{img_url}" />
    <div class="overlay"></div>
    <div class="text-area">
        {bracket_html}
        {tag_html}
        {subtitle_html}
        <div class="store-name">{store_name}</div>
    </div>
</div>
</body>
</html>
"""

    st.download_button(
        label="📥 HTML 썸네일 다운로드 (브라우저에서 스크린샷)",
        data=download_html,
        file_name=f"{store_name}_썸네일.html",
        mime="text/html",
        use_container_width=True,
    )
    st.caption("다운로드한 HTML 파일을 브라우저에서 열고 스크린샷(캡처)하면 이미지로 저장됩니다.")

elif not uploaded_file:
    pass
elif not store_name:
    st.info("가게 이름을 입력해주세요.")
