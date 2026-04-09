import base64
import streamlit as st
import streamlit.components.v1 as components


st.markdown('<style>.stMainBlockContainer{max-width:720px;margin:0 auto}</style>', unsafe_allow_html=True)

st.title("⭐ 별점 카드")
st.caption("맛/서비스/분위기/가성비 별점을 입력하면 예쁜 평가 카드를 만들어줍니다")

THEMES = {
    "다크": {"bg": "#1a1a2e", "card": "#16213e", "accent": "#e94560", "text": "#fff"},
    "라이트": {"bg": "#f8f9fa", "card": "#ffffff", "accent": "#ff6b35", "text": "#222"},
    "네이비": {"bg": "#0a1628", "card": "#1a2744", "accent": "#ffd700", "text": "#fff"},
    "민트": {"bg": "#e8f5e9", "card": "#ffffff", "accent": "#10b981", "text": "#222"},
}

store_name = st.text_input("가게 이름", placeholder="예: 광장족발")
one_line = st.text_input("한줄평", placeholder="예: 성수동에서 족발 먹으면 여기!")

col1, col2 = st.columns(2)
with col1:
    taste = st.slider("맛", 0.0, 5.0, 4.0, 0.5)
    service = st.slider("서비스", 0.0, 5.0, 4.0, 0.5)
with col2:
    mood = st.slider("분위기", 0.0, 5.0, 4.0, 0.5)
    value = st.slider("가성비", 0.0, 5.0, 4.0, 0.5)

col3, col4 = st.columns(2)
with col3:
    theme_name = st.selectbox("테마", list(THEMES.keys()))
with col4:
    uploaded = st.file_uploader("배경 사진 (선택)", type=["jpg", "jpeg", "png", "webp"])

theme = THEMES[theme_name]
avg = round((taste + service + mood + value) / 4, 1)


def stars_html(score, accent):
    full = int(score)
    half = 1 if score - full >= 0.5 else 0
    empty = 5 - full - half
    s = f'<span style="color:{accent}">' + "★" * full
    if half:
        s += "★"
    s += "</span>"
    s += f'<span style="color:rgba(255,255,255,0.2)">{"★" * empty}</span>'
    return s


def build_card(sz=480):
    bg_img = ""
    if uploaded:
        uploaded.seek(0)
        data = base64.standard_b64encode(uploaded.read()).decode("utf-8")
        bg_img = f"background-image:linear-gradient(rgba(0,0,0,0.7),rgba(0,0,0,0.7)),url(data:{uploaded.type};base64,{data});background-size:cover;background-position:center;"
        text_c = "#fff"
        card_bg = "rgba(0,0,0,0.5);backdrop-filter:blur(8px)"
    else:
        bg_img = f"background:{theme['bg']};"
        text_c = theme["text"]
        card_bg = theme["card"]

    ac = theme["accent"]

    rows = ""
    for label, score in [("맛", taste), ("서비스", service), ("분위기", mood), ("가성비", value)]:
        rows += f"""<div class="row">
            <span class="label">{label}</span>
            <span class="stars">{stars_html(score, ac)}</span>
            <span class="score">{score}</span>
        </div>"""

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans KR',sans-serif}}
.wrap{{{bg_img}width:{sz}px;height:{sz}px;display:flex;align-items:center;justify-content:center;
  border-radius:16px;overflow:hidden}}
.card{{background:{card_bg};border-radius:12px;padding:36px;width:85%;color:{text_c}}}
.title{{font-size:28px;font-weight:900;margin-bottom:4px}}
.oneline{{font-size:13px;opacity:0.7;margin-bottom:20px}}
.row{{display:flex;align-items:center;margin-bottom:12px}}
.label{{width:60px;font-size:14px;font-weight:700}}
.stars{{flex:1;font-size:18px;letter-spacing:2px}}
.score{{font-size:14px;font-weight:700;width:30px;text-align:right}}
.avg-wrap{{margin-top:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.15);
  display:flex;align-items:center;justify-content:space-between}}
.avg-label{{font-size:14px;font-weight:700}}
.avg-score{{font-size:36px;font-weight:900;color:{ac}}}
</style></head><body>
<div class="wrap"><div class="card">
<div class="title">{store_name or "가게 이름"}</div>
<div class="oneline">{one_line or ""}</div>
{rows}
<div class="avg-wrap"><span class="avg-label">총점</span><span class="avg-score">{avg}</span></div>
</div></div></body></html>"""


if store_name:
    st.divider()
    st.subheader("미리보기")
    components.html(build_card(480), height=500, scrolling=False)

    download = build_card(1080)
    st.download_button("📥 카드 다운로드 (HTML → 스크린샷)", download,
                       f"{store_name}_별점카드.html", "text/html", use_container_width=True)
