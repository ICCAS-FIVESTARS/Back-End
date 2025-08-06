# services/models/model_loader.py
"""
.pt 모델 로딩 및 관리 모듈
HTP, PITR Object Detection 모델을 효율적으로 로딩하고 캐싱
"""

import os
import torch
from typing import Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    """Object Detection 모델 로더 및 캐시 관리"""
    
    def __init__(self, weights_dir: str = "assets/weights"):
        self.weights_dir = Path(weights_dir)
        self._models: Dict[str, torch.nn.Module] = {}
        self._model_paths = {
            'htp': self.weights_dir / 'htp.pt',
            'pitr': self.weights_dir / 'pitr_yolov8.pt'
        }
        
    def load_model(self, model_name: str) -> Optional[torch.nn.Module]:
        """
        모델 로딩 (캐싱 지원)
        
        Args:
            model_name: 'htp' 또는 'pitr'
            
        Returns:
            로딩된 모델 객체 또는 None
        """
        if model_name in self._models:
            logger.info(f"✅ {model_name} 모델 캐시에서 로딩")
            return self._models[model_name]
            
        model_path = self._model_paths.get(model_name)
        if not model_path or not model_path.exists():
            logger.error(f"{model_name} 모델 파일 없음: {model_path}")
            return None
            
        try:
            logger.info(f"{model_name} 모델 로딩 중: {model_path}")
            
            # YOLO 모델 로딩
            if model_name == 'pitr':
                from ultralytics import YOLO
                model = YOLO(str(model_path))
            else:  # htp
                # PyTorch 모델 로딩
                model = torch.load(str(model_path), map_location='cpu')
                
            self._models[model_name] = model
            logger.info(f"{model_name} 모델 로딩 완료")
            return model
            
        except Exception as e:
            logger.error(f"{model_name} 모델 로딩 실패: {e}")
            return None
            
    def get_model_info(self, model_name: str) -> Dict:
        """모델 정보 반환"""
        model_path = self._model_paths.get(model_name)
        return {
            'name': model_name,
            'path': str(model_path) if model_path else None,
            'exists': model_path.exists() if model_path else False,
            'loaded': model_name in self._models,
            'type': 'YOLO' if model_name == 'pitr' else 'PyTorch'
        }
        
    def clear_cache(self):
        """모델 캐시 초기화"""
        self._models.clear()
        logger.info("모델 캐시 초기화 완료")

# 전역 모델 로더 인스턴스
model_loader = ModelLoader()
