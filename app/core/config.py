# app/core/config.py
import os
from pathlib import Path

# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ 모델 경로 (.pt 파일은 weights 폴더에 저장)
WEIGHTS_DIR = BASE_DIR / "assets" / "weights"

# YOLO 모델 경로
YOLO_MODELS = {
    "htp": WEIGHTS_DIR / "htp_yolov8.pt",
    "pitr": WEIGHTS_DIR / "pitr_yolov8.pt",  # = person in the rain
    "quest1": WEIGHTS_DIR / "cloud_quest.pt",
    "quest2": WEIGHTS_DIR / "sun_quest.pt",
    # 나머지 퀘스트 추가 가능
}

# OwlViT (멀티모달 탐지기) 모델 이름
OWL_VIT_MODEL = "google/owlv2-base-patch16-ensemble"

# 각 분석에서 필수로 포함되어야 할 객체
REQUIRED_OBJECTS = {
    "htp": ["person", "house", "tree"],
    "pitr": ["person", "rain"]
    # 다른 퀘스트는 개별 analyzer에서 따로 조건 처리
}

# 허용 이미지 확장자
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# API 키 설정 (환경변수 사용)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")
