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

## 데이터베이스 / 인증

로그인/회원가입은 EC2(13.61.144.167)의 `kudal-postgres` 컨테이너 안 **`ytsearch` DB**를 사용함
(자세한 셋업은 `db/README.md`). 앱은 `.env`의 `DATABASE_URL`로 접속하며, `db.py`가 커넥션을
제공. 비밀번호는 werkzeug 해시로 저장하고 로그인 상태는 Flask 세션 쿠키로 관리. 스키마 변경은
`db/schema.sql`에 반영한 뒤 서버 컨테이너에 적용할 것.

## 배포 워크플로 (기능 단위 완료 시 필수)

**기능 하나를 완성할 때마다** 아래를 수행한다. 서버는 이 리포를 pull 기반으로 배포함.

1. 로컬에서 기능 단위 작업 완료 → 스모크 테스트
2. `git add -A && git commit && git push origin main`
3. 서버에서 pull 후 Docker 재빌드/재시작:
   ```bash
   ssh -i giahn.pem ec2-user@13.61.144.167 'cd ~/new && git pull && sudo docker compose up -d --build'
   ```

배포 구조: 서버의 `~/new`가 이 리포의 클론. `docker-compose.yml`이 `Dockerfile`로 이미지를 빌드해
`ytsearch-web` 컨테이너(외부 8000 → 내부 gunicorn 5000)로 띄우며, 기존 `kudal_kudal-net`
네트워크에 붙어 `kudal-postgres:5432`로 DB에 접근함. 서버의 `.env`는 리포에 없으므로(gitignore)
최초 1회 수동 생성해야 하고, 그 `DATABASE_URL` 호스트는 `13.61.144.167`이 아니라 컨테이너명
**`kudal-postgres`** 여야 함(같은 도커 네트워크 기준).

## 아키텍처

검색은 YouTube Data API를 **사용하지 않음**. `app.py`의 `/api/search`가 브라우저처럼 위장한 User-Agent로 `https://www.youtube.com/results?search_query=...` 를 요청한 뒤:

1. `extract_yt_initial_data()` — 페이지 HTML에 박혀 있는 `ytInitialData` JSON 덩어리를 정규식으로 추출.
2. `parse_videos()` — `contents → twoColumnSearchResultsRenderer → ... → itemSectionRenderer` 중첩 트리를 순회하며 `videoRenderer` 항목을 평탄한 dict(title, channel, thumbnail, length, views, published, url)로 뽑아냄.

프론트엔드(`static/script.js`)는 `fetch`로 `/api/search?q=...` 를 호출해 결과 카드를 클라이언트 측에서 렌더링함. `templates/index.html`이 유일한 페이지.

**핵심 취약점:** YouTube 페이지 구조에 의존함. 파싱 결과가 0개거나 502가 나오면, `extract_yt_initial_data()`의 정규식이나 `parse_videos()`의 키 경로가 깨진 것 — 요청 실패라고 단정하지 말고 원본 HTML/JSON 구조부터 확인할 것.
