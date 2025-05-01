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
        

    async def request(
        self,
        method: str,
        path: str,
        headers: Optional[list[tuple[bytes, bytes]]] = None,
        body: Optional[bytes] = None
    ) -> httpx.Response:
        logger.info(f"👩🏻👩🏻👩🏻👩🏻 BaseURL: {self.base_url}")
        print(f"🎯🎯🎯 ServiceType: {self.service_type.value}")
        print(f"🤗😚😐😫😛 Path: {path}")
        url = f"{self.base_url}/{self.service_type.value}/{path}"
        print(f"🎯🎯🎯 Requesting URL: {url}")
        
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