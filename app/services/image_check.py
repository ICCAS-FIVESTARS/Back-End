# app/services/models/image_check.py
def validate_detection(detections, required_classes):
    found_classes = set(d["class"] for d in detections if d["confidence"] > 0.4)
    for cls in required_classes:
        if cls not in found_classes:
            return False, cls
    return True, None