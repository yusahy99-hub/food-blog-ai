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
    "화이트": "#FFFFFF",
    "블랙": "#1F2937",
}

TEMPLATES = {
    "모던 좌측": "modern",
    "센터": "center",
    "미니멀 바": "minimal",
    "매거진": "magazine",
    "프레임": "frame",
    "스플릿": "split",
}

FONT_OPTIONS = {
    "Noto Sans KR (고딕)": "Noto+Sans+KR",
    "Noto Serif KR (명조)": "Noto+Serif+KR",
    "Black Han Sans (굵은 제목)": "Black+Han+Sans",
    "Jua (둥근 고딕)": "Jua",
    "Do Hyeon (네모 고딕)": "Do+Hyeon",
    "Gaegu (손글씨)": "Gaegu",
    "Gowun Batang (바탕)": "Gowun+Batang",
    "Sunflower (라운드)": "Sunflower",
    "Gothic A1 (모던 고딕)": "Gothic+A1",
    "Nanum Myeongjo (나눔명조)": "Nanum+Myeongjo",
    "Nanum Gothic (나눔고딕)": "Nanum+Gothic",
    "Gamja Flower (귀여운)": "Gamja+Flower",
    "Single Day (캐주얼)": "Single+Day",
    "East Sea Dokdo (붓글씨)": "East+Sea+Dokdo",
    "Stylish (스타일리시)": "Stylish",
}

# --- 입력 ---
col1, col2 = st.columns(2)
with col1:
    store_name = st.text_input("가게 이름", placeholder="예: 광장족발")
with col2:
    store_location = st.text_input("위치 태그", placeholder="예: 성수")

subtitle = st.text_input("설명 문구", placeholder="예: 성수동 직장인 추천 족발맛집")

col3, col4, col5 = st.columns(3)
with col3:
    template_name = st.selectbox("템플릿", list(TEMPLATES.keys()))
with col4:
    color_name = st.selectbox("태그 색상", list(COLOR_PRESETS.keys()))
with col5:
    font_name = st.selectbox("폰트", list(FONT_OPTIONS.keys()))

# --- 글자 크기 설정 ---
with st.expander("글자 크기 설정"):
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        name_size = st.slider("가게 이름", 20, 80, 38, 2)
    with sc2:
        sub_size = st.slider("설명 문구", 10, 40, 16, 1)
    with sc3:
        tag_size = st.slider("위치 태그", 8, 30, 13, 1)

uploaded_file = st.file_uploader("배경 사진 업로드", type=["jpg", "jpeg", "png", "webp"])

accent = COLOR_PRESETS[color_name]
template = TEMPLATES[template_name]
font_id = FONT_OPTIONS[font_name]
font_css = font_id.replace("+", " ")
sizes = {"name": name_size, "sub": sub_size, "tag": tag_size}


def _is_white(c):
    return c.upper() in ("#FFFFFF", "#FFF")


