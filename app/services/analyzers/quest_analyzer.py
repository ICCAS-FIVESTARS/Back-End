from ..models.yolov8_detector import detect_objects
from ..models.image_check import check_required_classes
from ..models.stage_logic import analyze_stage, analyze_quest_stage
from ..models.gpt_analyzer import gpt_analyzer
from ...core.config import HTP_CLASS_NAMES, STAGE_REQUIRED_CLASSES
from PIL import Image

def analyze_quest(image_path: str, description: str, stage: int) -> dict:
    """
    12단계 Quest 분석: 객체 감지 + 설명 GPT 해석 + 조건 평가
    안전한 에러 처리 포함
    """
    try:
        # 더 안전한 경로 처리
        from pathlib import Path
        import os
        
        # Path 객체로 변환하여 자동으로 정규화
        path_obj = Path(image_path)
        normalized_path = path_obj.resolve()
        
        # 문자열로 변환하면서 이중 백슬래시 제거
        clean_path = str(normalized_path).replace('\\\\', '\\')
        
        # 추가 정규화: 경로를 다시 Path 객체로 만들어 문자열로 변환
        final_path = str(Path(clean_path))
        
        print(f"📍 Quest 분석 시작 (Stage {stage}):")
        print(f"   원본 경로: {image_path}")
        print(f"   Path 객체: {path_obj}")
        print(f"   정규화된 경로: {normalized_path}")
        print(f"   최종 경로: {final_path}")
        print(f"   파일 존재: {os.path.exists(final_path)}")
        
        # 파일 존재 확인
        if not os.path.exists(final_path):
            print(f"❌ 이미지 파일이 존재하지 않음: {final_path}")
            # 파일이 없어도 GPT 텍스트 분석 시도
            gpt_result = gpt_analyzer.analyze_drawing(
                stage=stage,
                detected_objects=[],
                description=description,
                position_dict={},
                size_dict={},
                analysis_type="quest"
            )
            
            return {
                "success": True,
                "message": "이미지 파일을 찾을 수 없어 설명만으로 분석했습니다.",
                "stage": stage,
                "analysis_type": "quest",
                "detected_objects": [],
                "position_analysis": {},
                "size_analysis": {},
                "gpt_analysis": gpt_result,
                "interpretation": gpt_result.get("interpretation", "설명 기반 분석 완료"),
                "emotion": gpt_result.get("emotion", "happiness"),
                "emotion_confidence": gpt_result.get("emotion_confidence", 0.3)
            }
        
        # 객체 감지 (최종 정리된 경로 사용) - 신뢰도 기반 분기
        print(f"🔍 Quest Stage {stage} - YOLO 객체 탐지 시작")
        results = detect_objects(final_path, model_name="htp", conf=0.4)  # htp.pt 사용
        
        # 신뢰도 기반 분기 분석 수행
        from ..models.confidence_analyzer import analyze_with_confidence_branching
        
        print(f"🎯 신뢰도 기반 Quest 분석 시작 (Stage {stage})")
        result = analyze_with_confidence_branching(results, final_path, description, stage)
        
        # Quest 특화 정보 추가
        result["analysis_type"] = "quest"
        result["stage"] = stage
        result["message"] = "제출이 완료되었습니다."
        
        return result
        
    except Exception as e:
        print(f"❌ Quest 분석 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "분석 중 오류가 발생했습니다.",
            "stage": stage,
            "analysis_type": "quest",
            "detected_objects": [],
            "position_analysis": {},
            "size_analysis": {},
            "gpt_analysis": {"interpretation": f"분석 중 오류 발생: {str(e)}", "emotion": "happiness", "emotion_confidence": 0.3},
            "interpretation": f"분석 중 오류가 발생했습니다: {str(e)}",
            "emotion": "happiness",
            "emotion_confidence": 0.3
        }
     