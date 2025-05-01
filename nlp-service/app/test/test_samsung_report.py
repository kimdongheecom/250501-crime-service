import os
import sys
import pytest
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from httpx import AsyncClient
import logging
import uvicorn
from app.domain.service.samsung_report import SamsungReport

# 현재 경로 출력
print(f"현재 디렉토리: {os.getcwd()}")
print(f"현재 Python 경로: {sys.path}")



# 앱 디렉토리를 경로에 추가
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.append(current_dir)
    print(f"추가된 경로: {current_dir}")

try:
    from app.domain.service.samsung_report import SamsungReport
    print("SamsungReport 클래스를 성공적으로 가져왔습니다.")
except ImportError as e:
    print(f"SamsungReport 클래스 가져오기 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("nlp_service_test")

# FastAPI 앱 생성
app = FastAPI(
    title="Samsung Report NLP Test Service",
    description="삼성 리포트 분석 테스트를 위한 NLP 서비스 API",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 생성
router = APIRouter(tags=["Test"])

@router.get("/test", summary="테스트 엔드포인트")
async def test_endpoint():
    """
    테스트 엔드포인트입니다.
    
    Returns:
        dict: "테스트용 파일입니다." 메시지를 포함한 응답
    """
    logger.info("테스트 엔드포인트가 호출되었습니다.")
    return {"message": "테스트용 파일입니다."}

@router.get("/wordcloud", summary="워드클라우드 생성")
async def create_wordcloud():
    """
    삼성 보고서 텍스트를 분석하여 워드클라우드를 생성합니다.
    
    Returns:
        FileResponse: 생성된 워드클라우드 이미지 파일
    """
    logger.info("워드클라우드 생성 엔드포인트가 호출되었습니다.")
    
    try:
        # SamsungReport 클래스 인스턴스 생성
        report = SamsungReport()
        logger.info(f"SamsungReport 인스턴스 생성 성공, 파일 경로: {report.file_path}")
        
        # 워드클라우드 생성 프로세스 실행
        result = report.process_report()
        logger.info(f"워드클라우드 생성 결과: {result}")
        
        # 출력 파일 경로 확인
        output_file = os.path.join(report.output_path, 'wordcloud.png')
        logger.info(f"출력 파일 경로: {output_file}, 존재 여부: {os.path.exists(output_file)}")
        
        if os.path.exists(output_file):
            return FileResponse(output_file, media_type="image/png")
        else:
            return JSONResponse(
                status_code=404,
                content={"message": "워드클라우드 생성에 실패했습니다.", "detail": result}
            )
    except Exception as e:
        logger.error(f"워드클라우드 생성 중 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"message": "서버 오류가 발생했습니다.", "detail": str(e)}
        )

# 라우터 등록
app.include_router(router)

# 테스트를 위한 픽스처 정의
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# 테스트 코드
@pytest.mark.asyncio
async def test_read_test(async_client):
    """테스트 엔드포인트 테스트 - 비동기 방식"""
    response = await async_client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "테스트용 파일입니다."}

# 서버 실행
if __name__ == "__main__":
    port = int(os.getenv("PORT", 7000))
    uvicorn.run("app.test.test_samsung_report:app", host="0.0.0.0", port=port, reload=True)

