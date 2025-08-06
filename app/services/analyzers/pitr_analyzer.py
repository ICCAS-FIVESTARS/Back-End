from ..models.yolov8_detector import detect_objects
from ..models.gpt_analyzer import gpt_analyzer
from ..models.pitr_interpreter import interpret_pitr
from ..models.image_check import is_image_valid
from ...core.config import YOLO_MODELS
from PIL import Image

# 클래스 이름 매핑 (PITR 모델 기준)
REQUIRED_LABELS = {"person", "rain"}

def analyze_pitr(image_path: str, description: str, model_path: str = None):
    """
    PITR 분석 - 안전한 에러 처리 포함
    """
    try:
        # config에서 모델 경로 가져오기
        if model_path is None:
            model_path = str(YOLO_MODELS["pitr"])
        
        # 경로 정규화
        import os
        normalized_path = os.path.normpath(image_path)
        if not os.path.isabs(normalized_path):
            normalized_path = os.path.abspath(normalized_path)
        
        print(f"📍 PITR 분석 시작:")
        print(f"   원본 경로: {image_path}")
        print(f"   정규화된 경로: {normalized_path}")
        print(f"   파일 존재: {os.path.exists(normalized_path)}")
        
        # 파일 존재 확인
        if not os.path.exists(normalized_path):
            print(f"❌ 이미지 파일이 존재하지 않음: {normalized_path}")
            # 파일이 없어도 GPT 텍스트 분석 시도
            gpt_response = gpt_analyzer.analyze_drawing(
                stage=1,
                detected_objects=[],
                description=description,
                position_dict={},
                size_dict={},
                analysis_type="pitr"
            )
            
            return {
                "success": True,
                "message": "이미지 파일을 찾을 수 없어 설명만으로 분석했습니다.",
                "stage": 1,
                "analysis_type": "pitr",
                "detected_objects": [],
                "position_analysis": {},
                "size_analysis": {},
                "gpt_analysis": gpt_response,
                "interpretation": gpt_response.get("interpretation", "설명 기반 PITR 분석 완료"),
                "emotion": gpt_response.get("emotion", "happiness"),
                "emotion_confidence": gpt_response.get("emotion_confidence", 0.3)
            }
        
        results = detect_objects(normalized_path, model_path=model_path, model_name="pitr", conf=0.4)
        
        # 신뢰도 기반 분기 분석 수행
        from ..models.confidence_analyzer import analyze_with_confidence_branching
        
        # 안전한 results 처리
        if results is None or not hasattr(results, 'boxes') or results.boxes is None:
            print("⚠️ YOLO 탐지 결과 없음 - 텍스트 분석으로 진행")
            return analyze_with_confidence_branching(None, normalized_path, description, 1)
        
        boxes = results.boxes
        
        # 빈 boxes 처리
        if not boxes or len(boxes) == 0 or (hasattr(boxes, 'cls') and len(boxes.cls) == 0):
            print("⚠️ 탐지된 객체 없음 - 텍스트 분석으로 진행")
            return analyze_with_confidence_branching(None, normalized_path, description, 1)
        
        # 신뢰도 기반 분기 분석 수행
        print(f"🎯 신뢰도 기반 PITR 분석 시작")
        result = analyze_with_confidence_branching(results, normalized_path, description, 1)
        
        # PITR 특화 정보 추가 및 interpreter 적용
        result["analysis_type"] = "pitr"
        result["stage"] = 1
        
        # interpreter 해석 추가 (높은 신뢰도 객체가 있을 때만)
        if result.get("analysis_method") == "rule_based_with_gpt_support":
            try:
                # PITR interpreter를 위한 데이터 변환
                detected_objects = result.get("detected_objects", [])
                high_conf_objects = result.get("high_confidence_objects", [])
                
                # PITR interpreter용 detection 형식으로 변환
                detections = []
                for obj_info in high_conf_objects:
                    detections.append({
                        "class": obj_info["label"],
                        "confidence": obj_info["confidence"],
                        "box": obj_info["box"]  # 실제 박스 좌표 사용
                    })
                
                if detections:
                    # 이미지 크기 정보
                    img = Image.open(normalized_path)
                    image_size = img.size
                    
                    # PITR interpreter 실행
                    pitr_interpretation = interpret_pitr(detections, image_size)
                    
                    # rule_based_interpretation 업데이트
                    result["rule_based_interpretation"] = {
                        "method": "pitr_interpreter",
                        "status": pitr_interpretation.get("status", "success"),
                        "interpretations": pitr_interpretation.get("analysis", []),
                        "detected_elements": detected_objects
                    }
                    
                    print(f"✅ PITR Interpreter 해석 완료")
                
            except Exception as e:
                print(f"⚠️ PITR Interpreter 오류: {e}")
        
        return result
        
    except Exception as e:
        print(f"❌ PITR 분석 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "분석 중 오류가 발생했습니다.",
            "stage": 1,
            "analysis_type": "pitr",
            "detected_objects": [],
            "position_analysis": {},
            "size_analysis": {},
            "gpt_analysis": {"interpretation": f"분석 중 오류 발생: {str(e)}", "emotion": "happiness", "emotion_confidence": 0.3},
            "interpretation": f"분석 중 오류가 발생했습니다: {str(e)}",
            "emotion": "happiness",
            "emotion_confidence": 0.3
        }
     