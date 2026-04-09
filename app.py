import streamlit as st

st.set_page_config(page_title="맛집 블로그 글쓰기 AI", page_icon="✍️", layout="wide")

from auth import check_password
if not check_password():
    st.stop()

pg = st.navigation([
    st.Page("1_맛집_블로그_글쓰기_AI.py", title="맛집 블로그 글쓰기 AI", icon="✍️", default=True),
    st.Page("pages/2_썸네일_만들기.py", title="썸네일 만들기", icon="🖼️"),
    st.Page("pages/3_사진_자르기.py", title="사진 자르기", icon="✂️"),
    st.Page("pages/4_사진_콜라주.py", title="사진 콜라주", icon="🖼️"),
    st.Page("pages/5_워터마크.py", title="워터마크", icon="💧"),
    st.Page("pages/6_해시태그.py", title="해시태그", icon="#️⃣"),
    st.Page("pages/7_사진_보정.py", title="사진 보정", icon="🎨"),
    st.Page("pages/8_메뉴판_번역.py", title="메뉴판 번역", icon="🌐"),
    st.Page("pages/9_별점_카드.py", title="별점 카드", icon="⭐"),
    st.Page("pages/10_인스타_캡션.py", title="인스타 캡션", icon="📱"),
    st.Page("pages/11_지도_링크.py", title="지도 링크", icon="📍"),
    st.Page("pages/12_글_히스토리.py", title="글 히스토리", icon="📚"),
    st.Page("pages/14_캐러셀_만들기.py", title="캐러셀 만들기", icon="📱"),
])
pg.run()
