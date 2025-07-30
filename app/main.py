# main.py
from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.analyze_router import router as analyze_router

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI()

# 분석 라우터 등록 (엔드포인트: /analyze)
app.include_router(analyze_router, prefix="/analyze")

# FastAPI app entrypoint