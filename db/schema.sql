-- YouTube 검색 앱: 로그인/회원가입용 스키마
-- kudal-postgres 컨테이너 안의 별도 데이터베이스 ytsearch 에 적용됨.
-- 이 파일은 ytsearch DB에 연결된 상태에서 실행하는 걸 전제로 함.

-- 대소문자 구분 없는 이메일 저장을 위해 citext 사용
CREATE EXTENSION IF NOT EXISTS citext;

-- updated_at 자동 갱신 트리거 함수
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
  id             BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email          CITEXT       NOT NULL UNIQUE,
  username       VARCHAR(50)  UNIQUE,
  password_hash  TEXT         NOT NULL,          -- bcrypt/argon2 해시만 저장 (평문 금지)
  is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
  email_verified BOOLEAN      NOT NULL DEFAULT FALSE,
  last_login_at  TIMESTAMPTZ,
  created_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),
  CONSTRAINT email_format CHECK (email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$')
);

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 로그인 세션(토큰) 테이블 — 서버측 세션/리프레시 토큰 관리용
CREATE TABLE IF NOT EXISTS sessions (
  id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     BIGINT       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash  TEXT         NOT NULL UNIQUE,       -- 세션 토큰의 해시 저장
  user_agent  TEXT,
  ip_address  INET,
  expires_at  TIMESTAMPTZ  NOT NULL,
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