def _head(fid, fname, sz):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family={fid}:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:transparent;font-family:'{fname}',sans-serif}}
"""


def _tag_html(loc, accent, style="pill"):
    if not loc:
        return ""
    w = _is_white(accent)
    if style == "pill":
        s = f"background:{accent};color:{'#222' if w else '#fff'};{'border:1.5px solid #ccc;' if w else ''}"
        return f'<div class="tag" style="{s}">{loc}</div>'
    elif style == "outline":
        bc = '#ccc' if w else accent
        return f'<div class="tag" style="border:2px solid {bc};color:{"#222" if w else "#fff"}">{loc}</div>'
    elif style == "underline":
        c = '#333' if w else accent
        return f'<span class="loc" style="color:{c}">{loc}</span>'
    return ""


# ===== 1. 모던 좌측 =====
def _modern(url, name, loc, sub, accent, sz, sc, fid, fname, S):
    tag = _tag_html(loc, accent, "pill")
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, sz) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{position:absolute;bottom:0;left:0;right:0;height:70%;
  background:linear-gradient(180deg,transparent 0%,rgba(0,0,0,0.12)30%,rgba(0,0,0,0.68)70%,rgba(0,0,0,0.88)100%)}}
.txt{{position:absolute;bottom:{int(44*sc)}px;left:{int(40*sc)}px;right:{int(40*sc)}px}}
.bracket{{width:{int(32*sc)}px;height:{int(32*sc)}px;
  border-left:{int(2.5*sc)}px solid rgba(255,255,255,0.45);
  border-top:{int(2.5*sc)}px solid rgba(255,255,255,0.45);margin-bottom:{int(16*sc)}px}}
.tag{{display:inline-block;padding:{int(5*sc)}px {int(16*sc)}px;border-radius:{int(20*sc)}px;
  font-size:{int(S["tag"]*sc)}px;font-weight:700;margin-bottom:{int(12*sc)}px;letter-spacing:.5px}}
.sub{{color:rgba(255,255,255,.88);font-size:{int(S["sub"]*sc)}px;font-weight:400;margin-bottom:{int(6*sc)}px;
  text-shadow:0 1px 4px rgba(0,0,0,.4)}}
.name{{color:#fff;font-size:{int(S["name"]*sc)}px;font-weight:900;line-height:1.15;letter-spacing:-1px;
  text-shadow:0 2px 8px rgba(0,0,0,.4)}}
</style></head><body>
<div class="card"><img src="{url}"/><div class="grad"></div>
<div class="txt"><div class="bracket"></div>{tag}{sub_h}<div class="name">{name}</div></div>
</div></body></html>"""


# ===== 2. 센터 =====
def _center(url, name, loc, sub, accent, sz, sc, fid, fname, S):
    tag = _tag_html(loc, accent, "outline")
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    ac = '#ccc' if _is_white(accent) else accent
    return _head(fid, fname, sz) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{position:absolute;inset:0;
  background:radial-gradient(ellipse at center,rgba(0,0,0,.2)0%,rgba(0,0,0,.6)100%)}}
.txt{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;width:80%}}
.deco{{width:{int(50*sc)}px;height:{int(2.5*sc)}px;background:{ac};margin:0 auto {int(18*sc)}px;border-radius:2px}}
.tag{{display:inline-block;padding:{int(5*sc)}px {int(18*sc)}px;border-radius:{int(20*sc)}px;
  font-size:{int(S["tag"]*sc)}px;font-weight:700;margin-bottom:{int(14*sc)}px;letter-spacing:1px}}
.name{{color:#fff;font-size:{int(S["name"]*sc)}px;font-weight:900;line-height:1.15;letter-spacing:-1px;
  text-shadow:0 3px 12px rgba(0,0,0,.5);margin-bottom:{int(14*sc)}px}}
.sub{{color:rgba(255,255,255,.9);font-size:{int(S["sub"]*sc)}px;font-weight:400;margin-bottom:{int(10*sc)}px;
  text-shadow:0 1px 4px rgba(0,0,0,.5)}}
