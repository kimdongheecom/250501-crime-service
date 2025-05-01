from konlpy.tag import Okt
from nltk.tokenize import word_tokenize
import nltk
import re
import pandas as pd
from nltk import FreqDist
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from icecream import ic
import os
import matplotlib.font_manager as fm
from collections import Counter
import sys
import platform

# NLTK 사용 가능 여부 설정
nltk_available = True

class SamsungReport:
    def __init__(self):
        # Adoptium JDK 환경 설정
        self._setup_java_env()
        
        try:
            self.okt = Okt()
            self.use_okt = True
            print("Okt 초기화 성공!")
        except Exception as e:
            print(f"Okt 초기화 실패: {e}")
            print("Okt 대신 정규식 기반 명사 추출을 사용합니다.")
            self.use_okt = False
        
        self.file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'original', 'kr-Report_2018.txt')
        self.stopwords_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'original', 'stopwords.txt')
        self.output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output')
        
        print(f"파일 경로: {self.file_path}")
        print(f"불용어 경로: {self.stopwords_path}")
        print(f"출력 경로: {self.output_path}")
        
        # 출력 디렉토리가 없으면 생성
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            print(f"출력 디렉토리 생성됨: {self.output_path}")
            
        # NLTK 데이터 다운로드 (필요시)
        if nltk_available:
            try:
                nltk.data.find('tokenizers/punkt')
                print("NLTK punkt 토크나이저가 이미 설치되어 있습니다.")
            except LookupError:
                try:
                    print("NLTK punkt 토크나이저 다운로드 중...")
                    nltk.download('punkt')
                    print("NLTK punkt 토크나이저 다운로드 완료")
                except Exception as e:
                    print(f"⚠️ NLTK 데이터 다운로드 실패: {e}")
        else:
            print("NLTK를 사용할 수 없어 토크나이저 다운로드를 건너뜁니다.")

    def _setup_java_env(self):
        """Adoptium JDK 환경 설정을 확인하고 필요시 설정합니다."""
        print("Java 환경 설정 확인 중...")
        
        # 현재 JAVA_HOME 환경변수 확인
        java_home = os.environ.get('JAVA_HOME')
        print(f"현재 JAVA_HOME: {java_home}")
        
        # 시스템 확인
        system = platform.system()
        print(f"운영 체제: {system}")
        
        # Adoptium 설치 경로 추정
        adoptium_paths = []
        
        if system == 'Windows':
            # Windows의 일반적인 Adoptium 설치 경로
            program_files = [
                "C:\\Program Files\\Eclipse Adoptium",
                "C:\\Program Files\\Eclipse Foundation", 
                "C:\\Program Files\\Java"
            ]
            
            for base_path in program_files:
                if os.path.exists(base_path):
                    # 디렉토리 목록 가져오기
                    try:
                        for item in os.listdir(base_path):
                            if item.startswith('jdk'):
                                full_path = os.path.join(base_path, item)
                                adoptium_paths.append(full_path)
                    except:
                        pass
        
        elif system == 'Darwin':  # macOS
            # macOS의 일반적인 Adoptium 설치 경로
            adoptium_paths = [
                "/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home",
                "/Library/Java/JavaVirtualMachines/temurin-11.jdk/Contents/Home"
            ]
        
        elif system == 'Linux':
            # Linux의 일반적인 Adoptium 설치 경로
            adoptium_paths = [
                "/usr/lib/jvm/temurin-17-jdk",
                "/usr/lib/jvm/temurin-11-jdk"
            ]
        
        # JAVA_HOME이 설정되지 않았거나 잘못된 경로라면 자동 설정 시도
        if not java_home or not os.path.exists(java_home):
            print("JAVA_HOME이 설정되지 않았거나 잘못된 경로입니다. 자동 설정을 시도합니다.")
            
            # Adoptium 경로 확인 및 설정
            for path in adoptium_paths:
                if os.path.exists(path):
                    print(f"Adoptium JDK 발견: {path}")
                    os.environ['JAVA_HOME'] = path
                    if system == 'Windows':
                        os.environ['PATH'] = f"{path}\\bin;{os.environ.get('PATH', '')}"
                    else:
                        os.environ['PATH'] = f"{path}/bin:{os.environ.get('PATH', '')}"
                    print(f"JAVA_HOME 환경변수가 설정되었습니다: {path}")
                    break
            else:
                print("자동으로 Adoptium JDK를 찾을 수 없습니다.")
                print("konlpy/JPype가 제대로 작동하지 않을 수 있습니다.")
        else:
            print(f"JAVA_HOME이 이미 설정되어 있습니다: {java_home}")
        
        # 현재 Java 버전 확인
        try:
            import subprocess
            result = subprocess.run(['java', '-version'], capture_output=True, text=True, stderr=subprocess.STDOUT)
            print(f"Java 버전 정보: {result.stdout}")
        except Exception as e:
            print(f"Java 버전 확인 중 오류 발생: {e}")

    def read_file(self):
        """
        파일을 읽어서 텍스트 내용을 반환합니다.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return text
        except Exception as e:
            ic(f"파일 읽기 오류: {e}")
            return ""

    def extract_hangul(self, text):
        """
        텍스트에서 한글만 추출합니다.
        """
        hangul = re.compile('[^가-힣\\s]')
        result = hangul.sub('', text)
        return result

    def change_token(self, text):
        """
        텍스트를 토큰화하여 단어 목록으로 변환합니다.
        """
        if nltk_available:
            try:
                tokens = word_tokenize(text)
                return tokens
            except Exception as e:
                print(f"NLTK 토큰화 실패: {e}. 기본 토큰화 사용")
                # 기본 토큰화 방식으로 대체
                return text.split()
        else:
            # NLTK가 없을 경우 간단한 공백 기반 토큰화 사용
            return text.split()

    def change_token_by_date(self, text, date_list):
        """
        특정 날짜별로 텍스트를 토큰화합니다.
        """
        result = {}
        for date in date_list:
            # 날짜 패턴 찾기
            pattern = f"{date}.*?(?={date_list[0]}|$)"
            date_text = re.search(pattern, text)
            if date_text:
                date_text = date_text.group()
                # 해당 날짜의 텍스트를 토큰화
                result[date] = self.change_token(date_text)
        return result

    def extract_noun(self, text):
        """
        텍스트에서 명사만 추출합니다.
        Okt가 실패하면 간단한 정규식 기반 접근법을 사용합니다.
        """
        try:
            if self.use_okt:
                print("Okt를 사용하여 명사 추출 중...")
                nouns = self.okt.nouns(text)
                # 한 글자 명사 제외
                nouns = [noun for noun in nouns if len(noun) > 1]
                return nouns
            else:
                print("정규식 기반 접근법으로 명사 추출 중...")
                # 간단한 공백 기반 토큰화
                words = text.split()
                # 2글자 이상인 단어만 선택 (한글자 명사 제외)
                words = [word for word in words if len(word) > 1]
                return words
        except Exception as e:
            ic(f"명사 추출 오류: {e}")
            print(f"명사 추출 중 오류 발생: {e}")
            # 오류 발생 시 간단한 공백 기반 토큰화로 대체
            words = text.split()
            words = [word for word in words if len(word) > 1]
            return words

    def read_stopwords(self):
        """
        불용어 사전을 읽어옵니다. 파일이 없으면 기본 불용어 목록을 반환합니다.
        """
        try:
            if os.path.exists(self.stopwords_path):
                with open(self.stopwords_path, 'r', encoding='utf-8') as f:
                    stopwords = f.read().splitlines()
            else:
                # 기본 불용어 목록
                stopwords = ['및', '등', '이', '그', '또한', '수', '이를', '통해', '위해', '위한', 
                            '이에', '더', '한', '또', '큰', '작은', '많은', '적은', '있는', '없는']
                # 기본 불용어 파일 생성
                with open(self.stopwords_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(stopwords))
            return stopwords
        except Exception as e:
            ic(f"불용어 사전 읽기 오류: {e}")
            return ['및', '등', '이', '그', '또한']

    def remove_stopwords(self, tokens):
        """
        토큰 목록에서 불용어를 제거합니다.
        """
        stopwords = self.read_stopwords()
        result = [word for word in tokens if word not in stopwords]
        return result
    
    def find_frequency(self, tokens, top_n=100):
        """
        토큰의 빈도수를 계산하여 상위 n개를 반환합니다.
        """
        if nltk_available:
            try:
                fdist = FreqDist(tokens)
                return fdist.most_common(top_n)
            except Exception as e:
                print(f"NLTK FreqDist 사용 실패: {e}. Counter 사용")
                # FreqDist가 실패하면 Counter로 대체
                counter = Counter(tokens)
                return counter.most_common(top_n)
        else:
            # NLTK가 없을 경우 Counter 사용
            counter = Counter(tokens)
            return counter.most_common(top_n)
    
    def draw_wordcloud(self, frequency_list, output_filename='wordcloud.png'):
        """
        빈도수 데이터를 기반으로 워드클라우드를 생성하고 저장합니다.
        """
        try:
            print("워드클라우드 생성 시작...")
            # 폰트 경로 설정 (한글 지원)
            font_path = self._get_font_path()
            print(f"사용할 폰트 경로: {font_path}")
            
            # 빈도수 데이터를 딕셔너리로 변환
            word_dict = dict(frequency_list)
            print(f"단어 빈도수 딕셔너리 생성 완료: {len(word_dict)}개 단어")
            
            # 워드클라우드 생성
            wc = WordCloud(
                font_path=font_path,
                background_color='white',
                width=800,
                height=600,
                max_words=200,
                max_font_size=200,
                random_state=42
            )
            
            print("워드클라우드 객체 생성 완료, 빈도 데이터 적용 중...")
            wc.generate_from_frequencies(word_dict)
            print("워드클라우드 빈도 데이터 적용 완료")
            
            # 이미지 저장
            output_file = os.path.join(self.output_path, output_filename)
            print(f"이미지 저장 시작: {output_file}")
            
            plt.figure(figsize=(10, 8))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            
            print("워드클라우드 그리기 완료, 저장 중...")
            plt.savefig(output_file, bbox_inches='tight')
            plt.close()
            
            print(f"워드클라우드 저장 완료: {output_file}")
            ic(f"워드클라우드 저장 완료: {output_file}")
            return output_file
        except Exception as e:
            print(f"워드클라우드 생성 중 오류 발생: {e}")
            ic(f"워드클라우드 생성 오류: {e}")
            
            # 오류 정보 자세히 출력
            import traceback
            traceback.print_exc()
            
            # 간단한 텍스트 파일로 결과 저장 (대체 방법)
            try:
                simple_output = os.path.join(self.output_path, 'wordcloud_text.txt')
                with open(simple_output, 'w', encoding='utf-8') as f:
                    for word, freq in frequency_list[:100]:
                        f.write(f"{word}: {freq}\n")
                print(f"대체 텍스트 파일 저장 완료: {simple_output}")
                return simple_output
            except:
                return None
    
    def _get_font_path(self):
        """
        시스템에서 사용 가능한 한글 폰트 경로를 반환합니다.
        """
        # 기본 폰트 경로
        default_font = None
        
        print("한글 폰트 찾는 중...")
        
        # 프로젝트 내 폰트 체크 (가장 먼저 확인)
        project_font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'original', 'D2Coding.ttf')
        if os.path.exists(project_font_path):
            print(f"프로젝트 내 폰트 발견: {project_font_path}")
            return project_font_path
        
        # 맥OS 폰트 경로
        mac_font_path = '/Library/Fonts/AppleGothic.ttf'
        # 윈도우 폰트 경로
        windows_font_path = 'c:/Windows/Fonts/malgun.ttf'
        # 리눅스 폰트 경로
        linux_font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
        
        # 시스템별 폰트 체크
        if os.path.exists(mac_font_path):
            print(f"MacOS 폰트 발견: {mac_font_path}")
            default_font = mac_font_path
        elif os.path.exists(windows_font_path):
            print(f"Windows 폰트 발견: {windows_font_path}")
            default_font = windows_font_path
        elif os.path.exists(linux_font_path):
            print(f"Linux 폰트 발견: {linux_font_path}")
            default_font = linux_font_path
        else:
            # matplotlib에서 사용 가능한 폰트 중 한글 지원 폰트 찾기
            print("시스템 폰트 목록에서 한글 폰트 찾는 중...")
            fonts = [f.name for f in fm.fontManager.ttflist]
            for font in fonts:
                if any(keyword in font.lower() for keyword in ['gothic', 'gulim', 'batang', 'malgun', 'nanum']):
                    default_font = fm.findfont(fm.FontProperties(family=font))
                    print(f"Matplotlib 폰트 발견: {default_font}")
                    break
        
        if not default_font:
            print("한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
            ic("한글 폰트를 찾을 수 없습니다. 시스템에 한글 폰트를 설치해주세요.")
            # 기본 폰트 사용 (한글이 제대로 표시되지 않을 수 있음)
            default_font = fm.findfont(fm.FontProperties(family='DejaVu Sans'))
            print(f"기본 폰트 사용: {default_font}")
        
        return default_font
    
    def process_report(self):
        """
        전체 프로세스를 실행하여 워드클라우드를 생성합니다.
        """
        try:
            print("워드클라우드 생성 프로세스 시작...")
            
            # 파일 읽기
            print("파일 읽기 시작...")
            text = self.read_file()
            if not text:
                print("파일을 읽을 수 없습니다.")
                return "파일을 읽을 수 없습니다."
            
            print(f"파일 읽기 완료: {len(text)} 글자")
            
            # 한글만 추출
            print("한글 추출 중...")
            hangul_text = self.extract_hangul(text)
            print(f"한글 추출 완료: {len(hangul_text)} 글자")
            
            # 명사 추출
            print("명사 추출 중...")
            nouns = self.extract_noun(hangul_text)
            print(f"명사 추출 완료: {len(nouns)} 개")
            
            # 불용어 제거
            print("불용어 제거 중...")
            filtered_nouns = self.remove_stopwords(nouns)
            print(f"불용어 제거 완료: {len(filtered_nouns)} 개")
            
            # 빈도수 계산
            print("빈도수 계산 중...")
            frequency = self.find_frequency(filtered_nouns)
            print(f"빈도수 계산 완료: 상위 단어는 {frequency[:5] if frequency else '없음'}")
            
            # 워드클라우드 생성
            print("워드클라우드 생성 중...")
            output_file = self.draw_wordcloud(frequency)
            
            if output_file:
                print(f"워드클라우드 생성 성공: {output_file}")
                return f"워드클라우드가 생성되었습니다: {output_file}"
            else:
                print("워드클라우드 생성 실패")
                return "워드클라우드 생성에 실패했습니다."
        
        except Exception as e:
            print(f"프로세스 실행 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return f"오류가 발생했습니다: {str(e)}"
    
    
    
    
