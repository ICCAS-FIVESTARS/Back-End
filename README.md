## 백엔드 서버
FastAPI를 기반으로 구축되었으며, YOLOv8을 활용한 객체 탐지 기능도 포함된 백엔드 서버입니다. 

---

## 주요 기능

### 1. Object Detection
- 사용자 그림에서 YOLOv8을 이용해 `person`, `home`, `tree`, `cloud`, `rain` 등 특정 객체 탐지
- 감지된 객체의 **위치 및 크기** 정보를 기반으로 심리 해석 수행 
- 사용 모델: `htp.pt`, `pitr_yolov8.pt` 등 (미리 학습된 YOLOv8 모델)

### 2. 설명 텍스트 감정 분석
- 사용자가 입력한 그림 설명(텍스트)을 **KoBERT 기반 감정 분석기**로 분석
- 감정 결과가 부정적이거나 분석 불가한 경우 재입력 요구 가능 
- 파일: `sentiment_kobert.py`

### 3. 해석 모듈 
- YOLO로 감지한 객체 정보(위치/크기) 및 텍스트를 기반으로 GPT 기반 해석 진행
- 결과는 긍정적인 피드백 중심으로 반환/ DB에 저장 
- 파일: `gpt_interpreter.py`, `htp_interpreter.py`, `pitr_interpreter.py`

### 4. API 라우터 
- `app/api/analyze_router.py`: 통합 분석 API 라우팅
- 분석 종류에 따라 `htp_analyzer.py`, `pitr_analyzer.py`, `quest_analyzer.py` 로 처리

### 5. 테스트 코드
- 주요 기능별 테스트 코드 포함
    - `tests/test_analyze_http.py` : HTP 분석 테스트
    - `tests/test_analyze_pitr.py` : Rainperson 분석 테스트
    - `tests/test_yolo_detector.py` : 객체 탐지 테스트

---

```
Back-End/
├── app/
│ ├── api/
│ ├── core/
│ └── services/
│ ├── analyzers/
│ └── models/
├── assets/weights/ # YOLO 모델 가중치
├── tests/
├── main.py
├── requirements.txt
├── .gitignore
```
