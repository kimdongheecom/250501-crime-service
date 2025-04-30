from app.domain.controller.matzip_controller import MatZipController

def main():
    controller = MatZipController()
    
    # matzip.csv 파일을 사용하여 맛집 모델링 수행
    matzip_fname = 'matzip.csv'
    result = controller.modelling(matzip_fname)
    
    print("🥘 맛집 모델링 완료 🥘",result)

if __name__ == "__main__":
    main()
