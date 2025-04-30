# 수정된 titanic_controller.py

from app.domain.service.titanic_service import TitanicService


# print(f'결정트리 활용한 검증 정확도 {None}')
# print(f'랜덤포레스트 활용한 검증 정확도 {None}')
# print(f'나이브베이즈 활용한 검증 정확도 {None}')
# print(f'KNN 활용한 검증 정확도 {None}')
# print(f'SVM 활용한 검증 정확도 {None}')




class TitanicController:
    def __init__(self):
        self.service = TitanicService()

    # 데이터 전처리 수행
    def preprocess(self, train, test):
        return self.service.preprocess(train, test)

    # K-Fold 교차 검증 수행
    def create_k_fold(self):
        return self.service.create_k_fold()

    # 모델 학습 수행
    def learning(self):
        return self.service.learning()

    # 모델 평가 수행
    def evaluation(self):
        return self.service.evaluation()

    # 제출 파일 생성
    def submit(self):
        return self.service.submit()

    