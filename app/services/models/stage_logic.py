# app/services/models/stage_logic.py
# 스테이지별 분석 로직 (Ekman's 6 Basic Emotions 기반)

from .gpt_analyzer import gpt_analyzer
import logging

logger = logging.getLogger(__name__)

# Paul Ekman의 6가지 기본 감정
EKMAN_EMOTIONS = ["anger", "disgust", "fear", "happiness", "sadness", "surprise"]

def analyze_stage(stage, position_dict, size_dict, description, detected_objects=None):
    """
    스테이지별 분석 로직 (GPT 연동 포함)
    """
    try:
        # GPT 분석 수행
        gpt_result = gpt_analyzer.analyze_drawing(
            stage=stage,
            detected_objects=detected_objects or [],
            description=description,
            position_dict=position_dict,
            size_dict=size_dict
        )
        
        # 기본 분석 결과에 GPT 결과 통합
        result = {
            "stage": stage,
            "position_analysis": position_dict,
            "size_analysis": size_dict,
            "description": description,
            "detected_objects": detected_objects or [],
            "gpt_analysis": gpt_result,
            "interpretation": gpt_result.get("interpretation", f"스테이지 {stage} 분석 완료"),
            "emotion": gpt_result.get("emotion", "happiness"),  # Ekman's 6 emotions
            "emotion_confidence": gpt_result.get("emotion_confidence", 0.5)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Stage analysis error: {e}")
        # GPT 분석 실패 시 기본 분석 결과 반환
        return {
            "stage": stage,
            "position_analysis": position_dict,
            "size_analysis": size_dict,
            "description": description,
            "detected_objects": detected_objects or [],
            "interpretation": f"스테이지 {stage} 기본 분석 완료",
            "emotion": "happiness",  # 기본값은 happiness
            "emotion_confidence": 0.3,
            "error": f"고급 분석 중 오류 발생: {str(e)}"
        }

def analyze_quest_stage(object_check=True, emotion="happiness"):
    """
    퀘스트 스테이지 조건 평가 (Ekman's 6 Basic Emotions 기반)
    """
    # Ekman의 6가지 기본 감정 중 하나인지 확인
    is_valid_emotion = emotion in EKMAN_EMOTIONS
    is_valid = object_check and is_valid_emotion
    
    return {
        "is_valid": is_valid,
        "object_check": object_check,
        "emotion": emotion,
        "valid_emotions": EKMAN_EMOTIONS
    }
