from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
import sys
import json
from gateway.app.domain.model.models import TitanicRequest, TitanicUpdateRequest

# ✅ 명시적 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("titanic_api")

# ✅ 라우터 생성
router = APIRouter()

# ✅ 요청 모델 정의
class TitanicRequest(BaseModel):
    data: List[Dict[str, Any]]

class TitanicUpdateRequest(BaseModel):
    passenger_id: int
    updates: Dict[str, Any]


# ✅ 상태 확인 엔드포인트
@router.get("/health", summary="Titanic 서비스 상태 확인")
async def health_check():
    logger.info("🩺 Health Check 호출")
    return {"status": "healthy"}

# ✅ GET API - 모든 승객 데이터 조회
@router.get("/passengers", summary="모든 승객 데이터 조회")
async def get_all_passengers():
    """
    저장된 모든 승객 데이터를 조회합니다.
    """
    logger.info("📋 모든 승객 데이터 조회")
    
    # 샘플 데이터
    passengers = [
        {
            "passenger_id": 1,
            "name": "John Doe",
            "age": 30,
            "sex": "male",
            "pclass": 1
        },
        {
            "passenger_id": 2,
            "name": "Jane Smith",
            "age": 25,
            "sex": "female",
            "pclass": 2
        },
        {
            "passenger_id": 3,
            "name": "Bob Johnson",
            "age": 45,
            "sex": "male",
            "pclass": 3
        }
    ]
    return {"passengers": passengers}

# ✅ POST /submit API
@router.post("/submit", summary="타이타닉 생존 예측")
async def predict_survival(payload: TitanicRequest):
    try:
        # 🔥 함수 진입 로깅
        logger.info("🔥 /submit 엔드포인트 호출됨")
        
        # 🔥 요청 데이터 로깅
        logger.info(f"요청 받은 데이터: {payload.data}")
        
        # ✅ 추후: 실제 예측 모델 호출 로직 구현
        # ex) predictor = TitanicPredictor() → 예측 수행
        
        # 임시 예측 결과
        predictions = []
        for passenger_data in payload.data:
            prediction = {
                "survived": True,  # 실제 모델 예측값으로 대체 필요
                "probability": 0.85,
                "passenger_data": passenger_data
            }
            predictions.append(prediction)
        
        # 🔥 함수 종료 로깅
        logger.info("✅ /submit 응답 준비 완료")
        
        return {
            "status": "success",
            "message": "타이타닉 생존 예측 완료",
            "predictions": predictions
        }
        
    except Exception as e:
        logger.error(f"❌ 예측 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ PUT API - 승객 데이터 전체 수정
@router.put("/passenger/{passenger_id}", summary="승객 정보 전체 수정")
async def update_passenger(passenger_id: int, request: Request):
    """
    승객 정보를 전체 수정합니다.
    """
    try:
        logger.info(f"📝 승객 ID {passenger_id}의 정보 전체 수정")
        data = await request.json()
        logger.info(f"수정 데이터: {data}")
        
        # 샘플 응답
        return {
            "status": "success",
            "message": f"승객 ID {passenger_id}의 정보가 성공적으로 수정되었습니다.",
            "updated_data": data
        }
    except Exception as e:
        logger.error(f"❌ 승객 정보 수정 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ DELETE API - 승객 데이터 삭제
@router.delete("/passenger/{passenger_id}", summary="승객 정보 삭제")
async def delete_passenger(passenger_id: int):
    """
    승객 정보를 삭제합니다.
    """
    try:
        logger.info(f"🗑️ 승객 ID {passenger_id} 정보 삭제")
        
        # 샘플 응답
        return {
            "status": "success",
            "message": f"승객 ID {passenger_id}의 정보가 성공적으로 삭제되었습니다."
        }
    except Exception as e:
        logger.error(f"❌ 승객 정보 삭제 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ PATCH API - 승객 데이터 부분 수정
@router.patch("/passenger/{passenger_id}", summary="승객 정보 부분 수정")
async def patch_passenger(passenger_id: int, update_data: TitanicUpdateRequest):
    """
    승객 정보를 부분적으로 수정합니다.
    """
    try:
        logger.info(f"✏️ 승객 ID {passenger_id}의 정보 부분 수정")
        logger.info(f"수정할 필드: {update_data.updates}")
        
        # 샘플 응답
        return {
            "status": "success",
            "message": f"승객 ID {passenger_id}의 정보가 부분적으로 수정되었습니다.",
            "updated_fields": update_data.updates
        }
    except Exception as e:
        logger.error(f"❌ 승객 정보 부분 수정 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 