import io
import base64
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

st.set_page_config(page_title="썸네일 만들기", page_icon="🖼️")

from auth import check_password
if not check_password():
    st.stop()

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

TEXT_COLORS = {
    "흰색": "#FFFFFF",
    "검정": "#1a1a1a",
    "연회색": "#e0e0e0",
    "크림": "#FFF8E7",
    "오렌지": "#FF6B35",
    "코랄": "#FF4F6F",
    "골드": "#F59E0B",
}

TEMPLATES = {
    "모던 좌측": "modern",
    "센터": "center",
    "미니멀 바": "minimal",
    "매거진": "magazine",
    "프레임": "frame",
    "스플릿": "split",
    "시네마틱": "cinematic",
    "폴라로이드": "polaroid",
    "네온": "neon",
    "타이포": "typo",
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

col3, col4 = st.columns(2)
with col3:
    template_name = st.selectbox("템플릿", list(TEMPLATES.keys()))
with col4:
    font_name = st.selectbox("폰트", list(FONT_OPTIONS.keys()))

col5, col6 = st.columns(2)
with col5:
    color_name = st.selectbox("태그 색상", list(COLOR_PRESETS.keys()))
with col6:
    text_color_name = st.selectbox("글씨 색상", list(TEXT_COLORS.keys()))

with st.expander("글자 크기 설정"):
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        name_size = st.slider("가게 이름", 20, 80, 38, 2)
    with sc2:
        sub_size = st.slider("설명 문구", 10, 40, 16, 1)
    with sc3:
        tag_size = st.slider("위치 태그", 8, 30, 13, 1)

uploaded_file = st.file_uploader("배경 사진 업로드", type=["jpg", "jpeg", "png", "webp"])

# 회전 버튼
rot_col1, rot_col2, rot_col3, rot_col4 = st.columns(4)
with rot_col1:
    if st.button("↩️ 왼쪽 90°"):
        st.session_state["img_rot"] = st.session_state.get("img_rot", 0) + 90
with rot_col2:
    if st.button("↪️ 오른쪽 90°"):
        st.session_state["img_rot"] = st.session_state.get("img_rot", 0) - 90
with rot_col3:
    if st.button("🔄 180°"):
        st.session_state["img_rot"] = st.session_state.get("img_rot", 0) + 180
with rot_col4:
    if st.button("초기화"):
        st.session_state["img_rot"] = 0

img_rotation = st.session_state.get("img_rot", 0) % 360

accent = COLOR_PRESETS[color_name]
text_c = TEXT_COLORS[text_color_name]
template = TEMPLATES[template_name]
font_id = FONT_OPTIONS[font_name]
font_css = font_id.replace("+", " ")
sizes = {"name": name_size, "sub": sub_size, "tag": tag_size}


def _w(c):
    return c.upper() in ("#FFFFFF", "#FFF")


def _head(fid, fname, rot=0):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family={fid}:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:transparent;font-family:'{fname}',sans-serif}}
"""


def _tag(loc, accent, tc):
    if not loc:
        return ""
    w = _w(accent)
    bg = accent
    c = '#222' if w else tc
    border = 'border:1.5px solid #ccc;' if w else ''
    return f'<div class="tag" style="background:{bg};color:{c};{border}">{loc}</div>'


# ===== 1. 모던 좌측 =====
def _modern(url, name, loc, sub, accent, tc, sz, sc, fid, fname, S, rot=0):
    tag = _tag(loc, accent, tc)
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, rot) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{position:absolute;bottom:0;left:0;right:0;height:70%;
  background:linear-gradient(180deg,transparent 0%,rgba(0,0,0,0.12)30%,rgba(0,0,0,0.68)70%,rgba(0,0,0,0.88)100%)}}
.txt{{position:absolute;bottom:{int(44*sc)}px;left:{int(40*sc)}px;right:{int(40*sc)}px}}
.bracket{{width:{int(32*sc)}px;height:{int(32*sc)}px;
  border-left:{int(2.5*sc)}px solid {tc}40;border-top:{int(2.5*sc)}px solid {tc}40;margin-bottom:{int(16*sc)}px}}
.tag{{display:inline-block;padding:{int(5*sc)}px {int(16*sc)}px;border-radius:{int(20*sc)}px;
  font-size:{int(S["tag"]*sc)}px;font-weight:700;margin-bottom:{int(12*sc)}px}}
.sub{{color:{tc}dd;font-size:{int(S["sub"]*sc)}px;font-weight:400;margin-bottom:{int(6*sc)}px;
  text-shadow:0 1px 4px rgba(0,0,0,.4)}}
.name{{color:{tc};font-size:{int(S["name"]*sc)}px;font-weight:900;line-height:1.15;letter-spacing:-1px;
  text-shadow:0 2px 8px rgba(0,0,0,.4)}}
</style></head><body>
<div class="card"><img src="{url}"/><div class="grad"></div>
<div class="txt"><div class="bracket"></div>{tag}{sub_h}<div class="name">{name}</div></div>
</div></body></html>"""


