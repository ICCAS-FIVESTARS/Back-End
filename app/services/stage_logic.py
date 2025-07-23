from app.services.models.image_check import check_required_elements
from app.services.models.sentiment_kobert import analyze_sentiment
from app.services.models.owlvit_detector import detect_objects

def analyze_stage(image_path: str, description: str, required_elements: list[str]) -> dict:
    """
    이미지와 설명에 기반한 종합 분석 결과를 반환.
    필수 요소 누락 시 재제출 요청.
    감정 분석 결과는 DB 저장용으로만 사용.
    """
    # 1. 객체 탐지
    detected_labels = detect_objects(image_path)

    # 2. 필수 요소 체크
    is_valid, missing = check_required_elements(detected_labels, required_elements)

    # 3. 감정 분석 (DB 저장용)
    sentiment_result = analyze_sentiment(description)

    # 4. 상태 반환
    return {
        "status": "resubmit" if not is_valid else "accepted",
        "missing_elements": missing,       # 프론트에는 비표시
        "sentiment": sentiment_result      # DB 저장용
    }
