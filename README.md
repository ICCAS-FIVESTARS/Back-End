AI 기반 미술 심리분석 플랫폼의 백엔드 서버입니다.  
FastAPI + HuggingFace (추후 수정) 모델 기반으로, HTP, Rainperson, 일반 미션(Quest) 분석을 지원. 

---

## 주요 기능

- **그림 분석 (Object Detection)**  
  TBD

- **설명 텍스트 감정 분석**  
  KoBERT 기반 분석
  잘못된 입력 받을 시 재입력 요구

- **해석 모듈**  
  LLM 기반 심리 분석 (gpt_interpreter.py)

- **테스트용 코드**  
  `tests/test_analyze_htp.py`, `test_analyze_pitr.py`

---