# ===== 2. 센터 =====
def _center(url, name, loc, sub, accent, tc, sz, sc, fid, fname, S, rot=0):
    w = _w(accent)
    ac = '#ccc' if w else accent
    tag = f'<div class="tag" style="border:2px solid {ac};color:{tc}">{loc}</div>' if loc else ""
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, rot) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(0,0,0,.2)0%,rgba(0,0,0,.6)100%)}}
.txt{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;width:80%}}
.deco{{width:{int(50*sc)}px;height:{int(2.5*sc)}px;background:{ac};margin:0 auto {int(18*sc)}px;border-radius:2px}}
.tag{{display:inline-block;padding:{int(5*sc)}px {int(18*sc)}px;border-radius:{int(20*sc)}px;
  font-size:{int(S["tag"]*sc)}px;font-weight:700;margin-bottom:{int(14*sc)}px;letter-spacing:1px}}
.name{{color:{tc};font-size:{int(S["name"]*sc)}px;font-weight:900;line-height:1.15;letter-spacing:-1px;
  text-shadow:0 3px 12px rgba(0,0,0,.5);margin-bottom:{int(14*sc)}px}}
.sub{{color:{tc}dd;font-size:{int(S["sub"]*sc)}px;font-weight:400;margin-bottom:{int(10*sc)}px;
  text-shadow:0 1px 4px rgba(0,0,0,.5)}}
.deco-b{{width:{int(50*sc)}px;height:{int(2.5*sc)}px;background:{ac};margin:{int(4*sc)}px auto 0;border-radius:2px}}
</style></head><body>
<div class="card"><img src="{url}"/><div class="grad"></div>
<div class="txt"><div class="deco"></div>{tag}<div class="name">{name}</div>{sub_h}<div class="deco-b"></div></div>
</div></body></html>"""


# ===== 3. 미니멀 바 =====
def _minimal(url, name, loc, sub, accent, tc, sz, sc, fid, fname, S, rot=0):
    w = _w(accent)
    bc = '#ddd' if w else accent
    lc = '#333' if w else accent
    loc_h = f'<span class="loc" style="color:{lc}">{loc}</span><span class="dot">·</span>' if loc else ""
    sub_h = f'<span class="sub">{sub}</span>' if sub else ""
    return _head(fid, fname, rot) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.bar{{position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,.82);
  backdrop-filter:blur(12px);padding:{int(28*sc)}px {int(36*sc)}px;border-top:3px solid {bc}}}
.name{{color:{tc};font-size:{int(S["name"]*sc)}px;font-weight:900;margin-bottom:{int(8*sc)}px}}
.meta{{display:flex;align-items:center;gap:{int(6*sc)}px;flex-wrap:wrap}}
.loc{{font-size:{int(S["tag"]*sc)}px;font-weight:700}}
.dot{{color:rgba(255,255,255,.3);font-size:{int(S["tag"]*sc)}px}}
.sub{{color:{tc}aa;font-size:{int(S["sub"]*sc)}px;font-weight:400}}
</style></head><body>
<div class="card"><img src="{url}"/>
<div class="bar"><div class="name">{name}</div><div class="meta">{loc_h}{sub_h}</div></div>
</div></body></html>"""


