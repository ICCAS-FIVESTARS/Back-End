# config.py
# app/core/config.py

import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 모델(.pt) 경로
WEIGHTS_DIR = BASE_DIR / "assets" / "weights"

# YOLO 모델 경로 (튜토리얼 전용)
YOLO_MODELS = {
    "htp": WEIGHTS_DIR / "htp.pt",       # HTP 분석
    "pitr": WEIGHTS_DIR / "pitr_yolov8.pt",     # Person-in-the-Rain 분석
}

# 튜토리얼 분석에서 필수로 포함되어야 할 객체 이름
TUTORIAL_REQUIRED_OBJECTS = {
    "htp": ["person", "house", "tree"],
    "pitr": ["person", "rain"],
}

# 12단계 프로그램 각 회기별 필수 객체 클래스 ID (htp.pt 모델 기준)
STAGE_REQUIRED_CLASSES = {
    1: [29, 26],           # 사람전체, 구름
    2: [14, 26],           # 태양, 구름
    3: [15, 19, 18, 20],   # 나무, 뿌리, 가지, 잎
    4: [8, 29],            # 길, 사람
    5: [22, 15],           # 열매, 나무
    6: [29, 3, 4],         # 사람, 문, 창문
    7: [12, 13],           # 꽃, 잔디
    8: [28, 29, 26],       # 별, 사람, 구름
    9: [0, 15, 14, 26],    # 집, 나무, 태양, 구름
    10: [8, 29],           # 길, 사람
}

PITR_CLASS_NAMES = {
    0: "rain",
    1: "umbrella",
    2: "person",
    3: "lightning",
    4: "cloud",
    5: "pool"
}
PITR_REQUIRED_CLASSES = [0, 2]  # rain, person
# 허용 이미지 확장자
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# API 키 (환경변수로 설정 권장)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")
