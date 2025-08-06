# app/services/models/gpt_analyzer.py
# GPT 분석 서비스 (Ekman's 6 Basic Emotions 기반)

import openai
from openai import OpenAI
from app.core.config import OPENAI_API_KEY, GPT_MODEL, GPT_MAX_TOKENS, GPT_TEMPERATURE
import json
import logging
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Paul Ekman의 6가지 기본 감정
EKMAN_EMOTIONS = ["anger", "disgust", "fear", "happiness", "sadness", "surprise"]

class GPTAnalyzer:
    def __init__(self):
        if OPENAI_API_KEY and OPENAI_API_KEY != "your-key-here":
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            logger.warning("OpenAI API key not configured. GPT analysis disabled.")
    
    def analyze_drawing(self, stage, detected_objects, description, position_dict=None, size_dict=None, image_path=None, analysis_type=None):
        """
        그림 분석을 위한 GPT 호출 - 이미지 직접 분석 지원
        """
        if not self.enabled:
            return {
                "interpretation": "GPT 분석이 비활성화되어 있습니다. API 키를 설정해주세요.",
                "emotion": "happiness",
                "emotion_confidence": 0.3
            }
        
        try:
            # 이미지가 제공된 경우 Vision API 사용
            if image_path and self._is_vision_model():
                return self._analyze_with_vision(stage, detected_objects, description, position_dict, size_dict, image_path, analysis_type)
            else:
                # 기존 텍스트 기반 분석
                return self._analyze_with_text(stage, detected_objects, description, position_dict, size_dict, analysis_type)
            
        except Exception as e:
            logger.error(f"GPT 분석 오류: {e}")
            return {
                "interpretation": f"GPT 분석 중 오류가 발생했습니다: {str(e)}",
                "emotion": "happiness",
                "emotion_confidence": 0.3
            }
    
    def _is_vision_model(self):
        """
        현재 모델이 Vision을 지원하는지 확인
        """
        vision_models = ["gpt-4-vision-preview", "gpt-4o", "gpt-4o-mini"]
        return GPT_MODEL in vision_models
    
    def _analyze_with_vision(self, stage, detected_objects, description, position_dict, size_dict, image_path, analysis_type=None):
        """
        GPT Vision을 사용한 이미지 직접 분석
        """
        try:
            # 더 안전한 경로 처리
            from pathlib import Path
            import os
            
            # Path 객체로 변환하여 자동으로 정규화
            path_obj = Path(image_path)
            normalized_path = str(path_obj.resolve())
            
            # 백슬래시를 일반 슬래시로 변환 (크로스 플랫폼 호환성)
            clean_path = normalized_path.replace('\\\\', '\\')
            
            if not os.path.exists(clean_path):
                logger.warning(f"이미지 파일 없음, 텍스트 분석으로 폴백: {clean_path}")
                return self._analyze_with_text(stage, detected_objects, description, position_dict, size_dict, analysis_type)
            
            # 이미지를 base64로 인코딩
            base64_image = self._encode_image(clean_path)
            
            # Vision 전용 프롬프트 생성
            prompt = self._create_vision_analysis_prompt(stage, detected_objects, description, position_dict, size_dict, analysis_type)
            
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": self._get_vision_system_prompt()},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=GPT_MAX_TOKENS,
                temperature=GPT_TEMPERATURE
            )
            
            result = response.choices[0].message.content
            logger.info("GPT Vision 분석 성공")
            return self._parse_gpt_response(result)
            
        except Exception as e:
            logger.error(f"GPT Vision 분석 오류: {e}")
            # Vision 실패 시 텍스트 기반으로 폴백
            logger.info("텍스트 기반 분석으로 폴백")
            return self._analyze_with_text(stage, detected_objects, description, position_dict, size_dict, analysis_type)
    
    def _analyze_with_text(self, stage, detected_objects, description, position_dict, size_dict, analysis_type=None):
        """
        기존 텍스트 기반 분석
        """
        prompt = self._create_analysis_prompt(stage, detected_objects, description, position_dict, size_dict, analysis_type)
        
        response = self.client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=GPT_MAX_TOKENS,
            temperature=GPT_TEMPERATURE
        )
        
        result = response.choices[0].message.content
        return self._parse_gpt_response(result)
    
    def _encode_image(self, image_path):
        """
        이미지를 base64로 인코딩 - 경로 정규화 및 안전한 처리
        """
        try:
            # 경로 정규화 (백슬래시 문제 해결)
            import os
            normalized_path = os.path.normpath(image_path)
            
            # 절대 경로로 변환
            if not os.path.isabs(normalized_path):
                # 현재 작업 디렉토리 기준으로 절대 경로 생성
                normalized_path = os.path.abspath(normalized_path)
            
            # 파일 존재 확인
            if not os.path.exists(normalized_path):
                logger.error(f"이미지 파일이 존재하지 않습니다: {normalized_path}")
                raise FileNotFoundError(f"Image file not found: {normalized_path}")
            
            logger.info(f"이미지 로딩 시도: {normalized_path}")
            
            # 이미지 최적화 (크기 조정)
            with Image.open(normalized_path) as img:
                # 이미지 크기 제한 (최대 1024x1024)
                max_size = 1024
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # JPEG로 변환하여 용량 최적화
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # 메모리 버퍼에 저장
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85, optimize=True)
                buffer.seek(0)
                
                # base64 인코딩
                image_data = buffer.read()
                logger.info(f"이미지 인코딩 성공: {len(image_data)} bytes")
                return base64.b64encode(image_data).decode('utf-8')
                
        except Exception as e:
            logger.error(f"이미지 인코딩 오류: {e}")
            raise e
    
    def _get_vision_system_prompt(self):
        """
        Vision API용 시스템 프롬프트
        """
        return """
당신은 조현병 회복기 환자를 위한 심리 미술 치료 전문가입니다.
환자가 그린 그림을 직접 보고 분석하여 심리 상태를 파악하고 적절한 피드백을 제공합니다.

**이미지 분석 시 중점 사항:**
1. 그림의 전체적인 구성과 색상 사용
2. 선의 굵기, 압력, 방향성
3. 공간 활용과 객체 배치
4. 세부 묘사의 정도와 완성도
5. 상징적 요소와 은유적 표현

**심리 분석 관점:**
- 긍정적이고 격려적인 톤으로 응답
- 환자의 감정 상태를 세심하게 파악
- 치료적 관점에서의 해석
- 구체적이고 실용적인 제안

**Ekman의 6가지 기본 감정 분석 기준:**
- anger: 분노, 짜증, 적대감이 드러나는 경우
- disgust: 혐오, 거부감, 불쾌감이 나타나는 경우
- fear: 두려움, 불안, 걱정이 명확히 드러나는 경우
- happiness: 기쁨, 만족, 즐거움, 희망이 표현되는 경우
- sadness: 슬픔, 우울, 상실감이 나타나는 경우
- surprise: 놀라움, 호기심, 새로운 발견이 드러나는 경우

응답은 반드시 다음 JSON 형식으로만 해주세요:
```json
{
    "interpretation": "이미지를 직접 보고 분석한 전문적 해석 (300자 이상)",
    "emotion": "anger/disgust/fear/happiness/sadness/surprise",
    "emotion_confidence": 0.0~1.0
}
```"""
    
    def _create_vision_analysis_prompt(self, stage, detected_objects, description, position_dict, size_dict, analysis_type=None):
        """
        Vision API용 분석 프롬프트 생성
        """
        prompt = f"""
환자가 그린 그림을 이미지와 함께 분석해주세요.

**치료 단계**: {stage}단계
**환자의 그림 설명**: {description}
"""
        
        # YOLO 탐지 정보도 참고 자료로 제공
        if detected_objects:
            prompt += f"\n**AI 객체 탐지 결과 (참고용)**: {detected_objects}"
        
        if position_dict:
            prompt += f"\n**객체 위치 정보 (참고용)**: {position_dict}"
        
        if size_dict:
            prompt += f"\n**객체 크기 정보 (참고용)**: {size_dict}"
        
        stage_context = self._get_stage_context(stage, analysis_type)
        if stage_context:
            prompt += f"\n**단계별 치료 목표**: {stage_context}"
        
        prompt += """

**분석 요청사항:**
1. 이미지를 직접 관찰하여 그림의 특징을 분석해주세요
2. 선의 세기, 색상, 구성, 완성도 등을 종합적으로 평가해주세요
3. AI가 탐지한 객체 정보는 참고만 하고, 실제 이미지에서 보이는 모든 요소를 고려해주세요
4. 환자의 설명에 대한 연관성도 분석해주세요
"""
        
        return prompt
    
    def _get_system_prompt(self):
        """
        시스템 프롬프트 정의
        """
        return """
당신은 조현병 회복기 환자를 위한 심리 미술 치료 전문가입니다.
그림 분석을 통해 환자의 심리 상태를 파악하고 분석합니다.

분석 시 다음 사항을 고려해주세요:
1. 환자의 감정 상태를 세심하게 파악
2. 치료적 관점에서의 해석
3. 구체적이고 실용적인 제안

**Ekman의 6가지 기본 감정 분석 기준:**
- anger: 분노, 짜증, 적대감이 드러나는 경우
- disgust: 혐오, 거부감, 불쾌감이 나타나는 경우
- fear: 두려움, 불안, 걱정이 명확히 드러나는 경우
- happiness: 기쁨, 만족, 즐거움, 희망이 표현되는 경우
- sadness: 슬픔, 우울, 상실감이 나타나는 경우
- surprise: 놀라움, 호기심, 새로운 발견이 드러나는 경우

응답은 반드시 다음 JSON 형식으로만 해주세요:
```json
{
    "interpretation": "그림에 대한 전문적 해석 (200자 이상)",
    "emotion": "anger/disgust/fear/happiness/sadness/surprise",
    "emotion_confidence": 0.0~1.0
}
```"""
    
    def _create_analysis_prompt(self, stage, detected_objects, description, position_dict, size_dict, analysis_type=None):
        """
        분석용 프롬프트 생성
        """
        prompt = f"""
환자가 그린 그림을 분석해주세요.

**치료 단계**: {stage}단계
**그림 설명**: {description}
**탐지된 객체들**: {detected_objects}
"""
        
        if position_dict:
            prompt += f"\n**객체 위치 정보**: {position_dict}"
        
        if size_dict:
            prompt += f"\n**객체 크기 정보**: {size_dict}"
        
        stage_context = self._get_stage_context(stage, analysis_type)
        if stage_context:
            prompt += f"\n**단계별 치료 목표**: {stage_context}"
        
        return prompt
    
    def _get_stage_context(self, stage, analysis_type=None):
        """
        단계별 치료 맥락 제공
        """
        # PITR 특별 처리
        if analysis_type == "pitr" and stage == 1:
            return "PITR 검사 - 스트레스 및 대처 능력 평가 (빗속의 사람 그리기)"
        
        stage_contexts = {
            # 기본 심리 검사 (고정 stage)
            0: "HTP 검사 - 기본적인 심리 상태 평가 (집-나무-사람 그리기)",
            
            # Quest 치료 단계 (1-12) - PITR과 겹치는 stage 1은 Quest로 우선 처리
            1: "Quest 1단계 - 현재 감정 인식: 구름을 통한 자아 표현",
            2: "Quest 2단계 - 기분 표현: 태양과 구름으로 감정 시각화", 
            3: "Quest 3단계 - 자아 성찰: 나무를 통한 내면 탐색",
            4: "Quest 4단계 - 일상 돌아보기: 길을 따라 하루 일과 표현",
            5: "Quest 5단계 - 감정 구체화: 열매를 통한 감정 표현",
            6: "Quest 6단계 - 관계 탐색: 소중한 사람들과의 관계 표현",
            7: "Quest 7단계 - 마음의 안식: 꽃 정원으로 편안함 표현",
            8: "Quest 8단계 - 소중한 기억: 별과 함께 특별한 순간 표현",
            9: "Quest 9단계 - 미래 비전: 꿈꾸는 미래 공간 상상",
            10: "Quest 10단계 - 시간 여행: 과거-현재-미래의 나 표현",
            11: "Quest 11단계 - 공동체 의식: 이상적인 마을 구성",
            12: "Quest 12단계 - 성장 완성: 별과 꽃으로 여정 완성"
        }
        
        return stage_contexts.get(stage, "일반적인 그림 치료 단계")
    
    def _parse_gpt_response(self, response_text):
        """
        GPT 응답 파싱 - JSON 블록 추출 지원
        """
        try:
            # ```json ... ``` 형식에서 JSON 추출
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end != -1:
                    json_text = response_text[start:end].strip()
                else:
                    json_text = response_text[start:].strip()
            else:
                json_text = response_text.strip()
            
            # JSON 파싱 시도
            result = json.loads(json_text)
            
            # 필수 필드 확인 및 기본값 설정
            parsed_result = {
                "interpretation": result.get("interpretation", "분석 결과를 파싱할 수 없습니다."),
                "emotion": result.get("emotion", "happiness"),
                "emotion_confidence": result.get("emotion_confidence", 0.5)
            }
            
            # 감정 분석 결과 정규화 (Ekman's 6 emotions)
            emotion = parsed_result["emotion"].lower()
            if emotion in EKMAN_EMOTIONS:
                parsed_result["emotion"] = emotion
            else:
                # 기존 감정 표현을 Ekman 감정으로 매핑
                emotion_mapping = {
                    "긍정적": "happiness", "positive": "happiness", "기쁨": "happiness", "즐거움": "happiness",
                    "부정적": "sadness", "negative": "sadness", "우울": "sadness", "슬픔": "sadness",
                    "불안": "fear", "두려움": "fear", "걱정": "fear",
                    "분노": "anger", "화남": "anger", "짜증": "anger",
                    "놀라움": "surprise", "신기함": "surprise",
                    "혐오": "disgust", "거부감": "disgust"
                }
                
                # 텍스트에서 감정 키워드 찾기
                for keyword, ekman_emotion in emotion_mapping.items():
                    if keyword in emotion or keyword in result.get("interpretation", ""):
                        parsed_result["emotion"] = ekman_emotion
                        break
                else:
                    parsed_result["emotion"] = "happiness"  # 기본값
            
            logger.info(f"GPT 분석 성공: emotion={parsed_result['emotion']}, confidence={parsed_result['emotion_confidence']}")
            return parsed_result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            # JSON 파싱 실패 시 텍스트에서 감정 키워드 추출 시도
            emotion = "happiness"  # 기본값
            confidence = 0.3
            
            # 키워드 기반 감정 매핑
            emotion_keywords = {
                "anger": ["분노", "화", "짜증", "적대", "anger"],
                "disgust": ["혐오", "거부", "불쾌", "disgust"],
                "fear": ["두려움", "불안", "걱정", "fear", "anxiety"],
                "happiness": ["기쁨", "즐거움", "행복", "희망", "happiness", "positive"],
                "sadness": ["슬픔", "우울", "상실", "sadness", "negative"],
                "surprise": ["놀라움", "신기", "호기심", "surprise"]
            }
            
            for emotion_name, keywords in emotion_keywords.items():
                if any(keyword in response_text.lower() for keyword in keywords):
                    emotion = emotion_name
                    confidence = 0.4
                    break
            
            return {
                "interpretation": response_text,
                "emotion": emotion,
                "emotion_confidence": confidence
            }
        except Exception as e:
            logger.error(f"응답 파싱 오류: {e}")
            return {
                "interpretation": f"응답 파싱 중 오류: {str(e)}",
                "emotion": "happiness",
                "emotion_confidence": 0.3
            }

# 전역 GPT 분석기 인스턴스
gpt_analyzer = GPTAnalyzer()
