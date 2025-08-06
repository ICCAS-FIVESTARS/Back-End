# config.py
# app/core/config.py

import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# 프로젝트 루트 경로 (Back-End 폴더)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 모델(.pt) 경로
WEIGHTS_DIR = BASE_DIR / "assets" / "weights"

# YOLO 모델 경로 (튜토리얼 전용)
YOLO_MODELS = {
    "htp": WEIGHTS_DIR / "htp.pt",       # HTP 분석
    "pitr": WEIGHTS_DIR / "pitr_yolov8.pt",     # Person-in-the-Rain 분석 (파일명 수정)
}

# 튜토리얼 분석에서 필수로 포함되어야 할 객체 이름
# names: ["rain", "umbrella", "person", "lightning", "cloud", "puddle"] # class names
TUTORIAL_REQUIRED_OBJECTS = {
    "htp": ["사람전체", "집전체", "나무전체"],
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
    11: [0, 15, 29, 3, 4], # 집, 나무, 사람, 문, 창문
    12: [0, 15, 29, 8, 12, 13, 3, 4]  # 집, 나무, 사람, 길, 꽃, 잔디, 문, 창문 (종합 단계)
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

# DAPR는 PITR의 이전 이름 (호환성 유지)
DAPR_CLASS_NAMES = PITR_CLASS_NAMES
DAPR_REQUIRED_CLASSES = PITR_REQUIRED_CLASSES

HTP_CLASS_NAMES = {
    0: "집전체",
    1: "지붕",
    2: "집벽",
    3: "문",
    4: "창문",
    5: "굴뚝",
    6: "연기",
    11: "나무",
    12: "꽃",
    13: "잔디",
    15: "나무전체",
    16: "기둥",
    19: "뿌리",
    20: "나뭇잎",
    29: "사람전체",
    30: "머리",
    31: "얼굴",
    32: "눈",
    33: "코",
    34: "입",
    35: "귀",
    36: "머리카락",
    37: "목",
    38: "상체",
    39: "팔",
    40: "손",
    41: "다리",
    42: "발"
}

HTP_REQUIRED_CLASSES = [15, 29, 0]  # 나무전체, 사람전체, 집전체

# 허용 이미지 확장자
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# API 키 (환경변수로 설정 권장)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")

# GPT 설정
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o")
GPT_MAX_TOKENS = 1000
GPT_TEMPERATURE = 0.7
