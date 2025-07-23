# app/api/analyze_router.py
# FE 수정 후 TBD 
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid

from ..services.analyzers.htp_analyzer import analyze_htp
from ..services.analyzers.pitr_analyzer import analyze_pitr
from ..services.analyzers.quest_analyzer import analyze_quest

router = APIRouter()
UPLOAD_DIR = Path("assets/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# API endpoint
@router.post("/analyze/")
async def analyze(
    stage: int = Form(...),
    image: UploadFile = File(...),
    description: str = Form(...)
):
    ext = Path(image.filename).suffix
    saved_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    with saved_path.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    try:
        # 단계별 분석 라우팅 - 요청 파라미터 
        if stage == 0:
            result = analyze_htp(str(saved_path), description)
        elif stage == 1:
            result = analyze_pitr(str(saved_path), description)
        else:
            result = analyze_quest(str(saved_path), description, stage)

        return JSONResponse(content=result)
    # 예외 처리 
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
