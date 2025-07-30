from ..models.yolov8_detector import detect_objects
from ..models.gpt_interpreter import run_gpt_interpretation
from ..models.image_check import is_image_valid
from PIL import Image

# 클래스 이름 매핑 (PITR 모델 기준)
REQUIRED_LABELS = {"person", "rain"}

def analyze_pitr(image_path: str, description: str, model_path: str = "assets/weights/pitr_yolov8.pt"):
    results = detect_objects(image_path, model_path=model_path, conf=0.4)
    boxes = results.boxes
    detected_labels = [results.names[int(cls)] for cls in boxes.cls] if boxes else []

    # 필수 객체 누락 확인
    missing = [obj for obj in REQUIRED_LABELS if obj not in detected_labels]
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
        size_dict[label] = round(size_ratio, 4)

        # 위치 계산
        pos_x = "left" if cx < width / 3 else "right" if cx > width * 2 / 3 else "center"
        pos_y = "up" if cy < height / 3 else "down" if cy > height * 2 / 3 else "center"
        position_dict[label] = pos_x if label == "person" else pos_y

    # GPT 해석용 프롬프트 구성
    gpt_prompt = (
        "조현병 잔류기 환자의 그림입니다. 분석 대상은 비를 맞는 사람(PITR)입니다.\n"
        f"객체 위치 정보: {position_dict}\n"
        f"객체 크기 정보: {size_dict}\n"
        f"그림에 대한 설명: \"{description}\"\n\n"
        "이 정보를 바탕으로 사용자의 정서 상태나 심리 상태를 해석해주세요."
    )
    gpt_response = run_gpt_interpretation(gpt_prompt)

    return {
        "success": True,
        "position": position_dict,
        "size": size_dict,
        "gpt_interpretation": gpt_response
    }
