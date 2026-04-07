import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def check_password():
    """비밀번호 확인 후 True/False 반환. 세션 스테이트로 로그인 상태 유지."""
    if st.session_state.get("authenticated"):
        return True

    # .env 또는 st.secrets에서 비밀번호 읽기
    correct_password = os.environ.get("APP_PASSWORD", "")
    if not correct_password:
        try:
            correct_password = st.secrets.get("APP_PASSWORD", "")
        except Exception:
            pass
    if not correct_password:
        correct_password = "foodblog2024"

    st.markdown(
        "<style>.stMainBlockContainer{max-width:480px;margin:0 auto}</style>",
        unsafe_allow_html=True,
    )
    st.title("🔒 로그인")
    st.caption("이 앱은 비밀번호로 보호되어 있습니다.")

    password = st.text_input("비밀번호를 입력하세요", type="password")

    if st.button("로그인", type="primary", use_container_width=True):
        if password == correct_password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")

    return False
