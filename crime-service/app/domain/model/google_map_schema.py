import os
import googlemaps


class GoogleMapSchema:
    _instance = None  # 싱글턴 인스턴스를 저장할 클래스 변수

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GoogleMapSchema, cls).__new__(cls)
            cls._instance._api_key = cls._instance._retrieve_api_key()
            cls._instance._client = googlemaps.Client(key=cls._instance._api_key)
        return cls._instance

    def _retrieve_api_key(self) -> str:
        """
        Google Maps API 키를 안전하게 불러오는 메서드
        환경변수 GOOGLE_API_KEY 또는 .env 파일에서 가져옴
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ 환경변수 'GOOGLE_API_KEY'가 설정되지 않았습니다.")
        return api_key

    def get_api_key(self) -> str:
        """API 키 반환"""
        return self._api_key

    def geocode(self, address: str, language: str = 'ko') -> dict:
        """주소를 위도·경도로 변환"""
        return self._client.geocode(address, language=language)


class ApiKeyManager(GoogleMapSchema):
    """
    기존 코드 호환성을 위한 별칭 클래스
    예: gmaps = ApiKeyManager()
    """
    pass
