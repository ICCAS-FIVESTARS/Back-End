from ..models.yolov8_detector import detect_objects
from ..models.gpt_analyzer import gpt_analyzer
from ..models.htp_interpreter import run_full_interpretation
from ..models.image_check import is_image_valid
from ...core.config import YOLO_MODELS
from PIL import Image


# class 이름 매핑 (모델 → GPT-friendly)
LABEL_MAP = {
    "사람전체": "person",
    "집전체": "house",
    "나무전체": "tree"
}
REQUIRED_OBJECTS = set(LABEL_MAP.keys())  # 필수 탐지 클래스 (htp.pt 기준)

def analyze_htp_image(image_path: str, description: str, model_path: str = None):
    """
    HTP 이미지 분석 - 안전한 에러 처리 포함
    """
    try:
        # config에서 모델 경로 가져오기
        if model_path is None:
            model_path = str(YOLO_MODELS["htp"])
        
        # 경로 정규화
        import os
        normalized_path = os.path.normpath(image_path)
        if not os.path.isabs(normalized_path):
            normalized_path = os.path.abspath(normalized_path)
        
        print(f"📍 HTP 분석 시작:")
        print(f"   원본 경로: {image_path}")
        print(f"   정규화된 경로: {normalized_path}")
        print(f"   파일 존재: {os.path.exists(normalized_path)}")
        
        # 파일 존재 확인
        if not os.path.exists(normalized_path):
            print(f"❌ 이미지 파일이 존재하지 않음: {normalized_path}")
            # 파일이 없어도 GPT 텍스트 분석 시도
            gpt_response = gpt_analyzer.analyze_drawing(
                stage=0,
                detected_objects=[],
                description=description,
                position_dict={},
                size_dict={},
                analysis_type="htp"
            )
            
            return {
                "success": True,
                "message": "이미지 파일을 찾을 수 없어 설명만으로 분석했습니다.",
                "stage": 0,
                "analysis_type": "htp",
                "detected_objects": [],
                "position_analysis": {},
                "size_analysis": {},
                "rule_based_interpretation": {"message": "이미지 파일을 찾을 수 없어 규칙 기반 분석을 수행할 수 없습니다."},
                "gpt_analysis": gpt_response,
                "interpretation": "이미지 파일을 찾을 수 없어 설명만으로 분석했습니다.",
                "emotion": gpt_response.get("emotion", "happiness"),
                "emotion_confidence": gpt_response.get("emotion_confidence", 0.3)
            }
        
        results = detect_objects(normalized_path, model_path=model_path, model_name="htp", conf=0.4)
        
        # 신뢰도 기반 분기 분석 수행
        from ..models.confidence_analyzer import analyze_with_confidence_branching
        
        # 안전한 results 처리
        if results is None or not hasattr(results, 'boxes') or results.boxes is None:
            print("⚠️ YOLO 탐지 결과 없음 - 텍스트 분석으로 진행")
            return analyze_with_confidence_branching(None, normalized_path, description, 0)
        
        boxes = results.boxes
        
        # boxes가 비어있는 경우 처리
        if not boxes or len(boxes) == 0 or (hasattr(boxes, 'cls') and len(boxes.cls) == 0):
            print("⚠️ 탐지된 객체 없음 - 텍스트 분석으로 진행")
            return analyze_with_confidence_branching(None, normalized_path, description, 0)
        
        # 신뢰도 기반 분기 분석 수행
        print(f"🎯 신뢰도 기반 HTP 분석 시작")
        result = analyze_with_confidence_branching(results, normalized_path, description, 0)
        
        # HTP 특화 정보 추가 및 interpreter 적용
        result["analysis_type"] = "htp"
        result["stage"] = 0
        
        # interpreter 해석 추가 (높은 신뢰도 객체가 있을 때만)
        if result.get("analysis_method") == "rule_based_with_gpt_support":
            try:
                # 기존 rule_based_interpretation을 HTP interpreter로 교체
                position_dict = result.get("position_analysis", {})
                size_dict = result.get("size_analysis", {})
                
                # HTP 키 매핑 (confidence_analyzer의 결과를 interpreter 형식으로)
                htp_position = {}
                htp_size = {}
                
                print(f"🔍 디버그 - position_dict: {position_dict}")
                print(f"🔍 디버그 - size_dict: {size_dict}")
                
                for key, value in position_dict.items():
                    if key in ["person", "사람전체"]:
                        htp_position["person"] = value
                    elif key in ["house", "집전체"]:
                        htp_position["home"] = value
                    elif key in ["tree", "나무전체"]:
                        htp_position["tree"] = value
                
                for key, value in size_dict.items():
                    if key in ["person", "사람전체"]:
                        htp_size["person"] = value
                    elif key in ["house", "집전체"]:
                        htp_size["home"] = value
                    elif key in ["tree", "나무전체"]:
                        htp_size["tree"] = value
                
                print(f"🔍 디버그 - htp_position: {htp_position}")
                print(f"🔍 디버그 - htp_size: {htp_size}")
                
                # HTP interpreter 실행
                htp_interpretation = run_full_interpretation(htp_position, htp_size)
                
                # rule_based_interpretation 업데이트
                result["rule_based_interpretation"] = {
                    "method": "htp_interpreter",
                    "interpretations": htp_interpretation,
                    "position_analysis": htp_position,
                    "size_analysis": htp_size
                }
                
                print(f"✅ HTP Interpreter 해석 완료: {len(htp_interpretation)}개 해석")
                
            except Exception as e:
                print(f"⚠️ HTP Interpreter 오류: {e}")
        
        return result
        
    except Exception as e:
        print(f"❌ HTP 분석 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "분석 중 오류가 발생했습니다.",
            "stage": 0,
            "analysis_type": "htp",
            "detected_objects": [],
            "position_analysis": {},
            "size_analysis": {},
            "rule_based_interpretation": {"error": str(e)},
            "gpt_analysis": {"interpretation": f"분석 중 오류 발생: {str(e)}", "emotion": "happiness", "emotion_confidence": 0.3},
            "interpretation": f"분석 중 오류가 발생했습니다: {str(e)}",
            "emotion": "happiness",
            "emotion_confidence": 0.3
        }
        