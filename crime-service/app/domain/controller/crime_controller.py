
from app.domain.service.crime_service import CrimeService
from app.domain.model.crime_schema import CrimeSchema
class CrimeController:
    def __init__(self):
        self.schema = CrimeSchema()
        self.service = CrimeService()

    def preprocess(self, *args):
        this = self.service.preprocess(*args)
     
        return this
    
    def correlation(self): #상관계수 분석
        print("Controller: Calling correlation_service.load_and_analyze...")
        results = self.correlation_service.load_and_analyze()
        print("Controller: Correlation analysis completed")
        return results
    
    def get_correlation_results(self):
        """상관계수 분석 결과를 반환하는 함수"""
        return self.correlation()

    def draw_crime_map(self):
        # 데이터 불러오기 전제: 기존 전처리된 객체를 사용해야 함
        """범죄 지도를 생성하는 함수"""
        print("Controller: Calling service.draw_crime_map...")
        result = self.service.draw_crime_map()
        if result.get("status") == "success":
            print(f"Controller: Crime map created successfully at {result.get('file_path')}")
        else:
            print(f"Controller: Failed to create crime map - {result.get('message')}")
        return result
    
    def learning(self): #모델 학습
        pass

    def evaluation(self): #모델 평가
        pass

    def deploy(self): #모델 배포
        pass
    

   
