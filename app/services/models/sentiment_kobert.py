# services/models/sentiment_kobert.py

from transformers import pipeline
from typing import Literal
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 감정 분석 모델: KoBERT / KcELECTRA 
sentiment_model = pipeline(
    "sentiment-analysis",
    model="beomi/KcELECTRA-base",
    tokenizer="beomi/KcELECTRA-base",
    device=0 if DEVICE == "cuda" else -1
)

def analyze_sentiment(text: str) -> Literal['positive', 'negative', 'neutral']:
    """
    텍스트 감정 분석 결과 반환
    :param text: 사용자 입력 설명
    :return: 감정 라벨
    """
    if not text.strip():
        return "neutral"

    try:
        result = sentiment_model(text)
        label = result[0]['label'].lower()  # 예: 'positive', 'negative'
        if "pos" in label:
            return "positive"
        elif "neg" in label:
            return "negative"
        else:
            return "neutral"
    except Exception as e:
        print(f"[ERROR] 감정 분석 실패: {e}")
        return "neutral"

# if __name__ == '__main__':
#     print(analyze_sentiment("이 그림은 행복하고 만족스러워요."))
#     print(analyze_sentiment("기분이 너무 우울하고 불안해요."))
