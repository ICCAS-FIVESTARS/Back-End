# analyzers/__init__.py
"""
이미지 분석 서비스 모듈

분석 유형:
- HTP (Stage 0): Object Detection with htp.pt model
- PITR (Stage 1): Object Detection with pitr_yolov8.pt model  
- Quest (Stage 2-12): GPT-4o Vision API analysis
"""

from .htp_analyzer import analyze_htp_image
from .pitr_analyzer import analyze_pitr
from .quest_analyzer import analyze_quest

__all__ = [
    'analyze_htp_image',
    'analyze_pitr', 
    'analyze_quest'
]

# 분석기 타입 매핑
ANALYZER_MAP = {
    0: 'htp',      # HTP Object Detection
    1: 'pitr',     # PITR Object Detection
    **{i: 'quest' for i in range(2, 13)}  # Quest GPT Vision (Stage 2-12)
}

def get_analyzer_type(stage: int) -> str:
    """단계별 분석기 타입 반환"""
    return ANALYZER_MAP.get(stage, 'quest')