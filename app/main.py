# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import sys
import os

# 현재 디렉토리를 Python path에 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .api.analyze_router import router as analyze_router
from .api.user_router import router as user_router

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="Drawing Analysis API",
    description="API for analyzing drawings using YOLOv8 and GPT",
    version="1.0.0"
)

# CORS 설정 - 모든 요청 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # credentials를 false로 설정
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 분석 라우터 등록
app.include_router(analyze_router, prefix="/api")

# 사용자 관리 라우터 등록
app.include_router(user_router, prefix="/api")

# 전역 OPTIONS 처리
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse(content={"message": "OK"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# 헬스체크 엔드포인트
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "Drawing Analysis API is running"}

# FastAPI app entrypoint