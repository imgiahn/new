FROM python:3.12-slim

WORKDIR /app

# psycopg2-binary는 휠로 설치되므로 빌드 도구 불필요
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# 운영은 gunicorn으로 (app.py의 app 객체)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "app:app"]
