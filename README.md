# YouTube 검색 웹사이트

Flask 백엔드 + HTML/CSS/JS 프론트로 만든 YouTube 검색 사이트입니다.
YouTube Data API v3를 사용합니다.

## 1. 패키지 설치

```powershell
python -m pip install -r requirements.txt
```

## 2. API 키 발급

1. https://console.cloud.google.com/ 접속
2. 새 프로젝트 생성
3. "API 및 서비스" → "라이브러리" → **YouTube Data API v3** 사용 설정
4. "사용자 인증 정보" → "API 키 만들기"

## 3. 환경변수 설정

`.env.example`을 복사해 `.env`로 만들고 키를 넣으세요.

```
YOUTUBE_API_KEY=발급받은_키
```

## 4. 실행

```powershell
python app.py
```

브라우저에서 http://localhost:5000 접속.

## 구조

```
new/
├── app.py              # Flask 백엔드 (/api/search 엔드포인트)
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html      # 검색 UI
└── static/
    ├── style.css       # 다크 테마 스타일
    └── script.js       # fetch로 검색 요청/렌더링
```
