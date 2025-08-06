# services/models/response_models.py
"""
분석 응답 데이터 모델
HTP/PITR Object Detection과 Quest GPT Vision 분석 결과를 통일된 형식으로 관리
"""

from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class AnalysisMetadata(BaseModel):
    """분석 메타데이터"""
    stage: int
    analysis_type: str  # 'object_detection' or 'gpt_vision'
    model_used: Optional[str] = None  # 'htp.pt', 'pitr_yolov8.pt', 'gpt-4o'
    processing_time: Optional[float] = None
    timestamp: datetime = datetime.now()

class ObjectDetectionResult(BaseModel):
    """Object Detection 결과 (HTP/PITR)"""
    objects_detected: List[Dict[str, Any]]
    confidence_scores: List[float]
    bounding_boxes: List[List[float]]  # [x1, y1, x2, y2] format
    total_objects: int
    model_confidence: float

class GPTVisionResult(BaseModel):
    """GPT Vision 분석 결과 (Quest)"""
    gpt_analysis: str
    psychological_insights: List[str]
    creativity_score: Optional[int] = None  # 1-10
    emotional_indicators: List[str]
    recommendations: List[str]

class AnalysisResponse(BaseModel):
    """통합 분석 응답"""
    success: bool
    message: str
    
    # 메타데이터
    metadata: AnalysisMetadata
    
    # 분석 결과 (둘 중 하나만 포함)
    object_detection: Optional[ObjectDetectionResult] = None
    gpt_vision: Optional[GPTVisionResult] = None
    
    # 공통 데이터
    stage_info: Optional[Dict[str, str]] = None
    user_input: Optional[str] = None  # 사용자 입력 텍스트
    
    # 에러 정보
    error: Optional[str] = None
    error_code: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# 빠른 응답 생성 헬퍼 함수들
def create_object_detection_response(
    stage: int,
    model_name: str,
    detection_result: ObjectDetectionResult,
    processing_time: float,
    user_input: str = None
) -> AnalysisResponse:
    """Object Detection 응답 생성"""
    return AnalysisResponse(
        success=True,
        message=f"Stage {stage} Object Detection 분석 완료",
        metadata=AnalysisMetadata(
            stage=stage,
            analysis_type="object_detection",
            model_used=model_name,
            processing_time=processing_time
        ),
        object_detection=detection_result,
        user_input=user_input
    )

def create_gpt_vision_response(
    stage: int,
    gpt_result: GPTVisionResult,
    processing_time: float,
    user_input: str = None
) -> AnalysisResponse:
    """GPT Vision 응답 생성"""
    return AnalysisResponse(
        success=True,
        message=f"Stage {stage} GPT Vision 분석 완료",
        metadata=AnalysisMetadata(
            stage=stage,
            analysis_type="gpt_vision",
            model_used="gpt-4o",
            processing_time=processing_time
        ),
        gpt_vision=gpt_result,
        user_input=user_input
    )

def create_error_response(
    stage: int,
    error_message: str,
    error_code: str = None,
    analysis_type: str = "unknown"
) -> AnalysisResponse:
    """에러 응답 생성"""
    return AnalysisResponse(
        success=False,
        message="분석 중 오류가 발생했습니다",
        metadata=AnalysisMetadata(
            stage=stage,
            analysis_type=analysis_type
        ),
        error=error_message,
        error_code=error_code
    )
