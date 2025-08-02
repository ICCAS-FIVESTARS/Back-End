# 🧠 Memory Garden 백엔드 서버 API 명세서

이 프로젝트는 "Memory Garden" 게임의 백엔드 서버입니다.  
FastAPI 기반으로 개발되었으며, 회원가입, 로그인, 게임 결과 저장 기능을 제공합니다.

---

## 🔧 사용 기술 (Tech Stack)

- **Python 3.10+**
- **FastAPI** – 웹 프레임워크
- **Uvicorn** – ASGI 서버 실행기
- **Pydantic** – 요청/응답 데이터 검증
- **SQLAlchemy** – ORM (DB 모델링 및 쿼리)
- **SQLite** – 로컬 데이터베이스
- **Swagger UI** – 자동 API 문서 (`/docs`)
- **Google Cloud VM** – 서버 배포 환경
- **GitHub** – 협업 및 버전 관리

---

## 🌐 Base URL

http://34.63.32.189:8000

---

## 🔹 1. 회원가입 API

- **URL**: `/signup`  
- **Method**: `POST`

### ✅ 요청 형식 (JSON)

```json
{
  "username": "example_user",
  "password": "1234",
  "email": "user@example.com"
}
🟢 성공 응답 예시
json
{
  "success": true,
  "message": "example_user님, 가입이 완료되었습니다!"
}
🔴 실패 응답 예시 (이미 존재하는 아이디)
json

{
  "detail": "이미 존재하는 사용자입니다."
}
🔹 2. 로그인 API
URL: /login

Method: POST

✅ 요청 형식 (JSON)
json

{
  "username": "example_user",
  "password": "1234"
}
🟢 성공 응답 예시
json

{
  "success": true,
  "message": "example_user님, 로그인 성공!",
  "isFirstLogin": true
}
🔴 실패 응답 예시 (아이디 또는 비밀번호 오류)
json

{
  "detail": "아이디 또는 비밀번호가 잘못되었습니다."
}
🔹 3. 게임 결과 저장 API
URL: /game/clear

Method: POST

✅ 요청 형식 (JSON)
json

{
  "username": "example_user",
  "clear_time": 123.45
}
🟢 성공 응답 예시
json

{
  "success": true,
  "message": "example_user님의 게임 결과가 저장되었습니다!",
  "clear_time": 123.45
}
🔴 실패 응답 예시 (유저 없음)
json

{
  "detail": "사용자를 찾을 수 없습니다."
}

Swagger 문서 자동 제공: http://34.63.32.189:8000/docs


