from app.services.models.yolov8_detector import detect_objects
from app.services.models.pitr_interpreter import interpret_pitr
from app.services.models.gpt_interpreter import gpt_interpret
from app.services.models.image_check import validate_detection

def analyze_pitr(image_path: str, description: str):
    detections = detect_objects(image_path, model_name="pitr")
    status, missing = validate_detection(detections, required_classes=["person", "rain"])
    if not status:
        return {"success": False, "reason": f"'{missing}' 객체가 포함되지 않았어요."}

    if any(d["confidence"] < 0.5 for d in detections):
        return gpt_interpret(image_path=image_path, description=description)

    result = interpret_pitr(detections)
    result["text_analysis"] = gpt_interpret(description=description)
    return {"success": True, "result": result}
