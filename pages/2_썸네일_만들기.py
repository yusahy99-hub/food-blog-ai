import io
import os
import glob
import urllib.request
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


st.markdown("""
<style>
    .stMainBlockContainer { max-width: 720px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("🖼️ 썸네일 만들기")
st.caption("사진 + 가게 정보 입력 → 미리보기 → 바로 PNG 다운로드")

# --- 프리셋 ---
COLOR_PRESETS = {
    "오렌지": "#FF6B35", "코랄": "#FF4F6F", "블루": "#3B82F6",
    "민트": "#10B981", "퍼플": "#8B5CF6", "골드": "#F59E0B",
    "화이트": "#FFFFFF", "블랙": "#1F2937",
}
TEXT_COLORS = {
    "흰색": "#FFFFFF", "검정": "#1a1a1a", "연회색": "#e0e0e0",
    "크림": "#FFF8E7", "오렌지": "#FF6B35", "코랄": "#FF4F6F", "골드": "#F59E0B",
}
TEMPLATES = {
    "모던 좌측": "modern", "센터": "center", "미니멀 바": "minimal",
    "매거진": "magazine", "프레임": "frame", "스플릿": "split",
    "시네마틱": "cinematic", "타이포": "typo",
}

# --- 폰트 로드 ---
@st.cache_resource
def load_font_path():
    # .ttf 우선 (한글 확실 지원)
    ttf_candidates = [
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        os.path.join(os.getcwd(), "fonts", "NotoSansKR-Bold.ttf"),
    ]
    for p in ttf_candidates:
        if os.path.exists(p):
            return p

    # .ttc는 인덱스 필요 - 별도 처리
    ttc_candidates = glob.glob("/usr/share/fonts/**/Noto*CJK*.ttc", recursive=True)
    if ttc_candidates:
        return ttc_candidates[0]

    # 다운로드
    import tempfile
    fp = os.path.join(tempfile.gettempdir(), "NotoSansKR-Bold.ttf")
    if not os.path.exists(fp):
        urllib.request.urlretrieve(
            "https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR-Bold.ttf", fp)
    return fp

FONT_PATH = load_font_path()

def font(size):
    try:
        if FONT_PATH.endswith(".ttc"):
            return ImageFont.truetype(FONT_PATH, size, index=0)
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def hex_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def center_crop(img, W, H):
    iw, ih = img.size
    ratio = max(W / iw, H / ih)
    img = img.resize((int(iw * ratio), int(ih * ratio)), Image.LANCZOS)
    nw, nh = img.size
    left, top = (nw - W) // 2, (nh - H) // 2
    return img.crop((left, top, left + W, top + H))

def draw_gradient(canvas, W, H, start_ratio=0.3, max_alpha=230):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    start = int(H * start_ratio)
    for y in range(start, H):
        a = int(max_alpha * ((y - start) / (H - start)) ** 1.2)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, min(a, max_alpha)))
    return Image.alpha_composite(canvas.convert("RGBA"), ov)

# --- 입력 UI ---
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
    color_name = st.selectbox("태그 색상", list(COLOR_PRESETS.keys()))

col5, col6 = st.columns(2)
with col5:
    text_color_name = st.selectbox("글씨 색상", list(TEXT_COLORS.keys()))
with col6:
    font_weight = st.selectbox("글씨 굵기", ["보통", "굵게"])

with st.expander("글자 크기 설정"):
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        name_size = st.slider("가게 이름", 20, 80, 38, 2)
    with sc2:
        sub_size = st.slider("설명 문구", 10, 40, 16, 1)
    with sc3:
        tag_size = st.slider("위치 태그", 8, 30, 13, 1)

uploaded_file = st.file_uploader("배경 사진 업로드", type=["jpg", "jpeg", "png", "webp"])

# 회전
rc1, rc2, rc3, rc4 = st.columns(4)
with rc1:
    if st.button("↩️ 왼쪽 90°"):
        st.session_state["img_rot"] = st.session_state.get("img_rot", 0) + 90
with rc2:
    if st.button("↪️ 오른쪽 90°"):
        st.session_state["img_rot"] = st.session_state.get("img_rot", 0) - 90
with rc3:
    if st.button("🔄 180°"):
        st.session_state["img_rot"] = st.session_state.get("img_rot", 0) + 180
with rc4:
    if st.button("초기화"):
        st.session_state["img_rot"] = 0

rot = st.session_state.get("img_rot", 0) % 360
tpl = TEMPLATES[template_name]
accent = hex_rgb(COLOR_PRESETS[color_name])
tc = hex_rgb(TEXT_COLORS[text_color_name])
tc_a = lambda a: (*tc, a)
ac_a = lambda a: (*accent, a)
is_white_accent = COLOR_PRESETS[color_name].upper() in ("#FFFFFF", "#FFF")
S = {"name": name_size * 2, "sub": sub_size * 2, "tag": tag_size * 2}


def render_thumbnail(pil_img):
    W, H = 1080, 1080
    img = center_crop(pil_img, W, H).convert("RGBA")

    # --- 오버레이 ---
    if tpl in ("modern", "magazine", "cinematic"):
        img = draw_gradient(img, W, H)
    elif tpl in ("center", "frame", "typo"):
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 120))
        img = Image.alpha_composite(img, ov)
    elif tpl == "neon":
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 160))
        img = Image.alpha_composite(img, ov)
    elif tpl == "polaroid":
        bg = Image.new("RGBA", (W, H), (240, 237, 232, 255))
        pad, bp = 48, 160
        iw2 = W - pad * 2 - 80
        ih2 = int(iw2 * 0.78)
        inner = center_crop(pil_img, iw2, ih2).convert("RGBA")
        cw, ch = iw2 + pad * 2, ih2 + pad + bp
        cx, cy = (W - cw) // 2, (H - ch) // 2
        bg.paste(Image.new("RGBA", (cw, ch), (255, 255, 255, 255)), (cx, cy))
        bg.paste(inner, (cx + pad, cy + pad))
        img = bg

    draw = ImageDraw.Draw(img)
    nf = font(S["name"])
    sf = font(S["sub"])
    tf = font(S["tag"])
    ml = 80

    name = store_name
    loc = store_location
    sub = subtitle

    if tpl == "modern":
        bottom = H - 100
        if loc:
            tb = draw.textbbox((0, 0), loc, font=tf)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            ty = bottom - S["name"] - (S["sub"] + 40 if sub else 10) - th - 50
            draw.rounded_rectangle([ml, ty, ml + tw + 48, ty + th + 28], radius=10, fill=(*accent, 230))
            draw.text((ml + 24, ty + 14), loc, fill=(34, 34, 34) if is_white_accent else (255, 255, 255), font=tf)
            bx, by = ml - 20, ty - 25
            draw.line([(bx, by + 50), (bx, by)], fill=tc_a(120), width=4)
            draw.line([(bx, by), (bx + 50, by)], fill=tc_a(120), width=4)
        if sub:
            draw.text((ml, bottom - S["name"] - S["sub"] - 20), sub, fill=tc_a(200), font=sf)
        draw.text((ml + 3, bottom - S["name"] + 3), name, fill=(0, 0, 0, 160), font=nf)
        draw.text((ml, bottom - S["name"]), name, fill=tc_a(255), font=nf)

    elif tpl == "center":
        nb = draw.textbbox((0, 0), name, font=nf)
        nw = nb[2] - nb[0]
        ny = (H - S["name"]) // 2
        draw.text(((W - nw) // 2, ny), name, fill=tc_a(255), font=nf)
        if sub:
            sb = draw.textbbox((0, 0), sub, font=sf)
            draw.text(((W - (sb[2] - sb[0])) // 2, ny + S["name"] + 20), sub, fill=tc_a(200), font=sf)
        if loc:
            tb = draw.textbbox((0, 0), loc, font=tf)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            tx = (W - tw - 48) // 2
            draw.rounded_rectangle([tx, ny - th - 50, tx + tw + 48, ny - 22], radius=20, outline=ac_a(200), width=3)
            draw.text((tx + 24, ny - th - 36), loc, fill=tc_a(255), font=tf)
        draw.rounded_rectangle([(W - 50) // 2, ny - 80, (W + 50) // 2, ny - 77], radius=2, fill=ac_a(255))
        draw.rounded_rectangle([(W - 50) // 2, ny + S["name"] + (60 if sub else 30), (W + 50) // 2, ny + S["name"] + (63 if sub else 33)], radius=2, fill=ac_a(255))

    elif tpl == "minimal":
        bh = 140
        bar = Image.new("RGBA", (W, bh), (0, 0, 0, 210))
        img.paste(bar, (0, H - bh), bar)
        draw = ImageDraw.Draw(img)
        draw.line([(0, H - bh), (W, H - bh)], fill=ac_a(255), width=3)
        draw.text((60, H - bh + 30), name, fill=tc_a(255), font=nf)
        my = H - bh + 30 + S["name"] + 10
        if loc:
            draw.text((60, my), loc, fill=(*accent, 255), font=tf)
            if sub:
                lw = draw.textbbox((0, 0), loc, font=tf)[2] - draw.textbbox((0, 0), loc, font=tf)[0]
                draw.text((60 + lw + 30, my), sub, fill=tc_a(180), font=sf)
        elif sub:
            draw.text((60, my), sub, fill=tc_a(180), font=sf)

    elif tpl == "magazine":
        ty = 100
        if loc:
            tb = draw.textbbox((0, 0), loc, font=tf)
            draw.rounded_rectangle([ml, ty, ml + tb[2] - tb[0] + 28, ty + S["tag"] + 16], radius=6, fill=ac_a(230))
            draw.text((ml + 14, ty + 8), loc, fill=(255, 255, 255), font=tf)
            ty += S["tag"] + 40
        draw.text((ml + 3, ty + 3), name, fill=(0, 0, 0, 100), font=nf)
        draw.text((ml, ty), name, fill=tc_a(255), font=nf)
        if sub:
            sy = ty + S["name"] + 20
            draw.line([(ml, sy), (ml, sy + S["sub"])], fill=ac_a(255), width=3)
            draw.text((ml + 16, sy), sub, fill=tc_a(200), font=sf)
        draw.line([(W - ml, H - ml - 50), (W - ml, H - ml)], fill=tc_a(90), width=3)
        draw.line([(W - ml - 50, H - ml), (W - ml, H - ml)], fill=tc_a(90), width=3)

    elif tpl == "frame":
        draw.rounded_rectangle([56, 56, W - 56, H - 56], radius=16, outline=tc_a(100), width=2)
        draw.rounded_rectangle([(W - 40) // 2, 104, (W + 40) // 2, 107], radius=2, fill=ac_a(255))
        nb = draw.textbbox((0, 0), name, font=nf)
        nw = nb[2] - nb[0]
        ny = H - 200
        draw.text(((W - nw) // 2, ny), name, fill=tc_a(255), font=nf)
        if sub:
            sb = draw.textbbox((0, 0), sub, font=sf)
            draw.text(((W - (sb[2] - sb[0])) // 2, ny + S["name"] + 16), sub, fill=tc_a(210), font=sf)
        if loc:
            tb = draw.textbbox((0, 0), loc, font=tf)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            tx = (W - tw - 48) // 2
            draw.rounded_rectangle([tx, ny - th - 40, tx + tw + 48, ny - 12], radius=20, outline=ac_a(200), width=2)
            draw.text((tx + 24, ny - th - 26), loc, fill=tc_a(255), font=tf)

    elif tpl == "split":
        bh = 180
        rgb = img.convert("RGB")
        white = Image.new("RGB", (W, bh), (255, 255, 255))
        rgb.paste(white, (0, H - bh))
        d2 = ImageDraw.Draw(rgb)
        d2.line([(0, H - bh), (W, H - bh)], fill=accent, width=4)
        d2.text((60, H - bh + 30), name, fill=(26, 26, 26), font=nf)
        my = H - bh + 30 + S["name"] + 10
        if loc:
            d2.text((60, my), f"📍 {loc}", fill=accent, font=tf)
        if loc and sub:
            lw = d2.textbbox((0, 0), f"📍 {loc}", font=tf)[2]
            d2.text((lw + 80, my), sub, fill=(102, 102, 102), font=sf)
        elif sub:
            d2.text((60, my), sub, fill=(102, 102, 102), font=sf)
        return rgb

    elif tpl == "cinematic":
        bar = int(H * 0.1)
        draw.rectangle([0, 0, W, bar], fill=(0, 0, 0, 255))
        draw.rectangle([0, H - bar, W, H], fill=(0, 0, 0, 255))
        bt = H - bar - 30
        if loc:
            draw.text((ml, bt - S["name"] - S["tag"] - 20), loc, fill=ac_a(255), font=tf)
        draw.text((ml, bt - S["name"]), name, fill=tc_a(255), font=nf)
        if sub:
            draw.text((ml, bt + 10), sub, fill=tc_a(180), font=sf)

    elif tpl == "typo":
        bf = font(int(S["name"] * 1.3))
        nb = draw.textbbox((0, 0), name, font=bf)
        nw = nb[2] - nb[0]
        ny = (H - int(S["name"] * 1.3)) // 2
        draw.text(((W - nw) // 2 + 3, ny + 3), name, fill=(0, 0, 0, 100), font=bf)
        draw.text(((W - nw) // 2, ny), name, fill=tc_a(255), font=bf)
        draw.rounded_rectangle([(W - 60) // 2, ny + int(S["name"] * 1.3) + 20, (W + 60) // 2, ny + int(S["name"] * 1.3) + 23], radius=2, fill=ac_a(255))
        if sub:
            sb = draw.textbbox((0, 0), sub, font=sf)
            draw.text(((W - (sb[2] - sb[0])) // 2, ny + int(S["name"] * 1.3) + 40), sub, fill=tc_a(200), font=sf)
        if loc:
            tb = draw.textbbox((0, 0), loc, font=tf)
            draw.text(((W - (tb[2] - tb[0])) // 2, ny - S["tag"] - 30), loc, fill=ac_a(255), font=tf)

    else:
        # 폴라로이드
        nb = draw.textbbox((0, 0), name, font=nf)
        draw.text(((W - (nb[2] - nb[0])) // 2, H - 160), name, fill=(50, 50, 50), font=nf)
        meta = (loc + " · " if loc else "") + (sub or "")
        if meta:
            sb = draw.textbbox((0, 0), meta, font=sf)
            draw.text(((W - (sb[2] - sb[0])) // 2, H - 100), meta, fill=(150, 150, 150), font=sf)

    return img.convert("RGB")


# --- 렌더링 ---
if uploaded_file and store_name:
    uploaded_file.seek(0)
    pil_img = Image.open(uploaded_file).convert("RGB")
    if rot:
        pil_img = pil_img.rotate(rot, expand=True, resample=Image.LANCZOS)

    thumb = render_thumbnail(pil_img)

    st.divider()
    st.subheader("미리보기")
    st.image(thumb, use_container_width=True)

    safe_name = store_name.replace('"', '').replace("'", "")
    dl_buf = io.BytesIO()
    thumb.save(dl_buf, format="PNG")

    st.download_button(
        label="📥 썸네일 다운로드 (PNG)",
        data=dl_buf.getvalue(),
        file_name=f"{safe_name}_썸네일.png",
        mime="image/png",
        use_container_width=True,
    )
