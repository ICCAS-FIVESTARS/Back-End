#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API 테스트 스크립트
"""

import requests
import json
import os
from pathlib import Path

# 서버 URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """서버 상태 확인"""
    print("🔍 서버 상태 확인 중...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ 서버 응답: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

def test_image_analysis(image_path, analysis_type="htp"):
    """이미지 분석 테스트"""
    print(f"\n🖼️  이미지 분석 테스트: {image_path}")
    print(f"📊 분석 타입: {analysis_type}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            
            # 각 분석 타입별로 다른 엔드포인트와 데이터 사용
            if analysis_type == "quest":
                data = {
                    'stage': 1,  # Quest는 stage 번호가 필요
                    'description': '테스트 그림입니다. 기본적인 그림을 그렸습니다.'
                }
                endpoint = f"{BASE_URL}/api/analyze/quest"
            else:
                data = {'description': '테스트 그림입니다.'}
                endpoint = f"{BASE_URL}/api/analyze/{analysis_type}"
            
            response = requests.post(
                endpoint, 
                files=files, 
                data=data
            )
            
        if response.status_code == 200:
            result = response.json()
            print("✅ 분석 성공!")
            print(f"📋 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        else:
            print(f"❌ 분석 실패: {response.status_code}")
            print(f"오류 내용: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 요청 중 오류: {e}")
        return None

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🚀 Drawing Analysis API 테스트 시작")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    if not test_health_check():
        print("서버가 실행되지 않았습니다. start_server.bat을 먼저 실행해주세요.")
        return
    
    # 2. 테스트 이미지 폴더 확인
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print("❌ uploads 폴더를 찾을 수 없습니다.")
        return
    
    # 3. 이미지 파일들 찾기
    image_files = list(uploads_dir.glob("*.png")) + list(uploads_dir.glob("*.jpg"))
    
    if not image_files:
        print("❌ 테스트할 이미지가 없습니다.")
        return
    
    print(f"\n📁 발견된 이미지 파일: {len(image_files)}개")
    
    # 4. 각 분석 타입별로 테스트
    analysis_types = ["htp", "pitr", "quest"]
    
    for i, image_file in enumerate(image_files[:2]):  # 처음 2개만 테스트
        print(f"\n{'='*30} 이미지 {i+1} {'='*30}")
        print(f"파일: {image_file.name}")
        
        for analysis_type in analysis_types:
            test_image_analysis(str(image_file), analysis_type)
            print("-" * 40)
    
    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    main()
