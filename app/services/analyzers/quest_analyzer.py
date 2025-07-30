from app.services.models.yolov8_detector import detect_objects
from app.services.models.image_check import check_required_classes
from app.services.models.stage_logic import analyze_quest_stage
from app.services.models.gpt_interpreter import run_gpt_interpretation
from app.core.config import STAGE_REQUIRED_CLASSES
from PIL import Image

def analyze_quest(image_path: str, description: str, stage: int) -> dict:
    """
    12단계 Quest 분석: 객체 감지 + 설명 GPT 해석 + 조건 평가
    """
    # 객체 감지
    results = detect_objects(image_path, model_name="htp")  # htp.pt 사용
    boxes = results.boxes
    width, height = Image.open(image_path).size
    image_area = width * height

    if not boxes or len(boxes.cls) == 0:
        return {"success": False, "message": "그림에서 객체를 인식하지 못했습니다. 다시 제출해주세요."}

    # 필수 클래스 확인
    required_classes = STAGE_REQUIRED_CLASSES.get(stage, [])
    detected_classes = [int(cls) for cls in boxes.cls]
    missing_classes = [cls for cls in required_classes if cls not in detected_classes]

    if missing_classes:
        return {
            "success": False,
            "message": f"필수 요소가 누락되었습니다: {missing_classes}. 다시 제출해주세요.",
            "missing_required": missing_classes
        }

    # 위치, 크기 계산
    position_dict = {}
    size_dict = {}

    for cls, box in zip(boxes.cls, boxes.xyxy):
        label = results.names[int(cls)]
        x1, y1, x2, y2 = box.tolist()
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        bw, bh = x2 - x1, y2 - y1
        box_area = bw * bh
        size_ratio = box_area / image_area
        size_dict[label] = round(size_ratio, 4)

        pos_x = "left" if cx < width / 3 else "right" if cx > width * 2 / 3 else "center"
        pos_y = "up" if cy < height / 3 else "down" if cy > height * 2 / 3 else "center"
        position_dict[label] = pos_y  # 퀘스트에서는 Y축 위주로 사용

    # GPT 해석
    gpt_prompt = (
        f"이 사용자는 조현병 회복기 환자이며, 심리 미술 치료 중 12단계 퀘스트의 {stage}단계를 수행 중입니다.\n"
        f"그림의 객체 위치 정보: {position_dict}\n"
        f"그림의 객체 크기 정보: {size_dict}\n"
        f"설명 텍스트: \"{description}\"\n\n"
        "이 정보들을 바탕으로 이 사용자의 현재 정서 상태를 간결히 해석해주세요."
    )
    gpt_result = run_gpt_interpretation(gpt_prompt)

    # 조건 평가 (원래 로직 유지 가능)
    result = analyze_quest_stage(object_check=True, sentiment=gpt_result.get("sentiment", "중립"))

    if not result["is_valid"]:
        return {
            "success": False,
            "message": "그림 또는 설명이 요구 조건을 만족하지 못했습니다. 다시 제출해주세요.",
            "gpt_interpretation": gpt_result
        }

    return {
        "success": True,
        "message": "제출이 완료되었습니다.",
        "gpt_interpretation": gpt_result
    }
