# app/api/user_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import asyncio

router = APIRouter()

# DB 서버 URL
DB_SERVER_URL = "http://34.63.32.189:8000"

# 요청 데이터 모델
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class GameClearData(BaseModel):
    username: str
    clear_time: float

@router.post("/signup")
async def signup(user: UserCreate):
    """회원가입 API - DB 서버로 요청 전달"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DB_SERVER_URL}/signup",
                json=user.dict(),
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json() if response.content else {"detail": "Unknown error"}
                raise HTTPException(status_code=response.status_code, detail=error_data.get("detail", "회원가입 실패"))
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="DB 서버에 연결할 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.post("/login")
async def login(user: UserLogin):
    """로그인 API - DB 서버로 요청 전달"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DB_SERVER_URL}/login",
                json=user.dict(),
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json() if response.content else {"detail": "Unknown error"}
                raise HTTPException(status_code=response.status_code, detail=error_data.get("detail", "로그인 실패"))
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="DB 서버에 연결할 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.post("/game/clear")
async def save_game_clear(data: GameClearData):
    """게임 클리어 결과 저장 API - DB 서버로 요청 전달"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DB_SERVER_URL}/game/clear",
                json=data.dict(),
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json() if response.content else {"detail": "Unknown error"}
                raise HTTPException(status_code=response.status_code, detail=error_data.get("detail", "게임 결과 저장 실패"))
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="DB 서버에 연결할 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/health/db")
async def check_db_health():
    """DB 서버 연결 상태 확인"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DB_SERVER_URL}/", timeout=5.0)
            if response.status_code == 200:
                return {"status": "healthy", "db_server": "connected"}
            else:
                return {"status": "unhealthy", "db_server": "error", "code": response.status_code}
    except Exception as e:
        return {"status": "unhealthy", "db_server": "disconnected", "error": str(e)}
