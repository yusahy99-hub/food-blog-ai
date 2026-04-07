import streamlit as st

st.set_page_config(page_title="글 히스토리", page_icon="📚")

from auth import check_password
if not check_password():
    st.stop()

st.markdown("""
<style>
    .stMainBlockContainer { max-width: 720px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("📚 글 히스토리")
st.caption("생성한 블로그 글을 저장하고 다시 확인할 수 있습니다.")

if "blog_history" not in st.session_state:
    st.session_state.blog_history = []

history = st.session_state.blog_history

if not history:
    st.info("아직 저장된 글이 없습니다.")
else:
    st.write(f"총 **{len(history)}**개의 글이 저장되어 있습니다.")

    if st.button("🗑️ 전체 삭제", type="secondary"):
        st.session_state.blog_history = []
        st.rerun()

    st.divider()

    for idx, item in enumerate(reversed(history)):
        real_idx = len(history) - 1 - idx
        title = f"{item.get('store_name', '제목 없음')} — {item.get('created_at', '')}"

        with st.expander(title, expanded=False):
            if item.get("location"):
                st.caption(f"위치: {item['location']}")

            st.text_area(
                "복사용 텍스트",
                value=item.get("text", ""),
                height=250,
                key=f"history_text_{real_idx}",
                label_visibility="collapsed",
            )

            if st.button("삭제", key=f"delete_{real_idx}"):
                st.session_state.blog_history.pop(real_idx)
                st.rerun()
