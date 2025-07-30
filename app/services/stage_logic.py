from app.services.models.image_check import check_required_objects
from app.services.models.sentiment_kobert import analyze_sentiment
from app.services.models.yolov8_detector import detect_objects

def analyze_stage(image_path: str, description: str, stage: int) -> dict:
    """
    이미지와 설명에 기반한 종합 분석 결과를 반환.
    필수 요소 누락 시 재제출 요청.
    감정 분석 결과는 DB 저장용으로만 사용.
    """
    # 1. 객체 탐지 (YOLOv8 기반)
    detections = detect_objects(image_path, model_name="htp")
    detected_classes = [int(det["class"]) if isinstance(det["class"], int) else det["class"] for det in detections]

    # 2. 필수 요소 체크
    check_result = check_required_objects(detected_classes, stage)

    # 3. 감정 분석 (DB 저장용)
    sentiment_result = analyze_sentiment(description)

    # 4. 상태 반환
    return {
        "status": "accepted" if check_result["ok"] else "resubmit",
        "missing_elements": check_result["missing_classes"],  # 프론트에는 비표시
        "sentiment": sentiment_result      # DB 저장용
    }
