from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from pydantic import BaseModel
import pandas as pd
import numpy as np
from datetime import datetime
from app.domain.controller.crime_controller import CrimeController

# 로거 설정
logger = logging.getLogger("crime_service")

# 라우터 설정
router = APIRouter(
    prefix="/api/v1/crime",
    tags=["crime"],
    responses={404: {"description": "Not found"}},
)

# 요청 모델
class CrimePredictionRequest(BaseModel):
    district: str  # 지역구
    date: str  # 예측하고자 하는 날짜 (YYYY-MM-DD)
    crime_type: str  # 범죄 유형

# 응답 모델
class CrimePredictionResponse(BaseModel):
    district: str
    date: str
    crime_type: str
    prediction: float
    risk_level: str
    additional_info: Dict[str, Any]

@router.post("/predict", response_model=CrimePredictionResponse)
async def predict_crime(request: CrimePredictionRequest):
    try:
        # 입력 데이터 검증
        if not request.district or not request.date or not request.crime_type:
            raise HTTPException(status_code=400, detail="모든 필드를 입력해주세요.")

        # 날짜 형식 검증
        try:
            prediction_date = datetime.strptime(request.date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)")

        # TODO: 실제 예측 모델 구현
        # 임시 예측 로직 (실제 구현 시 머신러닝 모델로 대체)
        mock_prediction = np.random.uniform(0, 1)
        
        # 위험도 레벨 결정
        risk_level = "낮음"
        if mock_prediction > 0.7:
            risk_level = "높음"
        elif mock_prediction > 0.4:
            risk_level = "중간"

        # 응답 생성
        response = CrimePredictionResponse(
            district=request.district,
            date=request.date,
            crime_type=request.crime_type,
            prediction=float(mock_prediction),
            risk_level=risk_level,
            additional_info={
                "confidence_score": float(np.random.uniform(0.6, 0.9)),
                "historical_data": {
                    "last_month_incidents": int(np.random.randint(0, 100)),
                    "avg_monthly_incidents": float(np.random.uniform(20, 80))
                }
            }
        )

        logger.info(f"😂😀😁😊범죄 예측 완료: {request.district}, {request.date}, {request.crime_type}")
        return response

    except Exception as e:
        logger.error(f"예측 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/districts", response_model=List[str])
async def get_districts():
    """사용 가능한 지역구 목록을 반환합니다."""
    # TODO: 실제 데이터베이스에서 지역구 목록을 가져오도록 수정
    districts = [
        "강남구", "강동구", "강북구", "강서구", "관악구",
        "광진구", "구로구", "금천구", "노원구", "도봉구",
        "동대문구", "동작구", "마포구", "서대문구", "서초구",
        "성동구", "성북구", "송파구", "양천구", "영등포구",
        "용산구", "은평구", "종로구", "중구", "중랑구"
    ]

    controller = CrimeController()
    result= controller.preprocess()
    return result

@router.get("/crime-types", response_model=List[str])
async def get_crime_types():
    """사용 가능한 범죄 유형 목록을 반환합니다."""
    # TODO: 실제 데이터베이스에서 범죄 유형 목록을 가져오도록 수정
    crime_types = [
        "절도", "폭력", "강도", "살인", "강간·강제추행",
        "방화", "마약", "사기", "횡령", "배임",
        "교통사고", "기타"
    ]
    return crime_types 
