# 맛집 블로그 AI 프로젝트

## GitHub
https://github.com/yusahy99-hub/food-blog-ai.git

## 배포 URL
https://food-blog-ai-kbt23k7r6uoegfsuftwwf2.streamlit.app/

## 집 컴퓨터에서 이어서 하기

### 1. 프로젝트 클론
```bash
git clone https://github.com/yusahy99-hub/food-blog-ai.git
cd food-blog-ai
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. .env 파일 생성
```
ANTHROPIC_API_KEY=여기에_Claude_API키
GROQ_API_KEY=여기에_Groq_API키
```

### 4. 로컬 실행
```bash
streamlit run app.py
```
→ http://localhost:8501

## 프로젝트 구조
```
food-blog-ai/
├── app.py                        ← 블로그 글 생성 (Claude API)
├── pages/
│   ├── 2_썸네일_만들기.py         ← 6종 템플릿, 15종 폰트
│   ├── 3_사진_자르기.py           ← 인스타/블로그 사이즈
│   ├── 4_사진_콜라주.py           ← 여러장 → 한장
│   ├── 5_워터마크.py              ← 텍스트 워터마크
│   ├── 6_해시태그.py              ← AI 해시태그 (Groq)
│   ├── 7_사진_보정.py             ← 필터 7종 + 수동
│   ├── 8_메뉴판_번역.py           ← 다국어 번역 + 구글맵 리뷰 (Groq)
│   ├── 9_별점_카드.py             ← 맛/서비스/분위기/가성비
│   └── 10_인스타_캡션.py          ← AI 캡션 (Groq)
├── fonts/
│   └── NotoSansKR-Bold.ttf
├── packages.txt                  ← Streamlit Cloud 한글 폰트
├── requirements.txt
├── .env                          ← API 키 (git에 안 올라감)
└── .env.example
```

## API
- **블로그 글쓰기**: Claude API (Anthropic) - $5 결제함
- **해시태그/캡션/메뉴판 번역**: Groq API (무료)

## Streamlit Cloud Secrets
```
ANTHROPIC_API_KEY = "Claude키"
GROQ_API_KEY = "Groq키"
```

## 보안
- API 키 입력란은 제거됨 (Secrets/env에서만 읽음)
- Manage app 버튼은 본인만 보임
- URL 아는 사람은 앱 사용 가능하나 코드 수정은 불가
