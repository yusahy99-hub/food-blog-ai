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
    "오렌지": "#FF6B35",
    "코랄": "#FF4F6F",
    "블루": "#3B82F6",
    "민트": "#10B981",
    "퍼플": "#8B5CF6",
    "골드": "#F59E0B",
    "블랙": "#1F2937",
}

TEMPLATE_OPTIONS = {
    "모던 (하단 좌측)": "modern",
    "센터 (중앙 정렬)": "center",
    "미니멀 (하단 바)": "minimal",
}

# --- 입력 ---
col1, col2 = st.columns(2)
with col1:
    store_name = st.text_input("가게 이름", placeholder="예: 광장족발")
with col2:
    store_location = st.text_input("위치 태그", placeholder="예: 성수")

col3, col4, col5 = st.columns(3)
with col3:
    subtitle = st.text_input("설명 문구", placeholder="예: 성수동 직장인 추천 족발맛집")
with col4:
    color_name = st.selectbox("태그 색상", list(COLOR_PRESETS.keys()))
with col5:
    template_name = st.selectbox("템플릿", list(TEMPLATE_OPTIONS.keys()))

uploaded_file = st.file_uploader("배경 사진 업로드", type=["jpg", "jpeg", "png", "webp"])

accent = COLOR_PRESETS[color_name]
template = TEMPLATE_OPTIONS[template_name]


def build_html(img_url, store_name, store_location, subtitle, accent, template, size=540):
    scale = size / 540

    if template == "modern":
        return _modern(img_url, store_name, store_location, subtitle, accent, size, scale)
    elif template == "center":
        return _center(img_url, store_name, store_location, subtitle, accent, size, scale)
    else:
        return _minimal(img_url, store_name, store_location, subtitle, accent, size, scale)


def _modern(img_url, name, loc, sub, accent, sz, sc):
    tag = f'<div class="tag" style="background:{accent};">{loc}</div>' if loc else ""
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:transparent}}
.card{{
    position:relative;width:{sz}px;height:{sz}px;overflow:hidden;
    font-family:'Noto Sans KR',sans-serif;border-radius:{int(12*sc)}px;
}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{
    position:absolute;bottom:0;left:0;right:0;height:70%;
    background:linear-gradient(180deg,transparent 0%,rgba(0,0,0,0.15) 30%,rgba(0,0,0,0.7) 70%,rgba(0,0,0,0.88) 100%);
}}
.txt{{position:absolute;bottom:{int(44*sc)}px;left:{int(40*sc)}px;right:{int(40*sc)}px}}
.bracket{{
    width:{int(32*sc)}px;height:{int(32*sc)}px;
    border-left:{int(2.5*sc)}px solid rgba(255,255,255,0.5);
    border-top:{int(2.5*sc)}px solid rgba(255,255,255,0.5);
    margin-bottom:{int(16*sc)}px;
}}
.tag{{
    display:inline-block;padding:{int(5*sc)}px {int(16*sc)}px;
    border-radius:{int(20*sc)}px;color:#fff;
    font-size:{int(13*sc)}px;font-weight:700;
    margin-bottom:{int(12*sc)}px;
    letter-spacing:0.5px;
}}
.sub{{
    color:rgba(255,255,255,0.88);font-size:{int(16*sc)}px;font-weight:400;
    margin-bottom:{int(6*sc)}px;letter-spacing:-0.2px;
    text-shadow:0 1px 4px rgba(0,0,0,0.4);
}}
.name{{
    color:#fff;font-size:{int(38*sc)}px;font-weight:900;
    line-height:1.15;letter-spacing:-1px;
    text-shadow:0 2px 8px rgba(0,0,0,0.4);
}}
</style></head><body>
<div class="card"><img src="{img_url}"/><div class="grad"></div>
<div class="txt"><div class="bracket"></div>{tag}{sub_h}<div class="name">{name}</div></div>
</div></body></html>"""


def _center(img_url, name, loc, sub, accent, sz, sc):
    tag = f'<div class="tag" style="background:{accent};">{loc}</div>' if loc else ""
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:transparent}}
.card{{
    position:relative;width:{sz}px;height:{sz}px;overflow:hidden;
    font-family:'Noto Sans KR',sans-serif;border-radius:{int(12*sc)}px;
}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{
    position:absolute;inset:0;
    background:radial-gradient(ellipse at center,rgba(0,0,0,0.25) 0%,rgba(0,0,0,0.6) 100%);
}}
.txt{{
    position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
    text-align:center;width:80%;
}}
.line{{width:{int(50*sc)}px;height:{int(2.5*sc)}px;background:{accent};margin:0 auto {int(18*sc)}px;border-radius:2px}}
.tag{{
    display:inline-block;padding:{int(5*sc)}px {int(18*sc)}px;
    border:2px solid {accent};border-radius:{int(20*sc)}px;
    color:#fff;font-size:{int(13*sc)}px;font-weight:700;
    margin-bottom:{int(14*sc)}px;letter-spacing:1px;
}}
.sub{{
    color:rgba(255,255,255,0.9);font-size:{int(16*sc)}px;font-weight:400;
    margin-bottom:{int(10*sc)}px;letter-spacing:0.3px;
    text-shadow:0 1px 4px rgba(0,0,0,0.5);
}}
.name{{
    color:#fff;font-size:{int(44*sc)}px;font-weight:900;
    line-height:1.15;letter-spacing:-1px;
    text-shadow:0 3px 12px rgba(0,0,0,0.5);
    margin-bottom:{int(14*sc)}px;
}}
.line-b{{width:{int(50*sc)}px;height:{int(2.5*sc)}px;background:{accent};margin:{int(4*sc)}px auto 0;border-radius:2px}}
</style></head><body>
<div class="card"><img src="{img_url}"/><div class="grad"></div>
<div class="txt"><div class="line"></div>{tag}<div class="name">{name}</div>{sub_h}<div class="line-b"></div></div>
</div></body></html>"""