# ===== 4. 매거진 =====
def _magazine(url, name, loc, sub, accent, tc, sz, sc, fid, fname, S, rot=0):
    w = _w(accent)
    ac = '#333' if w else accent
    tag = f'<div class="tag" style="background:{ac};color:#fff">{loc}</div>' if loc else ""
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, rot) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{position:absolute;inset:0;background:linear-gradient(160deg,rgba(0,0,0,.7)0%,transparent 50%,transparent 100%)}}
.txt{{position:absolute;top:{int(50*sc)}px;left:{int(44*sc)}px;max-width:65%}}
.tag{{display:inline-block;padding:{int(4*sc)}px {int(14*sc)}px;border-radius:{int(4*sc)}px;
  font-size:{int(S["tag"]*sc)}px;font-weight:700;letter-spacing:2px;margin-bottom:{int(16*sc)}px}}
.name{{color:{tc};font-size:{int(S["name"]*sc)}px;font-weight:900;line-height:1.1;letter-spacing:-1.5px;
  margin-bottom:{int(12*sc)}px;text-shadow:0 2px 10px rgba(0,0,0,.3)}}
.sub{{color:{tc}cc;font-size:{int(S["sub"]*sc)}px;font-weight:400;line-height:1.5;
  border-left:3px solid {ac};padding-left:{int(12*sc)}px}}
.corner{{position:absolute;bottom:{int(44*sc)}px;right:{int(44*sc)}px;
  width:{int(40*sc)}px;height:{int(40*sc)}px;
  border-right:3px solid {tc}55;border-bottom:3px solid {tc}55}}
</style></head><body>
<div class="card"><img src="{url}"/><div class="grad"></div>
<div class="txt">{tag}<div class="name">{name}</div>{sub_h}</div>
<div class="corner"></div>
</div></body></html>"""


# ===== 5. 프레임 =====
def _framed(url, name, loc, sub, accent, tc, sz, sc, fid, fname, S, rot=0):
    w = _w(accent)
    bc = '#ccc' if w else accent
    tag = f'<div class="tag" style="border-color:{bc};color:{tc}">{loc}</div>' if loc else ""
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, rot) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{position:absolute;inset:0;background:rgba(0,0,0,.35)}}
.border-frame{{position:absolute;
  top:{int(28*sc)}px;left:{int(28*sc)}px;right:{int(28*sc)}px;bottom:{int(28*sc)}px;
  border:2px solid {tc}66;border-radius:{int(8*sc)}px}}
.txt{{position:absolute;bottom:{int(56*sc)}px;left:{int(52*sc)}px;right:{int(52*sc)}px;text-align:center}}
.tag{{display:inline-block;padding:{int(4*sc)}px {int(16*sc)}px;border:1.5px solid;
  border-radius:{int(20*sc)}px;font-size:{int(S["tag"]*sc)}px;font-weight:700;
  margin-bottom:{int(14*sc)}px;letter-spacing:1px}}
.name{{color:{tc};font-size:{int(S["name"]*sc)}px;font-weight:900;line-height:1.15;
  margin-bottom:{int(10*sc)}px;text-shadow:0 2px 8px rgba(0,0,0,.4)}}
.sub{{color:{tc}dd;font-size:{int(S["sub"]*sc)}px;font-weight:400;text-shadow:0 1px 3px rgba(0,0,0,.4)}}
.top-deco{{position:absolute;top:{int(52*sc)}px;left:50%;transform:translateX(-50%);
  width:{int(40*sc)}px;height:{int(2.5*sc)}px;background:{bc};border-radius:2px}}
</style></head><body>
<div class="card"><img src="{url}"/><div class="grad"></div>
<div class="border-frame"></div><div class="top-deco"></div>
<div class="txt">{tag}<div class="name">{name}</div>{sub_h}</div>
</div></body></html>"""


# ===== 6. 스플릿 =====
def _split(url, name, loc, sub, accent, tc, sz, sc, fid, fname, S, rot=0):
    w = _w(accent)
    ac = '#333' if w else accent
    tag = f'<span class="loc" style="color:{ac}">📍 {loc}</span>' if loc else ""
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, rot) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px;
  display:flex;flex-direction:column}}
