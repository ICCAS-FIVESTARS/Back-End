# app/services/models/pitr_interpreter.py

from typing import List, Tuple, Dict
from ...core.config import DAPR_CLASS_NAMES  # PITR -> DAPR로 변경


def interpret_pitr(detections: List[Dict], image_size: Tuple[int, int]) -> Dict:
    """
    PITR(Person in the Rain) 해석 함수 (+ 정량적 스트레스 점수화)

    Args:
        detections (list): [{"class": "person", "box": [x1, y1, x2, y2], "confidence": 0.9}, ...]
        image_size (tuple): (width, height)

    Returns:
        dict: {
            "status": "success",
            "analysis": [해석 문장들]
        }
    """
    width, height = image_size
    area_total = width * height

    result = []
    has_person = False
    has_rain = False
    has_umbrella = False

    cloud_count = 0
    lightning_count = 0
    puddle_count = 0

    # 비 관련 스타일 점수 요소
    rain_boxes = []

    for det in detections:
        cls = det["class"]
        bbox = det["box"]
        conf = det.get("confidence", 1.0)
        if conf < 0.4:
            continue

        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]
        area_ratio = (bw * bh) / area_total

        horiz = "left" if cx < width / 3 else "right" if cx > width * 2 / 3 else "center"
        vert = "up" if cy < height / 3 else "down" if cy > height * 2 / 3 else "center"

        if cls == "person":
            has_person = True
            if horiz == "left":
                result.append("소극적이며 우울감을 가지고 있음.")
            elif horiz == "right":
                result.append("이기적이며 공격적이고 분노가 높음.")
            if vert == "up":
                result.append("통찰력이 부족하고 현실과 동떨어진 낙천주의를 가짐.")
            elif vert == "down":
                result.append("인간관계는 있으나 우울하고 위축됨.")
            if area_ratio <= 0.33:
                result.append("수축된 자아와 낮은 자존감을 가짐.")
            elif area_ratio >= 0.67:
                result.append("자기를 증명하려는 경향이 있음.")

        elif cls == "rain":
            has_rain = True
            rain_boxes.append((bw, bh, bw * bh))

        elif cls == "umbrella":
            has_umbrella = True
            result.append("방어기제를 나타내는 우산이 포함됨.")

        elif cls == "cloud":
            cloud_count += 1

        elif cls == "lightning":
            lightning_count += 1

        elif cls == "puddle" or cls == "pool":
            puddle_count += 1

    # 필수 요소 확인
    if not has_person or not has_rain:
        return {
            "status": "fail",
            "analysis": [],
            "reason": "필수 객체(person, rain)가 감지되지 않았습니다."
        }

    # -------------------------
    # 스트레스 점수 계산 (표 1 기반)
    # -------------------------
    stress_score = 0

    # 1. 비 표현 개수
    if len(rain_boxes) == 0:
        expression_score = 0
    elif len(rain_boxes) == 1:
        expression_score = 1
    else:
        expression_score = 2
    stress_score += expression_score

    # 2. 비 길이 (높이 기준)
    avg_height = sum([h for _, h, _ in rain_boxes]) / len(rain_boxes) if rain_boxes else 0
    if avg_height <= 20:
        stress_score += 0
    elif avg_height <= 50:
        stress_score += 1
    else:
        stress_score += 2

    # 3. 비 굵기 (너비 기준)
    avg_width = sum([w for w, _, _ in rain_boxes]) / len(rain_boxes) if rain_boxes else 0
    if avg_width <= 2:
        stress_score += 0
    elif avg_width <= 5:
        stress_score += 1
    else:
        stress_score += 2

    # 4. 비 면적 (총 비의 bbox 넓이 합 / 전체 면적)
    rain_total_area = sum([a for _, _, a in rain_boxes])
    rain_area_ratio = rain_total_area / area_total
    if rain_area_ratio <= 0.33:
        stress_score += 0
    elif rain_area_ratio <= 0.75:
        stress_score += 1
    else:
        stress_score += 2

    # 5. 그림 전체에 차지하는 비 면적
    if rain_area_ratio == 0:
        stress_score += 0
    elif rain_area_ratio <= 0.75:
        stress_score += 1
    else:
        stress_score += 2

    # 총점 기반 해석
    if stress_score >= 8:
        result.append("스트레스 수준: 상 (강한 스트레스 반응이 나타날 수 있음)")
    elif stress_score >= 5:
        result.append("스트레스 수준: 중 (일반적인 스트레스 반응)")
    else:
        result.append("스트레스 수준: 하 (스트레스 반응이 낮거나 없음)")

    # 추가 요소 해석
    if cloud_count >= 2:
        result.append("구름이 많이 그려져 정서적 혼란이나 우울감을 나타냄.")
    if lightning_count >= 2:
        result.append("번개가 많아 분노나 긴장 상태일 가능성이 있음.")
    if puddle_count >= 2:
        result.append("고인 물이 많아 감정의 정체 또는 우울함이 반영됨.")
    if not has_umbrella:
        result.append("보호 자원이 부족하거나 스트레스를 무방비로 받고 있음.")

    return {
        "status": "success",
        "analysis": result,
        "stress_score": stress_score,
        "rain_count": len(rain_boxes)
    }
