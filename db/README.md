# DB 셋업 정리

로그인/회원가입용 PostgreSQL을 EC2(13.61.144.167)에 구성한 결과 기록.

## 어디에 만들었나

서버에는 이미 다른 프로젝트(kudal)의 PostgreSQL이 Docker 컨테이너 `kudal-postgres`
(`postgres:16-alpine`)로 5432 포트에서 돌고 있었음. 새로 네이티브 PG를 설치하면 포트가
충돌하므로, **이 컨테이너 안에 이 프로젝트 전용 DB/유저만 새로 추가**했다.
(네이티브로 설치했던 postgresql16 서비스는 `disable` 처리해 둠. kudal 데이터는 손대지 않음.)

- 데이터베이스: `ytsearch`
- 앱 전용 role: `ytsearch` (슈퍼유저 아님, ytsearch DB만 소유)
- 슈퍼유저: `kudal` (kudal 프로젝트 소유, 관리용)

## 스키마

- `setup_role_db.sql` — role + database 생성 (postgres DB에 연결해 실행)
- `schema.sql` — 테이블/트리거 (ytsearch DB에 연결해 실행)

테이블:
- **users** — id, email(citext, unique, 형식검증), username, password_hash(해시만!),
  is_active, email_verified, last_login_at, created_at, updated_at(자동갱신 트리거)
- **sessions** — id(uuid), user_id(FK), token_hash, user_agent, ip_address, expires_at

## 로컬 PC에서 접속하는 법 (권장: SSH 터널)

EC2 보안그룹이 5432를 막고 있어 직접 접속은 안 됨. 포트를 인터넷에 여는 대신 SSH 터널 사용:

```powershell
ssh -i giahn.pem -N -L 5432:127.0.0.1:5432 ec2-user@13.61.144.167
```

터널을 연 채로 두면 `127.0.0.1:5432` → 컨테이너 DB로 연결됨. `.env`의 DATABASE_URL이
이 방식 기준으로 설정돼 있음.

## 재적용(마이그레이션) 방법

```powershell
scp -i giahn.pem db/schema.sql ec2-user@13.61.144.167:/tmp/
ssh -i giahn.pem ec2-user@13.61.144.167 "sudo docker cp /tmp/schema.sql kudal-postgres:/tmp/ && sudo docker exec kudal-postgres psql -U kudal -d ytsearch -f /tmp/schema.sql"
```