def _minimal(img_url, name, loc, sub, accent, sz, sc):
    loc_h = f'<span class="loc">{loc}</span><span class="dot">·</span>' if loc else ""
    sub_h = f'<span class="sub">{sub}</span>' if sub else ""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:transparent}}
.card{{
    position:relative;width:{sz}px;height:{sz}px;overflow:hidden;
    font-family:'Noto Sans KR',sans-serif;border-radius:{int(12*sc)}px;
}}
.card img{{width:100%;height:100%;object-fit:cover}}
.bar{{
    position:absolute;bottom:0;left:0;right:0;
    background:rgba(0,0,0,0.82);
    backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
    padding:{int(28*sc)}px {int(36*sc)}px;
    border-top:3px solid {accent};
}}
.name{{
    color:#fff;font-size:{int(30*sc)}px;font-weight:900;
    letter-spacing:-0.5px;margin-bottom:{int(8*sc)}px;
}}
.meta{{display:flex;align-items:center;gap:{int(6*sc)}px;flex-wrap:wrap}}
.loc{{
    color:{accent};font-size:{int(14*sc)}px;font-weight:700;
    letter-spacing:0.3px;
}}
.dot{{color:rgba(255,255,255,0.3);font-size:{int(14*sc)}px}}
.sub{{color:rgba(255,255,255,0.7);font-size:{int(14*sc)}px;font-weight:400}}
</style></head><body>
<div class="card"><img src="{img_url}"/>
<div class="bar"><div class="name">{name}</div><div class="meta">{loc_h}{sub_h}</div></div>
</div></body></html>"""


if uploaded_file and store_name:
    uploaded_file.seek(0)
    img_data = base64.standard_b64encode(uploaded_file.read()).decode("utf-8")
    media_type = uploaded_file.type or "image/jpeg"
    img_url = f"data:{media_type};base64,{img_data}"

    st.divider()
    st.subheader("미리보기")

    preview = build_html(img_url, store_name, store_location, subtitle, accent, template, 540)
    components.html(preview, height=560, scrolling=False)

    download = build_html(img_url, store_name, store_location, subtitle, accent, template, 1080)

    st.download_button(
        label="📥 썸네일 다운로드 (HTML → 브라우저에서 스크린샷)",
        data=download,
        file_name=f"{store_name}_썸네일.html",
        mime="text/html",
        use_container_width=True,
    )
    st.caption("💡 다운받은 HTML을 브라우저에서 열고 우클릭 → '이미지로 저장' 또는 스크린샷하세요")
