# app/services/models/confidence_analyzer.py
# 신뢰도 기반 분기 로직 처리

from typing import Dict, List, Tuple, Any
from PIL import Image

def analyze_with_confidence_branching(results, image_path: str, description: str, stage: int) -> Dict[str, Any]:
    """
    신뢰도 기반 분기 분석
    - 높은 신뢰도 (>=0.6): 규칙 기반 분석 + 위치/크기 분석
    - 낮은 신뢰도 (0.4-0.6): GPT 기반 분석
    - 탐지 실패 (<0.4): GPT 텍스트 분석만
    """
    from .yolov8_detector import categorize_detections_by_confidence
    from .gpt_analyzer import gpt_analyzer
    
    print(f"신뢰도 기반 분기 분석 시작 (Stage {stage})")
    
    # 신뢰도별 탐지 결과 분류
    confidence_categories = categorize_detections_by_confidence(
        results.boxes if results else None, 
        results,
        high_threshold=0.6,
        low_threshold=0.4
    )
    
    high_conf = confidence_categories['high_confidence']
    low_conf = confidence_categories['low_confidence']
    rejected = confidence_categories['rejected']
    
    # 분석 방식 결정
    if high_conf:
        # 높은 신뢰도 객체가 있는 경우 - 규칙 기반 + 위치/크기 분석
        print(f"높은 신뢰도 객체 발견 → 규칙 기반 분석 수행")
        return perform_rule_based_analysis(high_conf, low_conf, image_path, description, stage)
    
    elif low_conf:
        # 낮은 신뢰도 객체만 있는 경우 - GPT 기반 분석
        print(f"낮은 신뢰도 객체만 발견 → GPT 기반 분석 수행")
        return perform_gpt_based_analysis(low_conf, image_path, description, stage)
    
    else:
        # 객체 탐지 실패 - GPT 텍스트 분석만
        print(f"객체 탐지 실패 → GPT 텍스트 분석만 수행")
        return perform_text_only_analysis(description, stage)

def perform_rule_based_analysis(high_conf: List[Tuple], low_conf: List[Tuple], 
                               image_path: str, description: str, stage: int) -> Dict[str, Any]:
    """
    높은 신뢰도 객체에 대한 규칙 기반 분석
    """
    try:
        from .stage_logic import analyze_stage
        
        # 탐지된 객체 정보 구성
        detected_objects = []
        for label, conf, box in high_conf + low_conf:
            detected_objects.append(f"{label}({conf:.2f})")
        
        # 위치/크기 분석을 위한 데이터 구성
        position_dict, size_dict = analyze_object_positions_and_sizes(high_conf, image_path)
        
        # 규칙 기반 해석 생성
        rule_based_result = generate_rule_based_interpretation(high_conf, stage)
        
        # GPT 보조 분석 (이미지 포함)
        from .gpt_analyzer import gpt_analyzer
        # PITR 분석인지 확인 (stage=1이고 피처가 PITR 관련인 경우)
        analysis_type = "pitr" if stage == 1 else None
        gpt_result = gpt_analyzer.analyze_drawing(
            stage=stage,
            detected_objects=detected_objects,
            description=description,
            position_dict=position_dict,
            size_dict=size_dict,
            image_path=image_path,
            analysis_type=analysis_type
        )
        
        return {
            "success": True,
            "message": "높은 신뢰도 객체 탐지 성공",
            "analysis_method": "rule_based_with_gpt_support",
            "stage": stage,
            "detected_objects": detected_objects,
            "high_confidence_objects": [{"label": label, "confidence": conf, "box": box} for label, conf, box in high_conf],
            "low_confidence_objects": [{"label": label, "confidence": conf, "box": box} for label, conf, box in low_conf],
            "position_analysis": position_dict,
            "size_analysis": size_dict,
            "rule_based_interpretation": rule_based_result,
            "interpretation": combine_interpretations(rule_based_result, gpt_result),
            "emotion": gpt_result.get("emotion", "happiness"),
            "emotion_confidence": gpt_result.get("emotion_confidence", 0.7)
        }
        
    except Exception as e:
        print(f"규칙 기반 분석 오류: {e}")
        # 오류 시 GPT 분석으로 폴백
        return perform_gpt_based_analysis(high_conf + low_conf, image_path, description, stage)

