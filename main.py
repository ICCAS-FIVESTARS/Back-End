from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from database import get_db, create_tables
from models import User, GameResult

app = FastAPI()

# 테이블 자동 생성
create_tables()

# 회원가입 요청 데이터 형식
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

# 게임 클리어 결과 요청 데이터 형식
class GameClearData(BaseModel):
    username: str
    clear_time: float

@app.get("/")
def read_root():
    return {"message": "오성 memory garden 서버 작동 중!"}

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")
    
    new_user = User(username=user.username, password=user.password, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"{new_user.username}님, 가입이 완료되었습니다!"}

@app.post("/game/clear")
def save_game_clear(data: GameClearData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    new_result = GameResult(user_id=user.id, clear_time=data.clear_time)
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return {
        "message": f"{data.username}님의 게임 결과가 저장되었습니다!",
        "clear_time": data.clear_time
    }