.deco-b{{width:{int(50*sc)}px;height:{int(2.5*sc)}px;background:{ac};margin:{int(4*sc)}px auto 0;border-radius:2px}}
</style></head><body>
<div class="card"><img src="{url}"/><div class="grad"></div>
<div class="txt"><div class="deco"></div>{tag}<div class="name">{name}</div>{sub_h}<div class="deco-b"></div></div>
</div></body></html>"""


# ===== 3. 미니멀 바 =====
def _minimal(url, name, loc, sub, accent, sz, sc, fid, fname, S):
    w = _is_white(accent)
    lc = '#333' if w else accent
    bc = '#ddd' if w else accent
    loc_h = f'<span class="loc" style="color:{lc}">{loc}</span><span class="dot">·</span>' if loc else ""
    sub_h = f'<span class="sub">{sub}</span>' if sub else ""
    return _head(fid, fname, sz) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.bar{{position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,.82);
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  padding:{int(28*sc)}px {int(36*sc)}px;border-top:3px solid {bc}}}
.name{{color:#fff;font-size:{int(S["name"]*sc)}px;font-weight:900;letter-spacing:-.5px;margin-bottom:{int(8*sc)}px}}
.meta{{display:flex;align-items:center;gap:{int(6*sc)}px;flex-wrap:wrap}}
.loc{{font-size:{int(S["tag"]*sc)}px;font-weight:700;letter-spacing:.3px}}
.dot{{color:rgba(255,255,255,.3);font-size:{int(S["tag"]*sc)}px}}
.sub{{color:rgba(255,255,255,.7);font-size:{int(S["sub"]*sc)}px;font-weight:400}}
</style></head><body>
<div class="card"><img src="{url}"/>
<div class="bar"><div class="name">{name}</div><div class="meta">{loc_h}{sub_h}</div></div>
</div></body></html>"""


# ===== 4. 매거진 =====
def _magazine(url, name, loc, sub, accent, sz, sc, fid, fname, S):
    w = _is_white(accent)
    ac = '#333' if w else accent
    tag = ""
    if loc:
        tag = f'<div class="tag" style="background:{ac};color:#fff">{loc}</div>'
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, sz) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{position:absolute;inset:0;background:linear-gradient(160deg,rgba(0,0,0,.7)0%,transparent 50%,transparent 100%)}}
.txt{{position:absolute;top:{int(50*sc)}px;left:{int(44*sc)}px;max-width:65%}}
.tag{{display:inline-block;padding:{int(4*sc)}px {int(14*sc)}px;border-radius:{int(4*sc)}px;
  font-size:{int(S["tag"]*sc)}px;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:{int(16*sc)}px}}
.name{{color:#fff;font-size:{int(S["name"]*sc)}px;font-weight:900;line-height:1.1;letter-spacing:-1.5px;
  margin-bottom:{int(12*sc)}px;text-shadow:0 2px 10px rgba(0,0,0,.3)}}
.sub{{color:rgba(255,255,255,.8);font-size:{int(S["sub"]*sc)}px;font-weight:400;line-height:1.5;
  border-left:3px solid {ac};padding-left:{int(12*sc)}px}}
.corner{{position:absolute;bottom:{int(44*sc)}px;right:{int(44*sc)}px;
  width:{int(40*sc)}px;height:{int(40*sc)}px;
  border-right:3px solid rgba(255,255,255,.35);border-bottom:3px solid rgba(255,255,255,.35)}}
</style></head><body>
<div class="card"><img src="{url}"/><div class="grad"></div>
<div class="txt">{tag}<div class="name">{name}</div>{sub_h}</div>
<div class="corner"></div>
</div></body></html>"""


# ===== 5. 프레임 =====
def _framed(url, name, loc, sub, accent, sz, sc, fid, fname, S):
    w = _is_white(accent)
    bc = '#ccc' if w else accent
    tc = '#222' if w else '#fff'
    tag = ""
    if loc:
        tag = f'<div class="tag" style="border-color:{bc};color:{tc}">{loc}</div>'
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, sz) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{position:absolute;inset:0;background:rgba(0,0,0,.35)}}
.border-frame{{position:absolute;
  top:{int(28*sc)}px;left:{int(28*sc)}px;right:{int(28*sc)}px;bottom:{int(28*sc)}px;
  border:2px solid rgba(255,255,255,.4);border-radius:{int(8*sc)}px}}
.txt{{position:absolute;bottom:{int(56*sc)}px;left:{int(52*sc)}px;right:{int(52*sc)}px;text-align:center}}
.tag{{display:inline-block;padding:{int(4*sc)}px {int(16*sc)}px;border:1.5px solid;
  border-radius:{int(20*sc)}px;font-size:{int(S["tag"]*sc)}px;font-weight:700;
  margin-bottom:{int(14*sc)}px;letter-spacing:1px}}
.name{{color:#fff;font-size:{int(S["name"]*sc)}px;font-weight:900;line-height:1.15;letter-spacing:-.5px;
  margin-bottom:{int(10*sc)}px;text-shadow:0 2px 8px rgba(0,0,0,.4)}}
.sub{{color:rgba(255,255,255,.85);font-size:{int(S["sub"]*sc)}px;font-weight:400;
  text-shadow:0 1px 3px rgba(0,0,0,.4)}}
.top-deco{{position:absolute;top:{int(52*sc)}px;left:50%;transform:translateX(-50%);
  width:{int(40*sc)}px;height:{int(2.5*sc)}px;background:{bc};border-radius:2px}}
</style></head><body>
<div class="card"><img src="{url}"/><div class="grad"></div>
<div class="border-frame"></div><div class="top-deco"></div>
<div class="txt">{tag}<div class="name">{name}</div>{sub_h}</div>
</div></body></html>"""


