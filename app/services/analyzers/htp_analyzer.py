# services/analyzers/htp_analyzer.py

from services.models.yolov8_detector import detect_objects
from services.models.image_check import is_image_valid
from services.models.htp_interpreter import run_full_interpretation
from PIL import Image


def analyze_htp_image(image_path: str, model_path: str = "assets/weights/htp.pt"):
    """
    HTP 이미지 분석: 객체 검출 → 위치/크기 계산 → 해석 결과 반환
    """
    # Step 1: 객체 탐지
    results = detect_objects(image_path, model_path=model_path, conf=0.4)
    boxes = results.boxes

    if not boxes or len(boxes.cls) < 3:
        return {
            "status": "fail",
            "reason": "객체가 충분히 인식되지 않았습니다."
        }

    # Step 2: 유효성 체크
    if not is_image_valid(boxes):
        return {
            "status": "fail",
            "reason": "감지된 객체의 확신도가 낮습니다."
        }

    # Step 3: 위치 및 크기 계산
    img = Image.open(image_path)
    width, height = img.size
    image_area = width * height

    position_dict = {}
    size_dict = {}

    for cls, box in zip(boxes.cls, boxes.xyxy):
        label = results.names[int(cls)]
        x1, y1, x2, y2 = box.tolist()

        # 중심 좌표
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        bw, bh = x2 - x1, y2 - y1
        box_area = bw * bh
        size_ratio = box_area / image_area
        size_dict[label] = size_ratio

        # 위치 판별
        if cx < width / 3:
            pos_x = "left"
        elif cx > width * 2 / 3:
            pos_x = "right"
        else:
            pos_x = "center"

        if cy < height / 3:
            pos_y = "up"
        elif cy > height * 2 / 3:
            pos_y = "down"
        else:
            pos_y = "center"

        position_dict[label] = pos_x if label in ['home', 'tree', 'person'] else pos_y

    # Step 4: 해석 호출
    interpretation = run_full_interpretation(position_dict, size_dict)

    return {
        "status": "success",
        "position": position_dict,
        "size": size_dict,
        "interpretation": interpretation
    }
