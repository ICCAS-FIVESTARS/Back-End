# app/api/analyze_router.py - 단순화된 분석 API
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
import os
import json
import time
from typing import Optional, Dict, Any
from pydantic import BaseModel

from ..services.analyzers.htp_analyzer import analyze_htp_image
from ..services.analyzers.pitr_analyzer import analyze_pitr
from ..services.analyzers.quest_analyzer import analyze_quest

# === API 모델 ===

class AnalysisResponse(BaseModel):
    """표준 분석 응답 모델"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CanvasData(BaseModel):
    """Canvas 데이터 모델"""
    paths: list
    width: int = 400
    height: int = 300
    scale: float = 2.0

# === 라우터 설정 ===

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# === API 엔드포인트 ===

@router.get("/health")
async def health_check():
    """API 상태 확인"""
    return AnalysisResponse(
        success=True,
        message="Drawing Analysis API is running",
        metadata={
            "service": "drawing-analysis",
            "version": "3.1.0",
            "endpoints": {
                "htp": "/analyze/htp - HTP 심리검사 (신뢰도 분기 + GPT Vision)",
                "pitr": "/analyze/pitr - PITR 심리검사 (신뢰도 분기 + GPT Vision)", 
                "quest": "/analyze/quest - Quest 단계별 (이미지 필수 + 텍스트 설명)",
                "stage_deprecated": "/analyze/stage - 더 이상 사용 안함 (quest 사용)"
            },
            "models": {
                "htp": "yolov8_htp_pt_with_confidence_branching",
                "pitr": "yolov8_pitr_pt_with_confidence_branching", 
                "quest": "gpt_vision_image_analysis"
            },
            "features": {
                "confidence_branching": True,
                "rule_based_interpretation": True,
                "gpt_vision_fallback": True,
                "gpt_vision_analysis": True,
                "ekman_emotions": True,
                "canvas_json_support": True
            }
        }
    ).dict()

@router.post("/analyze/htp")
async def analyze_htp_drawing(
    image: UploadFile = File(..., description="업로드할 HTP 그림 파일"),
    description: str = Form("", description="그림에 대한 사용자 설명")
):
    """
    HTP (House-Tree-Person) 심리 검사 분석 API
    - YOLOv8 .pt 모델로 객체 탐지
    - 위치/크기 기반 심리 해석
    - 신뢰도 기반 분기: 높은 신뢰도 → 규칙 기반, 낮은 신뢰도 → GPT Vision
    """
    try:
        print(f"🏠 HTP 분석 요청: {image.filename}")
        
        if not image or not image.filename:
            return AnalysisResponse(
                success=False,
                message="이미지 파일이 필요합니다.",
                error="NO_IMAGE_FILE"
            ).dict()
        
        # 이미지 처리
        image_path = await process_image_upload(image)
        
        # HTP 분석 수행
        print("🔍 HTP 분석 (.pt 모델)")
        result = analyze_htp_image(image_path, description)
        
        # 표준 응답 형식
        response = AnalysisResponse(
            success=result.get('success', True),
            message=result.get('message', 'HTP 분석이 완료되었습니다.'),
            data=result,
            metadata={
                "test_type": "htp",
                "analysis_type": "htp_pt_model",
                "model_used": "yolov8_htp_pt",
                "timestamp": time.time()
            }
        )
        
        # 임시 파일 정리
        cleanup_temp_file(image_path)
        
        print(f"✅ HTP 분석 완료")
        return response.dict()
        
    except Exception as e:
        print(f"❌ HTP 분석 오류: {e}")
        return AnalysisResponse(
            success=False,
            message="HTP 분석 중 오류가 발생했습니다.",
            error=str(e),
            metadata={"test_type": "htp"}
        ).dict()

@router.post("/analyze/pitr")
async def analyze_pitr_drawing(
    image: UploadFile = File(..., description="업로드할 PITR 그림 파일"),
    description: str = Form("", description="그림에 대한 사용자 설명")
):
    """
    PITR (Person In The Rain) 심리 검사 분석 API
    - YOLOv8 .pt 모델로 객체 탐지
    - 스트레스 대처 능력 분석
    - 신뢰도 기반 분기: 높은 신뢰도 → 규칙 기반, 낮은 신뢰도 → GPT Vision
    """
    try:
        print(f"🌧️ PITR 분석 요청: {image.filename}")
        
        if not image or not image.filename:
            return AnalysisResponse(
                success=False,
                message="이미지 파일이 필요합니다.",
                error="NO_IMAGE_FILE"
            ).dict()
        
        # 이미지 처리
        image_path = await process_image_upload(image)
        
        # PITR 분석 수행
        print("🔍 PITR 분석 (.pt 모델)")
        result = analyze_pitr(image_path, description)
        
        # 표준 응답 형식
        response = AnalysisResponse(
            success=result.get('success', True),
            message=result.get('message', 'PITR 분석이 완료되었습니다.'),
            data=result,
            metadata={
                "test_type": "pitr",
                "analysis_type": "pitr_pt_model",
                "model_used": "yolov8_pitr_pt",
                "timestamp": time.time()
            }
        )
        
        # 임시 파일 정리
        cleanup_temp_file(image_path)
        
        print(f"✅ PITR 분석 완료")
        return response.dict()
        
    except Exception as e:
        print(f"❌ PITR 분석 오류: {e}")
        return AnalysisResponse(
            success=False,
            message="PITR 분석 중 오류가 발생했습니다.",
            error=str(e),
            metadata={"test_type": "pitr"}
        ).dict()

@router.post("/analyze/quest")
async def analyze_quest_drawing(
    stage: int = Form(..., description="분석할 Quest 스테이지 번호 (1-12)"),
    image: UploadFile = File(..., description="업로드할 이미지 파일 또는 Canvas JSON"),
    description: str = Form(..., description="그림에 대한 사용자 설명")
):
    """
    Quest 단계별 그림 분석 API (Stage 1-12)
    - 이미지 필수 (Canvas JSON 또는 일반 이미지 파일) + 텍스트 설명
    - GPT Vision을 통한 이미지+텍스트 통합 분석
    - Ekman 6감정 분석
    - 단계별 질문에 맞춘 감정 해석
    """
    try:
        print(f"🎯 Quest Stage {stage} 분석 요청: {image.filename}")
        
        if not image or not image.filename:
            return AnalysisResponse(
                success=False,
                message="이미지 파일이 필요합니다. Canvas JSON 또는 이미지 파일을 업로드해주세요.",
                error="NO_IMAGE_FILE"
            ).dict()
        
        if not description or description.strip() == "":
            return AnalysisResponse(
                success=False,
                message="그림에 대한 설명이 필요합니다.",
                error="NO_DESCRIPTION"
            ).dict()
        
        if stage < 1 or stage > 12:
            return AnalysisResponse(
                success=False,
                message="Quest Stage는 1-12 범위여야 합니다.",
                error="INVALID_STAGE"
            ).dict()
        
        # 이미지 처리 (필수)
        print(f"📸 이미지 처리: {image.filename}")
        image_path = await process_image_upload(image)
        analysis_method = "gpt_vision_with_image"
        
        # Quest 분석 수행 - GPT 직접 분석
        print(f"🔍 Quest Stage {stage} 분석 - GPT")
        
        # GPT 분석 직접 수행
        from ..services.models.gpt_analyzer import gpt_analyzer
        
        gpt_result = gpt_analyzer.analyze_drawing(
            stage=stage,
            detected_objects=[],  # Quest는 객체 탐지하지 않음
            description=description,
            position_dict={},
            size_dict={},
            image_path=image_path,  # 이미지 필수 포함
            analysis_type="quest"
        )
        
        # Stage Question 정보 가져오기
        stage_question = get_stage_question_info(stage)
        
        # 응답 구성
        result = {
            "stage": stage,
            "analysis_type": "quest_gpt_vision",
            "stage_info": stage_question,
            "user_description": description,
            "gpt_analysis": gpt_result,
            "detected_objects": [],  # Quest는 객체 탐지하지 않음
            "analysis_method": analysis_method,
            "has_image": True  # 항상 이미지 있음
        }
        
        # 표준 응답 형식
        response = AnalysisResponse(
            success=True,
            message=f'Quest Stage {stage} 분석이 완료되었습니다.',
            data=result,
            metadata={
                "test_type": "quest",
                "stage": stage,
                "analysis_type": "quest_gpt_vision",
                "model_used": analysis_method,
                "has_image": True,  # 항상 이미지 있음
                "timestamp": time.time()
            }
        )
        
        # 임시 파일 정리
        cleanup_temp_file(image_path)
        
        print(f"✅ Quest Stage {stage} 분석 완료: {gpt_result.get('emotion')} ({gpt_result.get('emotion_confidence'):.2f})")
        return response.dict()
        
    except Exception as e:
        print(f"❌ Quest Stage {stage} 분석 오류: {e}")
        return AnalysisResponse(
            success=False,
            message=f"Quest Stage {stage} 분석 중 오류가 발생했습니다.",
            error=str(e),
            metadata={"test_type": "quest", "stage": stage}
        ).dict()

@router.post("/analyze/stage")
async def analyze_stage_drawing(
    stage: int = Form(..., description="분석할 스테이지 번호 (1-12)"),
    description: str = Form(..., description="그림에 대한 사용자 설명")
):
    """
    ⚠️ DEPRECATED: 이 엔드포인트는 더 이상 사용되지 않습니다.
    대신 /analyze/quest를 사용하세요 (이미지 없이도 텍스트만으로 분석 가능)
    """
    return AnalysisResponse(
        success=False,
        message="이 엔드포인트는 더 이상 사용되지 않습니다. /analyze/quest를 사용하세요.",
        error="DEPRECATED_ENDPOINT",
        metadata={
            "deprecated": True,
            "use_instead": "/analyze/quest",
            "stage": stage
        }
    ).dict()

# === 헬퍼 함수들 ===

def get_stage_question_info(stage: int) -> dict:
    """Stage별 질문 정보 반환"""
    stage_questions = {
        1: {
            "question": "지금의 나를 표현하고, '구름'을 그려보세요",
            "description": "현재의 감정을 구름으로 표현해보세요"
        },
        2: {
            "question": "현재 기분을 '태양'과 '구름'으로 표현해보세요", 
            "description": "따뜻함, 답답함 등 감정을 날씨의 이미지로 표현해보세요"
        },
        3: {
            "question": "당신을 '나무'에 비유해서 표현해보세요",
            "description": "뿌리, 가지, 잎 등을 통해 나의 내면과 성격을 표현해보세요"
        },
        4: {
            "question": "하루의 일상을 '길'을 따라 그려보세요",
            "description": "아침부터 저녁까지의 나의 하루를 길 위의 장면으로 표현해보세요"
        },
        5: {
            "question": "현재 기분을 '열매'를 통해 표현해보세요",
            "description": "슬픔, 기쁨, 분노 등의 감정을 열매의 색과 모양으로 시각화해보세요"
        },
        6: {
            "question": "나에게 소중한 사람들과 있는 장면을 그려보세요",
            "description": "가족이나 친구들과 함께 있는 모습을 통해 관계의 의미를 표현해보세요"
        },
        7: {
            "question": "마음을 편안하게 하는 '꽃 정원'을 꾸며보세요",
            "description": "좋아하는 꽃과 잔디로 채워진 공간을 상상하고 꾸며보세요"
        },
        8: {
            "question": "기억 속 특별했던 순간을 '별'과 함께 그려보세요",
            "description": "반짝였던 순간을 별과 함께 표현해보세요"
        },
        9: {
            "question": "내가 꿈꾸는 미래의 공간을 상상해 그려보세요",
            "description": "밝고 희망찬 공간을 집, 구름, 태양, 나무 등으로 구성해보세요"
        },
        10: {
            "question": "과거-현재-미래의 나를 '길 위의 인물'로 표현해보세요",
            "description": "시간의 흐름에 따라 나의 변화된 모습을 길 위에 순서대로 표현해보세요"
        },
        11: {
            "question": "내가 살고 싶은 마을을 그려보세요",
            "description": "사람들과 어울려 사는 모습을 상상하며 마을을 구성해보세요"
        },
        12: {
            "question": "지난 여정을 담은 '별'과 '꽃'이 있는 포스터를 완성해보세요",
            "description": "나의 변화와 성장을 상징하는 요소들을 사용해 나만의 이야기를 구성해보세요"
        }
    }
    
    return stage_questions.get(stage, {
        "question": "자유롭게 그림을 그려보세요",
        "description": "현재의 감정과 생각을 자유롭게 표현해보세요"
    })

async def process_image_upload(image: UploadFile) -> str:
    """이미지 업로드 통합 처리 (Canvas JSON 또는 일반 이미지)"""
    try:
        # Canvas JSON인지 확인
        is_canvas_json = (
            image.content_type == 'application/json' or 
            image.filename.endswith('.json') or
            'canvas_paths' in image.filename
        )
        
        if is_canvas_json:
            # Canvas JSON을 이미지로 변환
            return await process_canvas_json(image)
        else:
            # 일반 이미지 파일 처리
            return await process_image_file(image)
            
    except Exception as e:
        print(f"❌ 이미지 업로드 처리 오류: {e}")
        raise e

def cleanup_temp_file(file_path: str):
    """임시 파일 정리"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            print(f"🗑️ 임시 파일 삭제: {file_path}")
    except Exception as e:
        print(f"⚠️ 파일 삭제 실패: {e}")

