import io
import streamlit as st
from PIL import Image


st.markdown("""
<style>
    .stMainBlockContainer { max-width: 720px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("🖼️ 사진 콜라주")
st.caption("여러 장의 사진을 한 장으로 합쳐줍니다")

LAYOUTS = {
    "2장 가로": {"grid": (2, 1), "min": 2},
    "2장 세로": {"grid": (1, 2), "min": 2},
    "3장 가로": {"grid": (3, 1), "min": 3},
    "4장 그리드 (2x2)": {"grid": (2, 2), "min": 4},
    "6장 그리드 (3x2)": {"grid": (3, 2), "min": 6},
    "9장 그리드 (3x3)": {"grid": (3, 3), "min": 9},
}

SIZE_OPTIONS = {
    "인스타 정사각형 (1080x1080)": (1080, 1080),
    "인스타 세로 (1080x1350)": (1080, 1350),
    "블로그 가로 (1280x720)": (1280, 720),
}

col1, col2 = st.columns(2)
with col1:
    layout_name = st.selectbox("레이아웃", list(LAYOUTS.keys()))
with col2:
    size_name = st.selectbox("출력 사이즈", list(SIZE_OPTIONS.keys()))

gap = st.slider("사진 간격 (px)", 0, 20, 4, 2)
bg_color = st.color_picker("배경색", "#ffffff")

layout = LAYOUTS[layout_name]
out_size = SIZE_OPTIONS[size_name]

uploaded_files = st.file_uploader(
    f"사진 업로드 (최소 {layout['min']}장)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)


def make_collage(images, grid, out_size, gap, bg):
    cols, rows = grid
    total_w, total_h = out_size
    gap_total_w = gap * (cols - 1)
    gap_total_h = gap * (rows - 1)
    cell_w = (total_w - gap_total_w) // cols
    cell_h = (total_h - gap_total_h) // rows

    canvas = Image.new("RGB", (total_w, total_h), bg)

    for idx in range(cols * rows):
        if idx >= len(images):
            break
        img = images[idx]
        # 중앙 크롭
        iw, ih = img.size
        target_ratio = cell_w / cell_h
        current_ratio = iw / ih
        if current_ratio > target_ratio:
            new_w = int(ih * target_ratio)
            left = (iw - new_w) // 2
            img = img.crop((left, 0, left + new_w, ih))
        else:
            new_h = int(iw / target_ratio)
            top = (ih - new_h) // 2
            img = img.crop((0, top, iw, top + new_h))

        img = img.resize((cell_w, cell_h), Image.LANCZOS)

        col_idx = idx % cols
        row_idx = idx // cols
        x = col_idx * (cell_w + gap)
        y = row_idx * (cell_h + gap)
        canvas.paste(img, (x, y))

    return canvas


if uploaded_files:
    if len(uploaded_files) < layout["min"]:
        st.warning(f"선택한 레이아웃은 최소 {layout['min']}장이 필요합니다. (현재 {len(uploaded_files)}장)")
    else:
        images = []
        for f in uploaded_files[:layout["min"]]:
            f.seek(0)
            images.append(Image.open(f).convert("RGB"))

        collage = make_collage(images, layout["grid"], out_size, gap, bg_color)

        st.divider()
        st.subheader("결과")
        st.image(collage, use_container_width=True)

        buf = io.BytesIO()
        collage.save(buf, format="JPEG", quality=95)
        st.download_button(
            label="📥 콜라주 다운로드",
            data=buf.getvalue(),
            file_name="collage.jpg",
            mime="image/jpeg",
            use_container_width=True,
        )
