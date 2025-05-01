from fastapi import APIRouter, Request
import logging
from app.domain.controller.crime_controller import CrimeController
from fastapi import Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
import os
from fastapi.responses import HTMLResponse

# 로거 설정
logger = logging.getLogger("crime_router")
logger.setLevel(logging.INFO)
router = APIRouter()

# GET
@router.get("/preprocess", summary="범죄상세")
async def preprocess():
    controller = CrimeController()
    controller.preprocess('cctv_in_seoul.csv', 'crime_in_seoul.csv', 'pop_in_seoul.xls')
    return {"message": '서울시의 범죄 데이터가 전처리 되었습니다.'}

@router.get("/map", summary="범죄지도 그리기", response_class=HTMLResponse)
async def draw_crime_map():
    controller = CrimeController()
    result = controller.draw_crime_map()
    
    # HTML 파일 읽어오기
    if result.get("status") == "범죄지도를 완성했습니다" and "file_path" in result:
        try:
            with open(result["file_path"], "r", encoding="utf-8") as f:
                html_content = f.read()
            return html_content
        except Exception as e:
            logger.error(f"HTML 파일 읽기 실패: {e}")
            return {"message": '지도 파일을 읽는데 실패했습니다.'}
    
    return {"message": '서울시의 범죄 지도가 완성되었습니다만, 표시할 수 없습니다.'}