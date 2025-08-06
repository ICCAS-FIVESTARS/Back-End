from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse
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

# 로그인 요청 데이터 형식
class UserLogin(BaseModel):
    username: str
    password: str

# 게임 클리어 결과 저장 요청 데이터 형식
class GameClearData(BaseModel):
    username: str
    result_text: str
    emotion: str
    emotion_confidence: float
    stage_number: int

@app.get("/")
def read_root():
    return {"message": "오성 memory garden 서버 작동 중!"}

# 회원가입 API
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")
    
    new_user = User(username=user.username, password=user.password, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "success": True,
        "message": f"{new_user.username}님, 가입이 완료되었습니다!"
    }

# 로그인 API
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        User.username == user.username,
        User.password == user.password
    ).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다.")
    
    return {
        "success": True,
        "message": f"{user.username}님, 로그인 성공!",
        "isFirstLogin": True
    }

# 게임 결과 저장 API
@app.post("/game/clear")
def save_game_clear(data: GameClearData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    new_result = GameResult(
        user_id=user.id,
        stage_number=data.stage_number,
        result_text=data.result_text,
        emotion=data.emotion,
        emotion_confidence=data.emotion_confidence
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return {
        "success": True,
        "message": f"{data.username}님의 Stage {data.stage_number} 결과가 저장되었습니다!"
    }

# 사용자별 전체 결과 확인 API
@app.get("/game/result", response_class=PlainTextResponse)
def get_all_results(db: Session = Depends(get_db)):
    users = db.query(User).all()
    output = ""

    for user in users:
        output += f"id: {user.id}\n"
        output += f"username: {user.username}\n"
        output += f"password: {user.password}\n"

        # ✅ 최근 결과 1개 가져와서 요약 표시
        latest_result = (
            db.query(GameResult)
            .filter(GameResult.user_id == user.id)
            .order_by(GameResult.id.desc())
            .first()
        )

        output += "results:\n"
        if latest_result:
            output += f"- {latest_result.result_text}\n"
            output += f"emotion: {latest_result.emotion}\n"
            output += f"emotion_confidence: {latest_result.emotion_confidence:.2f}\n"
        else:
            output += "- (결과 없음)\n"

        # ✅ 각 스테이지별 결과 출력
        for stage_num in range(1, 13):
            stage_results = [
                r for r in user.results if r.stage_number == stage_num
            ]
            output += f"\nstage{stage_num}:\n"
            if stage_results:
                for res in stage_results:
                    output += f"- {res.result_text}\n"
                    output += f"  emotion: {res.emotion}\n"
                    output += f"  emotion_confidence: {res.emotion_confidence:.2f}\n"
            else:
                output += "- (결과 없음)\n"

        output += "\n"

    return output
