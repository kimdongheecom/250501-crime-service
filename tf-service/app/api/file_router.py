from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
import tensorflow as tf
from app.domain.service.calculator import Calculator

router = APIRouter()

# Calculator 인스턴스 생성
calculator = Calculator()

# 파일 업로드 디렉토리 설정
UPLOAD_DIR = "app/uploads"  # app 내부의 uploads 폴더
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== 파일 관련 엔드포인트 ==========

@router.get("/info", summary="파일 정보")
async def file_info():
    return JSONResponse(content={
        "message": "✅ 파일 서비스 작동 중!",
        "upload_dir": UPLOAD_DIR
    })

@router.post("/upload", summary="파일 업로드")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return JSONResponse(content={
        "filename": file.filename,
        "message": "✅ 파일 업로드 성공!"
    })

# ========== 계산기 관련 엔드포인트 ==========

# 기본 경로
@router.get("/calc", summary="계산기 API 시작점")
async def calculator_root():
    return {"message": "Calculator API"}

# 덧셈 연산
@router.get("/calc/add/{num1}/{num2}", summary="두 숫자를 더합니다")
async def add(num1: int, num2: int):
    result = calculator.plus(tf.constant(num1), tf.constant(num2))
    return {"result": float(result.numpy())}

# 뺄셈 연산
@router.get("/calc/subtract/{num1}/{num2}", summary="첫번째 숫자에서 두번째 숫자를 뺍니다")
async def subtract(num1: int, num2: int):
    result = calculator.minus(tf.constant(num1), tf.constant(num2))
    return {"result": float(result.numpy())}

# 곱셈 연산
@router.get("/calc/multiply/{num1}/{num2}", summary="두 숫자를 곱합니다")
async def multiply(num1: int, num2: int):
    result = calculator.multiple(tf.constant(num1), tf.constant(num2))
    return {"result": float(result.numpy())}

# 나눗셈 연산
@router.get("/calc/divide/{num1}/{num2}", summary="첫번째 숫자를 두번째 숫자로 나눕니다")
async def divide(num1: int, num2: int):
    result = calculator.div(tf.constant(num1), tf.constant(num2))
    return {"result": float(result.numpy())}

# MNIST 샘플 실행
@router.get("/calc/run-sample", summary="MNIST 샘플 모델을 실행합니다")
async def run_sample():
    calculator.sample()
    return {"message": "Sample run completed"}
