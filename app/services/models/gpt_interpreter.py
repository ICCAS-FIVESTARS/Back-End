# gpt_interpreter
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_gpt_interpretation(
    prompt: str,
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = 200
) -> dict:
    """
    GPT 해석 요청. 해석 결과와 감정(가능시) 반환.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "너는 따뜻한 미술치료 해석가야. 사용자의 심리상태와 감정도 요약해줘."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        content = response.choices[0].message.content
        
        # 감정 추출(예시: '감정: 긍정' 등 프롬프트에서 분리)
        sentiment = "중립"
        if "감정:" in content:
            try:
                sentiment = content.split("감정:")[1].split()[0].strip()
            except Exception:
                pass
        
        return {
            "interpretation": content,
            "sentiment": sentiment
        }
    except Exception as e:
        return {
            "interpretation": f"GPT 해석 실패: {e}",
            "sentiment": "중립"
        }