def perform_gpt_based_analysis(low_conf: List[Tuple], image_path: str, 
                              description: str, stage: int) -> Dict[str, Any]:
    """
    낮은 신뢰도 객체에 대한 GPT 기반 분석
    """
    try:
        # 탐지된 객체 정보 구성
        detected_objects = []
        for label, conf, box in low_conf:
            detected_objects.append(f"{label}({conf:.2f})")
        
        # GPT 분석 수행 (이미지 포함)
        from .gpt_analyzer import gpt_analyzer
        # PITR 분석인지 확인 (stage=1이고 피처가 PITR 관련인 경우)
        analysis_type = "pitr" if stage == 1 else None
        gpt_result = gpt_analyzer.analyze_drawing(
            stage=stage,
            detected_objects=detected_objects,
            description=description,
            position_dict={},
            size_dict={},
            image_path=image_path,
            analysis_type=analysis_type
        )
        
        return {
            "success": True,
            "message": "낮은 신뢰도 객체 탐지, GPT 기반 분석 완료",
            "analysis_method": "gpt_based_analysis",
            "stage": stage,
            "detected_objects": detected_objects,
            "low_confidence_objects": [{"label": label, "confidence": conf, "box": box} for label, conf, box in low_conf],
            "position_analysis": {},
            "size_analysis": {},
            "interpretation": gpt_result.get("interpretation", "GPT 기반 분석 완료"),
            "emotion": gpt_result.get("emotion", "happiness"),
            "emotion_confidence": gpt_result.get("emotion_confidence", 0.5)
        }
        
    except Exception as e:
        print(f"GPT 기반 분석 오류: {e}")
        # 오류 시 텍스트 분석으로 폴백
        return perform_text_only_analysis(description, stage)

def perform_text_only_analysis(description: str, stage: int) -> Dict[str, Any]:
    """
    객체 탐지 실패 시 텍스트 기반 분석만 수행
    """
    try:
        # GPT 텍스트 분석
        from .gpt_analyzer import gpt_analyzer
        # PITR 분석인지 확인 (stage=1이고 피처가 PITR 관련인 경우)
        analysis_type = "pitr" if stage == 1 else None
        gpt_result = gpt_analyzer.analyze_drawing(
            stage=stage,
            detected_objects=[],
            description=description,
            position_dict={},
            size_dict={},
            image_path=None,  # 이미지 없음
            analysis_type=analysis_type
        )
        
        return {
            "success": True,
            "message": "객체 탐지 실패, 설명 기반 분석 완료",
            "analysis_method": "text_only_fallback",
            "stage": stage,
            "detected_objects": [],
            "position_analysis": {},
            "size_analysis": {},
            "interpretation": gpt_result.get("interpretation", "텍스트 기반 분석 완료"),
            "emotion": gpt_result.get("emotion", "happiness"),
            "emotion_confidence": gpt_result.get("emotion_confidence", 0.3)
        }
        
    except Exception as e:
        print(f"❌ 텍스트 분석 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "모든 분석 방법 실패",
            "analysis_method": "failed",
            "stage": stage,
            "detected_objects": [],
            "position_analysis": {},
            "size_analysis": {},
            "interpretation": f"분석 실패: {str(e)}",
            "emotion": "happiness",
            "emotion_confidence": 0.1
        }