async def process_canvas_json(json_file: UploadFile) -> str:
    try:
        # JSON 읽기
        content = await json_file.read()
        canvas_data_dict = json.loads(content.decode('utf-8'))
        canvas_data = CanvasData(**canvas_data_dict)
        
        print(f"📋 Canvas 변환: {len(canvas_data.paths)}개 경로")
        
        # PIL로 이미지 생성
        from PIL import Image, ImageDraw
        
        img_width = int(canvas_data.width * canvas_data.scale)
        img_height = int(canvas_data.height * canvas_data.scale)
        
        image = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(image)
        
        # SVG paths 그리기
        for path_info in canvas_data.paths:
            path_string = path_info.get('path', '')
            color = path_info.get('color', '#000000')
            stroke_width = int(path_info.get('strokeWidth', 3) * canvas_data.scale)
            
            points = parse_svg_path(path_string, canvas_data.scale)
            
            if len(points) > 1:
                for i in range(len(points) - 1):
                    draw.line([points[i], points[i + 1]], fill=color, width=stroke_width)
        
        # 파일 저장
        timestamp = int(time.time() * 1000)
        filename = f"canvas_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        file_path = UPLOAD_DIR / filename
        
        image.save(file_path, 'PNG', quality=95)
        
        return str(file_path.resolve()).replace('\\', '/')
        
    except Exception as e:
        print(f"Canvas 변환 오류: {e}")
        raise e

async def process_image_file(image: UploadFile) -> str:
    """일반 이미지 파일 저장"""
    try:
        # 파일 확장자 확인
        file_extension = Path(image.filename).suffix.lower() or '.png'
        
        # 파일 저장
        timestamp = int(time.time() * 1000)
        filename = f"img_{timestamp}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = UPLOAD_DIR / filename
        
        # 파일 쓰기
        content = await image.read()
        with file_path.open("wb") as f:
            f.write(content)
        
        print(f"📁 이미지 저장: {file_path} ({len(content)} bytes)")
        
        return str(file_path.resolve()).replace('\\', '/')
        
    except Exception as e:
        print(f"❌ 이미지 저장 오류: {e}")
        raise e

def parse_svg_path(path_string: str, scale: float = 1.0) -> list:
    """SVG path를 점 리스트로 변환"""
    import re
    
    points = []
    try:
        coords = re.findall(r'[\d\.-]+,[\d\.-]+', path_string)
        
        for coord in coords:
            try:
                x, y = coord.split(',')
                points.append((int(float(x) * scale), int(float(y) * scale)))
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ SVG 파싱 오류: {e}")
    
    return points
