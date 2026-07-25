import json
import os
import re

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from psycopg2 import errors
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_conn

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

YOUTUBE_RESULTS_URL = "https://www.youtube.com/results"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko,en;q=0.9",
}


# ─────────────────────────── 회원가입 / 로그인 ───────────────────────────
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash("아이디와 비밀번호를 모두 입력하세요.")
        return render_template("signup.html", username=username)
    if len(password) < 4:
        flash("비밀번호는 4자 이상이어야 합니다.")
        return render_template("signup.html", username=username)

    password_hash = generate_password_hash(password)
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                (username, password_hash),
            )
            user_id = cur.fetchone()["id"]
    except errors.UniqueViolation:
        flash("이미 존재하는 아이디입니다.")
        return render_template("signup.html", username=username)

    session["user_id"] = user_id
    session["username"] = username
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,),
        )
        user = cur.fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        flash("아이디 또는 비밀번호가 올바르지 않습니다.")
        return render_template("login.html", username=username)

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE users SET last_login_at = now() WHERE id = %s", (user["id"],))

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# 검색 전에 보여줄 AI 관련 추천 키워드
RECOMMENDED_KEYWORDS = [
    "ChatGPT 활용법",
    "생성형 AI",
    "프롬프트 엔지니어링",
    "LLM 원리",
    "머신러닝 입문",
    "딥러닝 강의",
    "AI 그림 그리기",
    "스테이블 디퓨전",
    "AI 코딩 도구",
    "AI 에이전트",
    "파이썬 머신러닝",
    "AI 최신 뉴스",
]


# ─────────────────────────── YouTube 검색 ───────────────────────────
@app.route("/")
def index():
    return render_template("index.html", username=session.get("username"))


@app.route("/api/recommendations")
def recommendations():
    return jsonify({"keywords": RECOMMENDED_KEYWORDS})


@app.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "검색어를 입력해 주세요."}), 400

    try:
        resp = requests.get(
            YOUTUBE_RESULTS_URL,
            params={"search_query": query},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException:
        return jsonify({"error": "YouTube에서 결과를 가져오지 못했습니다."}), 502

    data = extract_yt_initial_data(resp.text)
    if data is None:
        return jsonify({"error": "결과 페이지를 해석하지 못했습니다."}), 502

    return jsonify({"results": parse_videos(data)})


def extract_yt_initial_data(html):
    match = re.search(r"var ytInitialData\s*=\s*(\{.*?\});</script>", html)
    if not match:
        match = re.search(r'ytInitialData"\]\s*=\s*(\{.*?\});', html)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def parse_videos(data):
    results = []
    try:
        sections = data["contents"]["twoColumnSearchResultsRenderer"][
            "primaryContents"
        ]["sectionListRenderer"]["contents"]
    except (KeyError, TypeError):
        return results

    for section in sections:
        for item in section.get("itemSectionRenderer", {}).get("contents", []):
            video = item.get("videoRenderer")
            if not video or not video.get("videoId"):
                continue
            video_id = video["videoId"]
            thumbnails = video.get("thumbnail", {}).get("thumbnails", [])
            results.append(
                {
                    "videoId": video_id,
                    "title": _get_text(video.get("title")),
                    "channel": _get_text(video.get("ownerText"))
                    or _get_text(video.get("longBylineText")),
                    "thumbnail": thumbnails[-1]["url"] if thumbnails else None,
                    "length": _get_simple(video.get("lengthText")),
                    "views": _get_simple(video.get("viewCountText")),
                    "published": _get_simple(video.get("publishedTimeText")),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )
    return results


def _get_text(node):
    if not node:
        return None
    runs = node.get("runs")
    if runs:
        return "".join(r.get("text", "") for r in runs)
    return node.get("simpleText")


def _get_simple(node):
    if not node:
        return None
    return node.get("simpleText") or _get_text(node)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
