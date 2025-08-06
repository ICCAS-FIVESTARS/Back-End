# app/services/image_check.py
from app.core.config import STAGE_REQUIRED_CLASSES

CLASS_ID_TO_NAME = {
    0: "house", 3: "door", 4: "window", 8: "road",
    12: "flower", 13: "grass", 14: "sun", 15: "tree",
    18: "branch", 19: "root", 20: "leaf", 22: "fruit",
    26: "cloud", 28: "star", 29: "person"
}

def check_required_objects(detected_classes: list[int], stage: int) -> dict:
    """해당 회기의 필수 객체가 감지되었는지 검사"""
    required = STAGE_REQUIRED_CLASSES.get(stage, [])
    missing = [cid for cid in required if cid not in detected_classes]

    return {
        "ok": len(missing) == 0,
        "missing_classes": [CLASS_ID_TO_NAME.get(cid, f"class_{cid}") for cid in missing],
        "required_classes": [CLASS_ID_TO_NAME.get(cid, f"class_{cid}") for cid in required],
    }
