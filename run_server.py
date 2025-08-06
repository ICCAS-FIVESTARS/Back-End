# run_server.py - 간단한 서버 실행 스크립트
import os
import sys
from pathlib import Path

# 현재 디렉토리를 Python path에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("🚀 MemoryGarden API 서버 시작...")
print("📂 현재 경로:", current_dir)

try:
    import uvicorn
    from app.main import app
    
    print("✅ 모듈 로드 성공")
    print("🌐 서버 주소:")
    print("   - 메인: http://localhost:8000")
    print("   - API 문서: http://localhost:8000/docs") 
    print("   - 헬스체크: http://localhost:8000/api/health")
    print("🔄 서버 시작 중...")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    print("💡 해결방법:")
    print("   1. pip install fastapi uvicorn")
    print("   2. 현재 디렉토리가 Back-End인지 확인")
    
except Exception as e:
    print(f"❌ 서버 실행 오류: {e}")
