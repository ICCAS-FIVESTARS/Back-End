# app/services/models/image_check.py
# 이미지 검증 관련 함수들

def is_image_valid(boxes, conf_threshold=0.7):
    """
    감지된 객체들의 신뢰도가 임계값 이상인지 확인
    """
    if not boxes or len(boxes.conf) == 0:
        return False
    
    # 모든 객체의 신뢰도가 임계값 이상인지 확인
    valid_detections = [conf for conf in boxes.conf if conf >= conf_threshold]
    return len(valid_detections) > 0

def check_required_objects(detected_labels, required_objects):
    """
    필수 객체들이 모두 감지되었는지 확인
    """
    missing = [obj for obj in required_objects if obj not in detected_labels]
    return len(missing) == 0, missing

def check_required_classes(detected_classes, required_classes):
    """
    필수 클래스들이 모두 감지되었는지 확인 (클래스 ID 기준)
    """
    missing = [cls for cls in required_classes if cls not in detected_classes]
    return len(missing) == 0, missing
