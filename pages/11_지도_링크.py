import urllib.parse
import requests
import streamlit as st


st.markdown("""
<style>
    .stMainBlockContainer { max-width: 720px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("📍 지도 링크 & QR코드")
st.caption("가게 이름을 입력하면 네이버/카카오 지도 링크와 QR코드를 생성합니다.")

store_name = st.text_input("가게 이름", placeholder="예: 을지로 골목식당")

if store_name:
    encoded_name = urllib.parse.quote(store_name)

    naver_url = f"https://map.naver.com/v5/search/{encoded_name}"
    kakao_url = f"https://map.kakao.com/?q={encoded_name}"

    st.divider()

    # --- 네이버 지도 ---
    st.subheader("🟢 네이버 지도")
    st.code(naver_url, language=None)

    naver_qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(naver_url, safe='')}"
    st.image(naver_qr_url, caption="네이버 지도 QR코드", width=300)

    naver_qr_data = requests.get(naver_qr_url).content
    st.download_button(
        label="네이버 지도 QR 다운로드",
        data=naver_qr_data,
        file_name=f"naver_qr_{store_name}.png",
        mime="image/png",
    )

    st.divider()

    # --- 카카오맵 ---
    st.subheader("🟡 카카오맵")
    st.code(kakao_url, language=None)

    kakao_qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(kakao_url, safe='')}"
    st.image(kakao_qr_url, caption="카카오맵 QR코드", width=300)

    kakao_qr_data = requests.get(kakao_qr_url).content
    st.download_button(
        label="카카오맵 QR 다운로드",
        data=kakao_qr_data,
        file_name=f"kakao_qr_{store_name}.png",
        mime="image/png",
    )
