# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

YouTube 검색 웹사이트. Flask 백엔드 + 순수 HTML/CSS/JS 프론트엔드로 구성됨. **API 키도 로그인도 필요 없음** — YouTube 공개 검색 결과 페이지를 스크래핑해서 동작함.

## 명령어

```powershell
python -m pip install -r requirements.txt   # 의존성 설치
python app.py                               # 개발 서버 실행 (http://localhost:5000)
```

테스트 스위트나 린터는 설정되어 있지 않음. 브라우저 없이 라우트를 스모크 테스트하려면 Flask 테스트 클라이언트 사용:

```powershell
python -c "import app; c=app.app.test_client(); print(c.get('/api/search?q=lofi').get_json())"
```

주의: Windows 콘솔(cp949)은 영상 제목의 이모지/한글을 출력하지 못함 — 결과를 출력할 때 stdout을 UTF-8로 재설정할 것 (`sys.stdout.reconfigure(encoding='utf-8')`).

## 아키텍처

검색은 YouTube Data API를 **사용하지 않음**. `app.py`의 `/api/search`가 브라우저처럼 위장한 User-Agent로 `https://www.youtube.com/results?search_query=...` 를 요청한 뒤:

1. `extract_yt_initial_data()` — 페이지 HTML에 박혀 있는 `ytInitialData` JSON 덩어리를 정규식으로 추출.
2. `parse_videos()` — `contents → twoColumnSearchResultsRenderer → ... → itemSectionRenderer` 중첩 트리를 순회하며 `videoRenderer` 항목을 평탄한 dict(title, channel, thumbnail, length, views, published, url)로 뽑아냄.

프론트엔드(`static/script.js`)는 `fetch`로 `/api/search?q=...` 를 호출해 결과 카드를 클라이언트 측에서 렌더링함. `templates/index.html`이 유일한 페이지.

**핵심 취약점:** YouTube 페이지 구조에 의존함. 파싱 결과가 0개거나 502가 나오면, `extract_yt_initial_data()`의 정규식이나 `parse_videos()`의 키 경로가 깨진 것 — 요청 실패라고 단정하지 말고 원본 HTML/JSON 구조부터 확인할 것.