# ===== 6. 스플릿 =====
def _split(url, name, loc, sub, accent, sz, sc, fid, fname, S):
    w = _is_white(accent)
    ac = '#333' if w else accent
    tag = ""
    if loc:
        tag = f'<span class="loc" style="color:{ac}">📍 {loc}</span>'
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, sz) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px;
  display:flex;flex-direction:column}}
.img-wrap{{position:relative;flex:1;overflow:hidden}}
.img-wrap img{{width:100%;height:100%;object-fit:cover}}
.bottom{{background:#fff;padding:{int(30*sc)}px {int(36*sc)}px;
  border-top:4px solid {ac}}}
.name{{color:#1a1a1a;font-size:{int(S["name"]*sc)}px;font-weight:900;letter-spacing:-.5px;margin-bottom:{int(8*sc)}px}}
.meta{{display:flex;align-items:center;gap:{int(10*sc)}px;flex-wrap:wrap}}
.loc{{font-size:{int(S["tag"]*sc)}px;font-weight:700}}
.sub{{color:#666;font-size:{int(S["sub"]*sc)}px;font-weight:400}}
.divider{{color:#ccc;font-size:{int(S["sub"]*sc)}px}}
</style></head><body>
<div class="card">
<div class="img-wrap"><img src="{url}"/></div>
<div class="bottom"><div class="name">{name}</div>
<div class="meta">{tag}{"<span class='divider'>|</span>" if loc and sub else ""}{sub_h}</div></div>
</div></body></html>"""


def build_html(url, name, loc, sub, accent, tpl, fid, fname, S, size=540):
    sc = size / 540
    funcs = {
        "modern": _modern, "center": _center, "minimal": _minimal,
        "magazine": _magazine, "frame": _framed, "split": _split,
    }
    return funcs[tpl](url, name, loc, sub, accent, size, sc, fid, fname, S)


if uploaded_file and store_name:
    uploaded_file.seek(0)
    img_data = base64.standard_b64encode(uploaded_file.read()).decode("utf-8")
    media_type = uploaded_file.type or "image/jpeg"
    img_url = f"data:{media_type};base64,{img_data}"

    st.divider()
    st.subheader("미리보기")

    preview = build_html(img_url, store_name, store_location, subtitle, accent, template, font_id, font_css, sizes, 540)
    components.html(preview, height=560, scrolling=False)

    download = build_html(img_url, store_name, store_location, subtitle, accent, template, font_id, font_css, sizes, 1080)

    st.download_button(
        label="📥 썸네일 다운로드 (HTML → 브라우저에서 스크린샷)",
        data=download,
        file_name=f"{store_name}_썸네일.html",
        mime="text/html",
        use_container_width=True,
    )
    st.caption("💡 다운받은 HTML을 브라우저에서 열고 우클릭 → '이미지로 저장' 또는 스크린샷하세요")
