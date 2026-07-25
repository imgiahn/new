-- postgres DB에 연결한 상태에서 실행 (kudal 슈퍼유저로).
-- 이 프로젝트 전용 role과 database를 생성한다. kudal 데이터는 건드리지 않음.

SELECT format('CREATE ROLE ytsearch LOGIN PASSWORD %L', 'DoKcWzYH973r8XoOQO3R')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ytsearch')
\gexec

SELECT 'CREATE DATABASE ytsearch OWNER ytsearch'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'ytsearch')
\gexec
