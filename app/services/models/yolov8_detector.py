from ultralytics import YOLO
import os
from ...core.config import YOLO_MODELS

def detect_objects(image_path: str, model_path: str = None, model_name: str = "htp", conf: float = 0.4):
    """
    객체 탐지 함수 - 안전한 에러 처리 및 경로 정규화 포함
    Args:
        image_path: 이미지 파일 경로
        model_path: 모델 파일 경로 (우선순위)
        model_name: 모델 이름 (htp, pitr)
        conf: 신뢰도 임계값
    Returns:
        YOLO 결과 객체 또는 안전한 빈 결과
    """
    try:
        # 더 안전한 경로 처리
        from pathlib import Path
        
        # Path 객체로 변환하여 자동으로 정규화
        path_obj = Path(image_path)
        normalized_image_path = str(path_obj.resolve())
        
        # 백슬래시를 일반 슬래시로 변환 (크로스 플랫폼 호환성)
        clean_path = normalized_image_path.replace('\\\\', '\\')
        
        # 이미지 파일 존재 확인
        if not os.path.exists(clean_path):
            print(f"❌ 이미지 파일이 존재하지 않음: {clean_path}")
            return create_empty_result()
        
        print(f"🔍 YOLO 분석 시작:")
        print(f"   원본 경로: {image_path}")
        print(f"   최종 경로: {clean_path}")
        
        # model_path가 제공되면 우선 사용, 없으면 model_name으로 선택
        if model_path and os.path.exists(model_path):
            selected_model_path = model_path
            print(f"   모델 경로 (직접): {model_path}")
        elif model_name in YOLO_MODELS:
            selected_model_path = str(YOLO_MODELS[model_name])
            print(f"   모델 경로 (config): {selected_model_path}")
        else:
            # 기본값으로 htp 모델 사용
            selected_model_path = str(YOLO_MODELS["htp"])
            print(f"   모델 경로 (기본값): {selected_model_path}")
        
        # 모델 파일 존재 확인
        if not os.path.exists(selected_model_path):
            print(f"❌ 모델 파일이 존재하지 않음: {selected_model_path}")
            return create_empty_result()
        
        print(f"✅ 모델 로드: {selected_model_path}")
        model = YOLO(selected_model_path)
        
        # 예측 수행 (최종 정리된 경로 사용)
        results = model.predict(source=clean_path, imgsz=512, conf=conf, verbose=False)
        
        if results and len(results) > 0:
            result = results[0]
            
            # 결과 검증
            if hasattr(result, 'boxes') and result.boxes is not None:
                num_detections = len(result.boxes) if hasattr(result.boxes, '__len__') else 0
                print(f"✅ YOLO 탐지 완료: {num_detections}개 객체 발견")
                return result
            else:
                print("⚠️ YOLO 결과에 boxes 속성이 없음")
                return create_empty_result()
        else:
            print("⚠️ YOLO 예측 결과가 비어있음")
            return create_empty_result()
            
    except Exception as e:
        print(f"❌ YOLO 탐지 중 오류: {e}")
        print(f"   원본 경로: {image_path}")
        if 'clean_path' in locals():
            print(f"   최종 경로: {clean_path}")
        if 'selected_model_path' in locals():
            print(f"   모델 경로: {selected_model_path}")
        return create_empty_result()

def get_confidence_scores(boxes):
    """
    박스들의 신뢰도 점수 반환
    """
    if not boxes or not hasattr(boxes, 'conf'):
        return []
    return boxes.conf.tolist() if hasattr(boxes.conf, 'tolist') else list(boxes.conf)

def categorize_detections_by_confidence(boxes, results, high_threshold=0.6, low_threshold=0.4):
    """
    신뢰도에 따라 탐지 결과를 분류
    Returns:
        dict: {
            'high_confidence': [(label, conf, box), ...],
            'low_confidence': [(label, conf, box), ...],
            'rejected': [(label, conf, box), ...]
        }
    """
    if not boxes or not hasattr(boxes, 'cls') or not hasattr(boxes, 'conf'):
        return {'high_confidence': [], 'low_confidence': [], 'rejected': []}
    
    high_confidence = []
    low_confidence = []
    rejected = []
    
    for cls, conf, box in zip(boxes.cls, boxes.conf, boxes.xyxy):
        label = results.names[int(cls)] if hasattr(results, 'names') else str(int(cls))
        conf_value = float(conf)
        
        if conf_value >= high_threshold:
            high_confidence.append((label, conf_value, box.tolist()))
        elif conf_value >= low_threshold:
            low_confidence.append((label, conf_value, box.tolist()))
        else:
            rejected.append((label, conf_value, box.tolist()))
    
    print(f"🎯 신뢰도 분류 결과:")
    print(f"   높은 신뢰도 (>={high_threshold}): {len(high_confidence)}개")
    print(f"   낮은 신뢰도 ({low_threshold}-{high_threshold}): {len(low_confidence)}개")
    print(f"   거부됨 (<{low_threshold}): {len(rejected)}개")
    
    return {
        'high_confidence': high_confidence,
        'low_confidence': low_confidence,
        'rejected': rejected
    }

def create_empty_result():
    """
    안전한 빈 결과 객체 생성
    """
    class EmptyResult:
        def __init__(self):
            self.boxes = EmptyBoxes()
            self.names = {}
    
    class EmptyBoxes:
        def __init__(self):
            self.cls = []
            self.xyxy = []
            self.conf = []
        
        def __len__(self):
            return 0
        
        def __bool__(self):
            return False
    
    return EmptyResult()