def analyze_object_positions_and_sizes(detections: List[Tuple], image_path: str) -> Tuple[Dict, Dict]:
    """
    탐지된 객체들의 위치와 크기 분석
    """
    try:
        # 이미지 크기 가져오기
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        position_dict = {}
        size_dict = {}
        
        for label, conf, box in detections:
            # box는 [x1, y1, x2, y2] 형식
            x1, y1, x2, y2 = box
            
            # 중심점 계산
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            # 상대적 위치 (0~1)
            rel_x = center_x / img_width
            rel_y = center_y / img_height
            
            # 크기 계산
            width = x2 - x1
            height = y2 - y1
            area = width * height
            
            # 상대적 크기
            rel_area = area / (img_width * img_height)
            
            # 위치 해석
            pos_desc = get_position_description(rel_x, rel_y)
            size_desc = get_size_description(rel_area)
            
            position_dict[label] = {
                "center": (rel_x, rel_y),
                "description": pos_desc
            }
            
            size_dict[label] = {
                "relative_area": rel_area,
                "description": size_desc,
                "dimensions": (width, height)
            }
        
        return position_dict, size_dict
        
    except Exception as e:
        print(f"⚠️ 위치/크기 분석 오류: {e}")
        return {}, {}

def get_position_description(x: float, y: float) -> str:
    """
    상대적 위치를 설명으로 변환
    """
    h_pos = "가운데"
    if x < 0.33:
        h_pos = "왼쪽"
    elif x > 0.67:
        h_pos = "오른쪽"
    
    v_pos = "가운데"
    if y < 0.33:
        v_pos = "위쪽"
    elif y > 0.67:
        v_pos = "아래쪽"
    
    return f"{v_pos} {h_pos}"

def get_size_description(area: float) -> str:
    """
    상대적 크기를 설명으로 변환
    """
    if area < 0.1:
        return "작음"
    elif area < 0.3:
        return "보통"
    else:
        return "큼"

def generate_rule_based_interpretation(detections: List[Tuple], stage: int) -> Dict[str, Any]:
    """
    규칙 기반 해석 생성
    """
    try:
        interpretations = []
        detected_labels = [label for label, _, _ in detections]
        
        # 단계별 규칙 기반 해석
        if stage == 0:  # HTP
            if "사람전체" in detected_labels:
                interpretations.append("사람이 명확하게 그려져 있어 자아 표현이 잘 되고 있습니다.")
            if "집전체" in detected_labels:
                interpretations.append("집이 표현되어 가정과 안정감에 대한 인식이 나타났습니다.")
            if "나무전체" in detected_labels:
                interpretations.append("나무를 통해 성장과 생명력이 표현되었습니다.")
                
        elif stage == 1:  # PITR
            if "person" in detected_labels:
                interpretations.append("사람이 그려져 스트레스 상황에서의 자아가 표현되었습니다.")
            if "rain" in detected_labels:
                interpretations.append("비가 표현되어 스트레스 상황이 인식되고 있습니다.")
            if "umbrella" in detected_labels:
                interpretations.append("우산이 있어 스트레스에 대한 대처 방안을 갖고 있습니다.")
        
        # 기본 해석이 없으면 일반적인 해석 추가
        if not interpretations:
            interpretations.append("그림을 통한 표현이 이루어졌습니다.")
        
        return {
            "method": "rule_based",
            "detected_objects": detected_labels,
            "interpretations": interpretations
        }
        
    except Exception as e:
        return {
            "method": "rule_based",
            "error": str(e),
            "interpretations": ["규칙 기반 분석 중 오류가 발생했습니다."]
        }

def combine_interpretations(rule_based: Dict[str, Any], gpt_result: Dict[str, Any]) -> str:
    """
    규칙 기반 해석과 GPT 해석을 결합
    """
    try:
        combined = []
        
        # 규칙 기반 해석 추가
        if rule_based.get("interpretations"):
            combined.append("【구조적 분석】")
            combined.extend(rule_based["interpretations"])
        
        # GPT 해석 추가
        if gpt_result.get("interpretation"):
            combined.append("\n【전문가 해석】")
            combined.append(gpt_result["interpretation"])
        
        return "\n".join(combined) if combined else "분석이 완료되었습니다."
        
    except Exception as e:
        return gpt_result.get("interpretation", "분석이 완료되었습니다.")
