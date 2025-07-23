# app/services/analyzers/quest_analyzer.py

from ..models.owlvit_detector import detect_objects
from ..models.sentiment_kobert import analyze_sentiment
from ..models.image_check import check_required_objects
from ..models.stage_logic import analyze_quest_stage

def analyze_quest(image_path: str, description: str, stage: int) -> dict:
    labels = detect_objects(image_path)
    
    # 필수 포함 객체 매핑 
    required_objs = {
        2: ["sun", "cloud"],
        3: ["tree"],
        4: ["house"],
        # ... 미션에 따라 추가 예정 
    }
    required = required_objs.get(stage, []) # 조건 미정인 객체 - 무조건 통과 

    object_check = check_required_objects("quest", labels, required)
    sentiment = analyze_sentiment(description)

    result = analyze_quest_stage(object_check, sentiment)

    if not result["is_valid"]:
        return {
            "success": False,
            "message": "그림 또는 설명에 필요한 요소가 부족합니다. 다시 제출해주세요."
        }

    # 조건 충족 시 
    return {
        "success": True,
        "message": "제출이 완료되었습니다."
    }