.img-wrap{{position:relative;flex:1;overflow:hidden}}
.img-wrap img{{width:100%;height:100%;object-fit:cover}}
.bottom{{background:#fff;padding:{int(30*sc)}px {int(36*sc)}px;border-top:4px solid {ac}}}
.name{{color:#1a1a1a;font-size:{int(S["name"]*sc)}px;font-weight:900;margin-bottom:{int(8*sc)}px}}
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


# ===== 7. 시네마틱 =====
def _cinematic(url, name, loc, sub, accent, tc, sz, sc, fid, fname, S, rot=0):
    ac = accent
    tag = f'<span class="loc">{loc}</span>' if loc else ""
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    bar = int(sz * 0.1)
    return _head(fid, fname, rot) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.bar-t,.bar-b{{position:absolute;left:0;right:0;background:#000;height:{bar}px}}
.bar-t{{top:0}}.bar-b{{bottom:0}}
.grad{{position:absolute;inset:0;background:linear-gradient(180deg,transparent 60%,rgba(0,0,0,.7)100%)}}
.txt{{position:absolute;bottom:{bar + int(20*sc)}px;left:{int(40*sc)}px;right:{int(40*sc)}px}}
.loc{{color:{ac};font-size:{int(S["tag"]*sc)}px;font-weight:700;letter-spacing:2px;
  margin-bottom:{int(8*sc)}px;display:block}}
.name{{color:{tc};font-size:{int(S["name"]*sc)}px;font-weight:900;line-height:1.1;
  text-shadow:0 2px 10px rgba(0,0,0,.5)}}
.sub{{color:{tc}bb;font-size:{int(S["sub"]*sc)}px;margin-top:{int(8*sc)}px}}
</style></head><body>
<div class="card"><img src="{url}"/><div class="bar-t"></div><div class="bar-b"></div><div class="grad"></div>
<div class="txt">{tag}<div class="name">{name}</div>{sub_h}</div>
</div></body></html>"""


# ===== 8. 폴라로이드 =====
def _polaroid(url, name, loc, sub, accent, tc, sz, sc, fid, fname, S, rot=0):
    pad = int(24*sc)
    bot = int(80*sc)
    return _head(fid, fname, rot) + f"""
.wrap{{width:{sz}px;height:{sz}px;display:flex;align-items:center;justify-content:center;
  background:#f0ede8;border-radius:{int(12*sc)}px}}
.card{{background:#fff;padding:{pad}px {pad}px {bot}px;box-shadow:0 4px 20px rgba(0,0,0,.12);
  transform:rotate(-2deg);border-radius:{int(4*sc)}px}}
.card img{{width:{int(sz*0.7)}px;height:{int(sz*0.55)}px;object-fit:cover;display:block}}
.txt{{padding-top:{int(14*sc)}px;text-align:center}}
.name{{color:#333;font-size:{int(S["name"]*0.7*sc)}px;font-weight:900;margin-bottom:{int(4*sc)}px}}
.sub{{color:#999;font-size:{int(S["sub"]*sc)}px}}
</style></head><body>
<div class="wrap"><div class="card"><img src="{url}"/>
<div class="txt"><div class="name">{name}</div>
<div class="sub">{(loc + ' · ' if loc else '')}{sub or ''}</div></div>
</div></div></body></html>"""


# ===== 9. 네온 =====
def _neon(url, name, loc, sub, accent, tc, sz, sc, fid, fname, S, rot=0):
    ac = accent
    tag = f'<div class="tag">{loc}</div>' if loc else ""
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, rot) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover;filter:brightness(0.4) contrast(1.1)}}
.txt{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;width:85%}}
.tag{{display:inline-block;border:2px solid {ac};color:{ac};padding:{int(5*sc)}px {int(18*sc)}px;
  border-radius:{int(20*sc)}px;font-size:{int(S["tag"]*sc)}px;font-weight:700;
  margin-bottom:{int(16*sc)}px;letter-spacing:2px;
  text-shadow:0 0 10px {ac},0 0 30px {ac}50}}
.name{{color:{tc};font-size:{int(S["name"]*sc)}px;font-weight:900;line-height:1.15;
  text-shadow:0 0 20px {ac}80,0 0 60px {ac}40;margin-bottom:{int(10*sc)}px}}
.sub{{color:{tc}cc;font-size:{int(S["sub"]*sc)}px;text-shadow:0 0 10px {ac}40}}
</style></head><body>
<div class="card"><img src="{url}"/>
<div class="txt">{tag}<div class="name">{name}</div>{sub_h}</div>
</div></body></html>"""


# ===== 10. 타이포 =====
def _typo(url, name, loc, sub, accent, tc, sz, sc, fid, fname, S, rot=0):
    ac = accent
    tag = f'<span class="loc" style="color:{ac}">{loc}</span>' if loc else ""
    sub_h = f'<p class="sub">{sub}</p>' if sub else ""
    return _head(fid, fname, rot) + f"""
.card{{position:relative;width:{sz}px;height:{sz}px;overflow:hidden;border-radius:{int(12*sc)}px}}
.card img{{width:100%;height:100%;object-fit:cover}}
.grad{{position:absolute;inset:0;background:rgba(0,0,0,.55)}}
.txt{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:{int(40*sc)}px}}
.loc{{font-size:{int(S["tag"]*sc)}px;font-weight:700;letter-spacing:4px;margin-bottom:{int(20*sc)}px}}
.name{{color:{tc};font-size:{int(S["name"]*1.3*sc)}px;font-weight:900;line-height:1.05;
  text-align:center;letter-spacing:-2px;text-shadow:0 4px 20px rgba(0,0,0,.4)}}
.line{{width:{int(60*sc)}px;height:3px;background:{ac};margin:{int(20*sc)}px auto}}
.sub{{color:{tc}cc;font-size:{int(S["sub"]*sc)}px;text-align:center;letter-spacing:1px}}
</style></head><body>
<div class="card"><img src="{url}"/><div class="grad"></div>
<div class="txt">{tag}<div class="name">{name}</div><div class="line"></div>{sub_h}</div>
</div></body></html>"""


def build_html(url, name, loc, sub, accent, tc, tpl, fid, fname, S, rot=0, size=540):
    sc = size / 540
    funcs = {
        "modern": _modern, "center": _center, "minimal": _minimal,
        "magazine": _magazine, "frame": _framed, "split": _split,
        "cinematic": _cinematic, "polaroid": _polaroid, "neon": _neon, "typo": _typo,
    }
    return funcs[tpl](url, name, loc, sub, accent, tc, size, sc, fid, fname, S, rot)


def _pil_render(pil_img, name, loc, sub, accent, tc, tpl, S):
    """PIL로 썸네일 PNG 생성 - 템플릿별 대응"""
    import os, glob, urllib.request
    from PIL import ImageDraw, ImageFont, ImageFilter

    W, H = 1080, 1080

    # 중앙 크롭
    iw, ih = pil_img.size
    ratio = max(W / iw, H / ih)
    pil_img = pil_img.resize((int(iw * ratio), int(ih * ratio)), Image.LANCZOS)
    nw, nh = pil_img.size
    left, top = (nw - W) // 2, (nh - H) // 2
    canvas = pil_img.crop((left, top, left + W, top + H)).convert("RGBA")

    # 폰트
    font_paths = [
        "C:/Windows/Fonts/malgunbd.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        os.path.join(os.getcwd(), "fonts", "NotoSansKR-Bold.ttf"),
    ]
    font_paths += glob.glob("/usr/share/fonts/**/Noto*CJK*", recursive=True)
    fp = None
    for p in font_paths:
        if os.path.exists(p):
            fp = p
            break
    if not fp:
        import tempfile
        fp = os.path.join(tempfile.gettempdir(), "NotoSansKR-Bold.ttf")
        if not os.path.exists(fp):
            urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR-Bold.ttf", fp)

    def font(size):
        try: return ImageFont.truetype(fp, size)
        except: return ImageFont.load_default()

    nf = font(S["name"] * 2)
    sf = font(S["sub"] * 2)
    tf = font(S["tag"] * 2)

    def hex_to_rgba(h, a=255):
        h = h.lstrip("#")
        if len(h) == 3: h = h[0]*2+h[1]*2+h[2]*2
        return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), a)

    tc_rgb = hex_to_rgba(tc)
    ac_rgb = hex_to_rgba(accent)
    is_w = accent.upper() in ("#FFFFFF","#FFF")

    if tpl in ("modern", "magazine", "cinematic"):
        # 하단 그라데이션
        ov = Image.new("RGBA", (W, H), (0,0,0,0))
        od = ImageDraw.Draw(ov)
        for y in range(H//3, H):
            a = int(230*((y-H//3)/(H-H//3))**1.2)
            od.line([(0,y),(W,y)], fill=(0,0,0,min(a,230)))
        canvas = Image.alpha_composite(canvas, ov)
    elif tpl in ("center", "frame", "neon", "typo"):
        # 전체 어둡게
        ov = Image.new("RGBA", (W,H), (0,0,0,120 if tpl!="neon" else 160))
        canvas = Image.alpha_composite(canvas, ov)
    elif tpl == "minimal":
        pass  # 하단 바로 처리
    elif tpl == "split":
        pass  # 하단 흰 영역
    elif tpl == "polaroid":
        bg = Image.new("RGBA",(W,H),(240,237,232,255))
        pad, bot_pad = 48, 160
        img_w, img_h = W-pad*2-80, int((W-pad*2-80)*0.78)
        inner = canvas.resize((img_w, img_h), Image.LANCZOS)
        card_w, card_h = img_w+pad*2, img_h+pad+bot_pad
        cx, cy = (W-card_w)//2, (H-card_h)//2
        bg.paste(Image.new("RGBA",(card_w,card_h),(255,255,255,255)), (cx,cy))
        bg.paste(inner, (cx+pad, cy+pad))
        canvas = bg

    draw = ImageDraw.Draw(canvas)
    ml = 80

    if tpl == "modern":
        bottom = H - 100
        # 꺾쇠
        if loc:
            tb = draw.textbbox((0,0),loc,font=tf)
            tw,th = tb[2]-tb[0], tb[3]-tb[1]
            tag_y = bottom - S["name"]*2 - (S["sub"]*2+40 if sub else 10) - th - 50
            draw.rounded_rectangle([ml,tag_y,ml+tw+48,tag_y+th+28], radius=10, fill=ac_rgb)
            draw.text((ml+24, tag_y+14), loc, fill=(34,34,34,255) if is_w else (255,255,255,255), font=tf)
            bx,by = ml-20, tag_y-25
            draw.line([(bx,by+50),(bx,by)], fill=(*tc_rgb[:3],120), width=4)
            draw.line([(bx,by),(bx+50,by)], fill=(*tc_rgb[:3],120), width=4)
        if sub:
            draw.text((ml, bottom-S["name"]*2-S["sub"]*2-20), sub, fill=(*tc_rgb[:3],200), font=sf)
        draw.text((ml+3, bottom-S["name"]*2+3), name, fill=(0,0,0,160), font=nf)
        draw.text((ml, bottom-S["name"]*2), name, fill=tc_rgb, font=nf)

    elif tpl == "center":
        nb = draw.textbbox((0,0),name,font=nf)
        nw2 = nb[2]-nb[0]
        ny = (H - S["name"]*2)//2
        draw.text(((W-nw2)//2, ny), name, fill=tc_rgb, font=nf)
        if sub:
            sb2 = draw.textbbox((0,0),sub,font=sf)
            draw.text(((W-(sb2[2]-sb2[0]))//2, ny+S["name"]*2+20), sub, fill=(*tc_rgb[:3],200), font=sf)
        if loc:
            tb2 = draw.textbbox((0,0),loc,font=tf)
            tw2 = tb2[2]-tb2[0]
            th2 = tb2[3]-tb2[1]
            tx = (W-tw2-48)//2
            draw.rounded_rectangle([tx, ny-th2-50, tx+tw2+48, ny-22], radius=20, outline=(*ac_rgb[:3],200), width=3)
            draw.text((tx+24, ny-th2-36), loc, fill=tc_rgb, font=tf)
        # 상하 라인
        lw = 50
        draw.rounded_rectangle([(W-lw)//2, ny-80, (W+lw)//2, ny-77], radius=2, fill=ac_rgb)
        draw.rounded_rectangle([(W-lw)//2, ny+S["name"]*2+(60 if sub else 30), (W+lw)//2, ny+S["name"]*2+(63 if sub else 33)], radius=2, fill=ac_rgb)

    elif tpl == "minimal":
        bar_h = 140
        bar = Image.new("RGBA",(W,bar_h),(0,0,0,210))
        canvas.paste(bar, (0, H-bar_h), bar)
        draw = ImageDraw.Draw(canvas)
        draw.line([(0,H-bar_h),(W,H-bar_h)], fill=ac_rgb, width=3)
        draw.text((60, H-bar_h+30), name, fill=tc_rgb, font=nf)
        meta_y = H-bar_h+30+S["name"]*2+10
        if loc:
            draw.text((60, meta_y), loc, fill=ac_rgb, font=tf)
        if loc and sub:
            lw2 = draw.textbbox((0,0),loc,font=tf)[2]-draw.textbbox((0,0),loc,font=tf)[0]
            draw.text((60+lw2+15, meta_y), "·", fill=(255,255,255,80), font=tf)
            draw.text((60+lw2+30, meta_y), sub, fill=(*tc_rgb[:3],180), font=sf)
        elif sub:
            draw.text((60, meta_y), sub, fill=(*tc_rgb[:3],180), font=sf)

    elif tpl == "split":
        # 하단 흰 영역
        bar_h = 180
        canvas_rgb = canvas.convert("RGB")
        white = Image.new("RGB",(W,bar_h),(255,255,255))
        canvas_rgb.paste(white, (0,H-bar_h))
        draw2 = ImageDraw.Draw(canvas_rgb)
        draw2.line([(0,H-bar_h),(W,H-bar_h)], fill=ac_rgb[:3], width=4)
        draw2.text((60, H-bar_h+30), name, fill=(26,26,26), font=nf)
        meta_y = H-bar_h+30+S["name"]*2+10
        if loc:
            draw2.text((60, meta_y), f"📍 {loc}", fill=ac_rgb[:3], font=tf)
        if loc and sub:
            lw3 = draw2.textbbox((0,0),f"📍 {loc}",font=tf)[2]
            draw2.text((lw3+80, meta_y), sub, fill=(102,102,102), font=sf)
        elif sub:
            draw2.text((60, meta_y), sub, fill=(102,102,102), font=sf)
        return canvas_rgb

    else:
        # 나머지 템플릿: 기본 모던 스타일로 대체
        bottom = H - 100
        if loc:
            tb = draw.textbbox((0,0),loc,font=tf)
            tw,th = tb[2]-tb[0], tb[3]-tb[1]
            tag_y = bottom - S["name"]*2 - (S["sub"]*2+40 if sub else 10) - th - 50
            draw.rounded_rectangle([ml,tag_y,ml+tw+48,tag_y+th+28], radius=10, fill=ac_rgb)
            draw.text((ml+24, tag_y+14), loc, fill=(34,34,34,255) if is_w else (255,255,255,255), font=tf)
        if sub:
            draw.text((ml, bottom-S["name"]*2-S["sub"]*2-20), sub, fill=(*tc_rgb[:3],200), font=sf)
        draw.text((ml+3, bottom-S["name"]*2+3), name, fill=(0,0,0,160), font=nf)
        draw.text((ml, bottom-S["name"]*2), name, fill=tc_rgb, font=nf)

    return canvas.convert("RGB")


if uploaded_file and store_name:
    uploaded_file.seek(0)
    pil_img = Image.open(uploaded_file).convert("RGB")
    if img_rotation:
        pil_img = pil_img.rotate(img_rotation, expand=True, resample=Image.LANCZOS)
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=90)
    img_data = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
    img_url = f"data:image/jpeg;base64,{img_data}"

    st.divider()
    st.subheader("미리보기")

    preview = build_html(img_url, store_name, store_location, subtitle, accent, text_c, template, font_id, font_css, sizes, 0, 540)
    components.html(preview, height=560, scrolling=False)

    safe_name = store_name.replace('"', '').replace("'", "")
    st.caption(f"선택된 템플릿: {template_name} ({template})")
    thumb = _pil_render(pil_img.copy(), store_name, store_location, subtitle, accent, text_c, template, sizes)
    dl_buf = io.BytesIO()
    thumb.save(dl_buf, format="PNG")

    st.download_button(
        label="📥 썸네일 다운로드 (PNG)",
        data=dl_buf.getvalue(),
        file_name=f"{safe_name}_썸네일.png",
        mime="image/png",
        use_container_width=True,
    )
