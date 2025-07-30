from services.models.yolov8_detector import detect_objects
from ..models.gpt_interpreter import run_gpt_interpretation
from services.models.htp_interpreter import run_full_interpretation
from services.models.image_check import is_image_valid
from PIL import Image

# class 이름 매핑 (모델 → GPT-friendly)
LABEL_MAP = {
    "사람전체": "person",
    "집전체": "house",
    "나무전체": "tree"
}
REQUIRED_OBJECTS = set(LABEL_MAP.keys())  # 필수 탐지 클래스 (htp.pt 기준)

def analyze_htp_image(image_path: str, description: str, model_path: str = "assets/weights/htp.pt"):
    results = detect_objects(image_path, model_path=model_path, conf=0.4)
    boxes = results.boxes
    detected_labels = [results.names[int(cls)] for cls in boxes.cls] if boxes else []

    # 필수 요소 존재 여부 확인
    missing = [obj for obj in REQUIRED_OBJECTS if obj not in detected_labels]
    if missing:
        return {
            "success": False,
            "message": f"다음 필수 요소가 누락되었습니다: {', '.join(missing)}. 다시 제출해주세요.",
            "missing_required": missing
        }

    if not is_image_valid(boxes):
        return {
            "success": False,
            "message": "감지된 객체의 확신도가 낮습니다. 다시 제출해주세요."
        }

    # 이미지 크기 정보
    img = Image.open(image_path)
    width, height = img.size
    image_area = width * height

    position_dict = {}
    size_dict = {}

    for cls, box in zip(boxes.cls, boxes.xyxy):
        label = results.names[int(cls)]
        x1, y1, x2, y2 = box.tolist()

        # 중심 좌표 및 면적 계산
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        bw, bh = x2 - x1, y2 - y1
        size_ratio = (bw * bh) / image_area
        size_dict[LABEL_MAP.get(label, label)] = round(size_ratio, 4)

        # 위치 계산
        pos_x = "left" if cx < width / 3 else "right" if cx > width * 2 / 3 else "center"
        pos_y = "up" if cy < height / 3 else "down" if cy > height * 2 / 3 else "center"
        position_dict[LABEL_MAP.get(label, label)] = pos_x if label in REQUIRED_OBJECTS else pos_y

    # 해석 - 규칙 기반
    rule_based = run_full_interpretation(position_dict, size_dict)

    # GPT 해석 - 이미지 + 설명 모두 기반
    gpt_prompt = (
        "조현병 잔류기 환자의 HTP 검사입니다.\n"
        "그림의 주요 객체 위치와 크기는 다음과 같습니다.\n"
        f"위치 정보: {position_dict}\n"
        f"크기 정보: {size_dict}\n\n"
        f"또한, 사용자가 그림에 대해 다음과 같이 설명했습니다:\n\"{description}\"\n\n"
        "이 정보를 바탕으로 사용자의 심리 상태를 전문가처럼 해석해주세요."
    )
    gpt_response = run_gpt_interpretation(gpt_prompt)

    return {
        "success": True,
        "position": position_dict,
        "size": size_dict,
        "rule_based_interpretation": rule_based,
        "gpt_interpretation": gpt_response
    }
