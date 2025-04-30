import numpy as np
import pandas as pd
from app.domain.model.data_schema import DataSchema

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier


# 머신러닝 관련 import
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, train_test_split, cross_val_score
from sklearn.metrics import accuracy_score

class TitanicService:
    dataschema = DataSchema()

    # 모델 생성
    def new_model(self, fname) -> object:
        this = self.dataschema
        this.context = 'C:\\Users\\bitcamp\\Documents\\kpmg-250424\\kpmg2501\\V2\\ai-server\\titanic-service\\app\\domain\\stored_data\\'
        this.fname = fname
        return pd.read_csv(this.context + this.fname)

    # 데이터 전처리
    def preprocess(self, train_fname, test_fname) -> object:
        print("--------- 모델 전처리 시작 ----------")
        feature = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 
                   'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked']
        this = self.dataschema
        this.train = self.new_model(train_fname)
        this.test = self.new_model(test_fname)
        this.id = this.test['PassengerId']
        this.label = this.train['Survived']
        this.train = this.train.drop('Survived', axis=1)

        # 특성 엔지니어링
        this = self.extract_title_from_name(this)
        title_mapping = self.remove_duplicate_title(this)
        this = self.title_nominal(this, title_mapping)
        this = self.gender_nominal(this)
        this = self.embarked_nominal(this)
        this = self.age_ratio(this)
        this = self.fare_ordinal(this)

        # FamilySize 추가
        for df in [this.train, this.test]:
            df['FamilySize'] = df['SibSp'] + df['Parch'] + 1

        # 필요 없는 특성 제거
        this = self.drop_feature(this, 'Name', 'Sex', 'Age', 'Fare', 'SibSp', 'Parch', 'Cabin', 'Ticket')

        print("😚☺🙂🤗 전처리 완료")
        return this

    # K-Fold 교차 검증
    def create_k_fold(self):
        this = self.dataschema
        numeric_cols = ['Pclass', 'Gender', 'AgeGroup', 'FareGroup', 'Embarked', 'FamilySize']
        X = this.train[numeric_cols]
        y = this.label

        kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
        model = RandomForestClassifier(random_state=42)
        scores = cross_val_score(model, X, y, cv=kf)
        print(f"😎🧐🤓 K-Fold 교차 검증 결과: 평균={scores.mean():.4f}, 표준편차={scores.std():.4f}")
        return scores

    # 랜덤 피처 추가 (선택)
    def create_random_variable(self):
        this = self.dataschema
        np.random.seed(42)
        this.train['RandomFeature'] = np.random.randn(len(this.train))
        this.test['RandomFeature'] = np.random.randn(len(this.test))
        print("🎲 랜덤 피처(RandomFeature) 추가 완료")
        return this

    # 학습
    def learning(self):
        print("----- 학습 시작 -----")
        this = self.dataschema
        numeric_cols = ['Pclass', 'Gender', 'AgeGroup', 'FareGroup', 'Embarked', 'FamilySize']
        X = this.train[numeric_cols]
        y = this.label

        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        scores = cross_val_score(model, X, y, cv=5)
        print(f"📚 K-Fold 정확도 평균: {scores.mean():.4f}, 표준편차: {scores.std():.4f}")

        model.fit(X, y)

        this.model = model
        this.feature_columns = numeric_cols
        print("----- 학습 완료 -----")
        return this

    # 평가
    def evaluation(self):
        print("----- 평가 시작 -----")
        this = self.dataschema
        if not hasattr(this, 'model'):
            print("❗ 모델이 학습되지 않았습니다. 먼저 learning() 메소드를 호출하세요.")
            return None

        dtree_acc = self.accuracy_by_dtree()
        rf_acc = self.accuracy_by_random_forest()
        nb_acc = self.accuracy_by_naive_bayes()
        knn_acc = self.accuracy_by_knn()
        svm_acc = self.accuracy_by_svm()
        xgb_acc = self.accuracy_by_xgboost()        # 🔥 추가
        lgbm_acc = self.accuracy_by_lightgbm()      # 🔥 추가

        results = {
            "decision_tree": dtree_acc,
            "random_forest": rf_acc,
            "naive_bayes": nb_acc,
            "knn": knn_acc,
            "svm": svm_acc,
            "xgboost": xgb_acc,                     # 🔥 추가
            "lightgbm": lgbm_acc                     # 🔥 추가
        }

        print("----- 평가 완료 -----")
        return results


    # 제출
    def submit(self):
        print("----- 제출 시작 -----")
        this = self.dataschema
        if not hasattr(this, 'model'):
            print("❗ 모델이 학습되지 않았습니다. 먼저 learning() 메소드를 호출하세요.")
            return None

        X_test = this.test[this.feature_columns]
        predictions = this.model.predict(X_test)

        submission = pd.DataFrame({
            'PassengerId': this.id,
            'Survived': predictions
        })

        submission_path = this.context + 'submission.csv'
        submission.to_csv(submission_path, index=False)
        print(f"📤 제출 파일 저장 완료: {submission_path}")
        print("----- 제출 완료 -----")
        return submission

    # 공통 학습 + 평가 함수
    def _train_and_evaluate(self, model):
        this = self.dataschema
        numeric_cols = ['Pclass', 'Gender', 'AgeGroup', 'FareGroup', 'Embarked', 'FamilySize']
        X = this.train[numeric_cols]
        y = this.label
        
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)
        acc = accuracy_score(y_val, y_pred)
        print(f"✅ 검증 정확도: {acc:.4f}")
        return acc

    # 개별 알고리즘 정확도 비교
    def accuracy_by_dtree(self):
        print("🌲 DecisionTreeClassifier")
        return self._train_and_evaluate(DecisionTreeClassifier())

    def accuracy_by_random_forest(self):
        print("🌳 RandomForestClassifier")
        return self._train_and_evaluate(RandomForestClassifier())

    def accuracy_by_naive_bayes(self):
        print("🧠 NaiveBayes (GaussianNB)")
        return self._train_and_evaluate(GaussianNB())

    def accuracy_by_knn(self):
        print("👣 K-Nearest Neighbors")
        return self._train_and_evaluate(KNeighborsClassifier())

    def accuracy_by_svm(self):
        print("💫 Support Vector Machine")
        return self._train_and_evaluate(SVC(probability=True))
    
    # XGBoost 정확도 비교
    def accuracy_by_xgboost(self):
        print("🚀 XGBoostClassifier")
        return self._train_and_evaluate(
            XGBClassifier(random_state=42)
        )

    # LightGBM 정확도 비교
    def accuracy_by_lightgbm(self):
        print("🌟 LightGBMClassifier")
        return self._train_and_evaluate(
            LGBMClassifier(random_state=42)
        )


    # 전처리 유틸리티 함수들
    @staticmethod
    def drop_feature(this, *features) -> object:
        for feature in features:
            for df in [this.train, this.test]:
                df.drop(columns=feature, inplace=True)
        return this

    @staticmethod
    def extract_title_from_name(this):
        for df in [this.train, this.test]:
            df['Title'] = df['Name'].str.extract('([A-Za-z]+)\\.', expand=False)
        return this

    @staticmethod
    def remove_duplicate_title(this):
        titles = pd.concat([this.train['Title'], this.test['Title']]).unique()
        title_mapping = {'Mr': 1, 'Ms': 2, 'Mrs': 3, 'Master': 4, 'Royal': 5, 'Rare': 6}
        return title_mapping

    @staticmethod
    def title_nominal(this, title_mapping):
        for df in [this.train, this.test]:
            df['Title'] = df['Title'].replace(['Countess', 'Lady', 'Sir'], 'Royal')
            df['Title'] = df['Title'].replace(['Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Jonkheer', 'Dona', 'Mme'], 'Rare')
            df['Title'] = df['Title'].replace(['Mlle'], 'Mr')
            df['Title'] = df['Title'].replace(['Miss'], 'Ms')
            df['Title'] = df['Title'].map(title_mapping)
            df['Title'] = df['Title'].fillna(0)
        return this

    @staticmethod
    def gender_nominal(this):
        gender_mapping = {'male': 1, 'female': 2}
        for df in [this.train, this.test]:
            df['Gender'] = df['Sex'].map(gender_mapping)
        return this

    @staticmethod
    def embarked_nominal(this):
        embarked_mapping = {'S': 1, 'C': 2, 'Q': 3}
        for df in [this.train, this.test]:
            df['Embarked'].fillna('S', inplace=True)
            df['Embarked'] = df['Embarked'].map(embarked_mapping)
        return this

    @staticmethod
    def age_ratio(this):
        # 나이 결측치 처리
        for df in [this.train, this.test]:
            df['Age'].fillna(df['Age'].mean(), inplace=True)
            
        # 나이 구간과 매핑
        def map_age_to_group(age):
            if age <= 0:
                return 0  # Unknown
            elif age <= 5:
                return 1  # Baby
            elif age <= 12:
                return 2  # Child
            elif age <= 18:
                return 3  # Teenager
            elif age <= 24:
                return 4  # Student
            elif age <= 35:
                return 5  # Young Adult
            elif age <= 60:
                return 6  # Adult
            else:
                return 7  # Senior
        
        # apply 메서드로 값 배정
        for df in [this.train, this.test]:
            df['AgeGroup'] = df['Age'].apply(map_age_to_group)
            
        return this

    @staticmethod
    def fare_ordinal(this):
        # 요금 결측치 처리
        for df in [this.train, this.test]:
            df['Fare'].fillna(df['Fare'].mean(), inplace=True)
            
        # 요금 구간과 매핑
        def map_fare_to_group(fare):
            if fare <= 128.0823:
                return 1  # Low
            elif fare <= 256.1646:
                return 2  # Medium-Low
            elif fare <= 384.2469:
                return 3  # Medium-High
            else:
                return 4  # High
        
        # apply 메서드로 값 배정
        for df in [this.train, this.test]:
            df['FareGroup'] = df['Fare'].apply(map_fare_to_group)
            
        return this
