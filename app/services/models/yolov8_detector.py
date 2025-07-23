
from ultralytics import YOLO

MODEL_PATHS = {
    "htp": "assets/weights/htp.pt",
    "pitr": "assets/weights/pitr_yolov8.pt"
}

def detect_objects(image_path: str, model_name: str = "pitr"):
    model = YOLO(MODEL_PATHS[model_name])
    results = model.predict(source=image_path, imgsz=512, conf=0.4)[0]

    detections = []
    for box in results.boxes:
        class_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(float, box.xyxy[0])
        detections.append({
            "class": results.names[class_id],
            "confidence": conf,
            "box": (x1, y1, x2, y2)
        })
    return detections