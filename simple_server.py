# simple_server.py - 개선된 분석 시스템 테스트용
import sys
import os
from pathlib import Path

# 백엔드 디렉토리를 Python path에 추가
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 MemoryGarden Drawing Analysis API 서버 시작...")
    print("📋 기능:")
    print("   ✅ 신뢰도 기반 분기 분석")
    print("   ✅ HTP/PITR Interpreter 통합")
    print("   ✅ YOLO 객체 탐지")
    print("   ✅ GPT Vision 분석")
    print("🌐 서버 주소: http://localhost:8000")
    print("� API 문서: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
