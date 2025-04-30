from typing import Optional
from fastapi import HTTPException
import httpx
from app.domain.model.service_type import SERVICE_URLS, ServiceType
import logging

logger = logging.getLogger("gateway_api")

class ServiceProxyFactory:
    def __init__(self, service_type: ServiceType):
        self.service_type = service_type
        self.base_url = SERVICE_URLS[service_type]
        logger.info(f"👩🏻 Service URL: {self.base_url}")

    async def request(
        self,
        method: str,
        path: str,
        headers: Optional[list[tuple[bytes, bytes]]] = None,
        body: Optional[bytes] = None
    ) -> httpx.Response:
        # 서비스 URL이 없는 경우 오류 발생
        if not self.base_url:
            error_msg = f"Service URL for {self.service_type} is not configured"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

        # 기본 API 경로 구성
        if self.service_type == ServiceType.CRIME:
            # crime-service의 경우 라우터 접두사가 '/api/v1/crime'로 설정되어 있음
            if path.startswith("api/"):
                api_path = path
            else:
                api_path = f"api/v1/crime/{path}"
        elif self.service_type == ServiceType.TITANIC:
            if path.startswith("api/"):
                api_path = path
            else:
                api_path = f"api/v1/titanic/{path}"
        elif self.service_type == ServiceType.MATZIP:
            if path.startswith("api/"):
                api_path = path
            else:
                api_path = f"api/v1/matzip/{path}"
        else:
            api_path = path
            
        # 최종 URL 구성
        url = f"{self.base_url}/{api_path}"
        logger.info(f"🔄 Requesting URL: {url}")
        
        # 헤더 설정 (필요 시 외부 헤더 병합 가능)
        headers_dict = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers_dict,
                    content=body
                )
                logger.info(f"📊 Response status: {response.status_code}")
                if response.status_code >= 400:
                    logger.error(f"❌ Error response: {response.text}")
                return response
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Request failed: {error_msg}")
                raise HTTPException(status_code=500, detail=error_msg)