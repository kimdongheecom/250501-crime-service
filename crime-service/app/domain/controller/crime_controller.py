import logging

from app.domain.service.crime_preprocessor import CrimePreprocessor
from app.domain.service.crime_visualizer import CrimeVisualizer


logger = logging.getLogger(__name__)

class CrimeController:
    def __init__(self):
        self.preprocessor = CrimePreprocessor()
        self.visualizer = CrimeVisualizer()

    def preprocess(self, *args):
        """데이터 전처리를 수행"""
        self.preprocessor.preprocess(*args)
        return {"status": "preprocessing completed"}

    def draw_crime_map(self):
        """범죄 지도를 생성하는 함수"""
        result = self.visualizer.draw_crime_map()
        if result.get("status") == "범죄지도를 완성했습니다":
            logger.info(f"Crime map created at {result.get('file_path')}")
        else:
            logger.error("Failed to create crime map")
        return result

    def learning(self):  # 추후 확장 가능
        pass

    def evaluation(self):
        pass

    def deploy(self):
        pass
