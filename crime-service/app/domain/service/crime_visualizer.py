# 데이터 시각화 작업을 위한 클래스
import logging
import traceback
from fastapi import HTTPException
from app.domain.service.internal.crime_map_create import CrimeMapCreator

logger = logging.getLogger("crime_service")

class CrimeVisualizer:
    def draw_crime_map(self) -> dict:
        try:
            map_creator = CrimeMapCreator()
            map_file_path = map_creator.create_map()
            return {"status": "범죄지도를 완성했습니다", "file_path": map_file_path}
        except HTTPException as e:
            logger.error(f"지도 생성 실패 (HTTPException): {e.status_code} - {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"지도 생성 중 예상치 못한 오류 발생: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"지도 생성 중 예상치 못한 서버 오류: {type(e).__name__}")
