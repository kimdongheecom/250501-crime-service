# 데이터 전처리 작업을 위한 클래스
import logging
import os
import traceback
from fastapi import HTTPException
import folium
import numpy as np
import pandas as pd
from sklearn import preprocessing

from app.domain.model.reader_schema import ReaderSchema
from app.domain.model.crime_schema import CrimeSchema
from app.domain.model.google_map_schema import ApiKeyManager, GoogleMapSchema
from app.domain.model.data_save import save_dir
from app.domain.service.internal.crime_map_create import CrimeMapCreator

logger = logging.getLogger("crime_service") # 로거 설정

class CrimeService:
    def __init__(self):
        self.reader = ReaderSchema()
        self.dataset = CrimeSchema()
        self.crime_rate_columns = ['살인검거율', '강도검거율', '강간검거율', '절도검거율', '폭력검거율']
        self.crime_columns = ['살인', '강도', '강간', '절도', '폭력']
        self.stored_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'stored_data')
        self.updated_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'updated_data')

    def preprocess(self, *args) -> CrimeSchema:
        """파일 로드 및 전처리 함수"""
        logger.info(f"------------모델 전처리 시작-----------")

        for i in list(args):
            logger.debug(f"전처리 대상 파일: {i}")
            self.save_object_to_csv(i)
        return self.dataset

    def create_matrix(self, fname) -> pd.DataFrame:
        self.reader.fname = fname

        if fname.endswith('.csv'):
            return self.reader.csv_to_dframe()
        elif fname.endswith('.xls') or fname.endswith('.xlsx'):
            return self.reader.xls_to_dframe(header=2, usecols='B,D,G,J,N')
        else:
            logger.error(f"지원하지 않는 파일 형식: {fname}")
            raise ValueError(f"❌ 지원하지 않는 파일 형식: {fname}")

    def save_object_to_csv(self, fname) -> None:
        logger.info(f"🌱 save_object_to_csv 실행 : {fname}")
        full_name = os.path.join(save_dir, fname)

        try:
            if not os.path.exists(full_name) and fname == "cctv_in_seoul.csv":
                self.dataset.cctv = self.create_matrix(fname)
                self.update_cctv()
            
            elif not os.path.exists(full_name) and fname == "crime_in_seoul.csv":
                self.dataset.crime = self.create_matrix(fname)
                self.update_crime() 
                self.update_police() 

            elif not os.path.exists(full_name) and fname == "pop_in_seoul.xls":
                self.dataset.pop = self.create_matrix(fname)
                self.update_pop()

            else:
                logger.info(f"파일이 이미 존재하거나 처리 대상이 아님: {fname}")

        except FileNotFoundError as e:
            logger.error(f"파일 처리 중 오류: {fname} 파일을 찾을 수 없습니다. - {e}")
            raise HTTPException(status_code=404, detail=f"{fname} 파일을 찾을 수 없습니다.")
        except ValueError as e:
            logger.error(f"파일 처리 중 오류: {fname} 처리 중 값 오류 발생 - {e}")
            raise HTTPException(status_code=400, detail=f"{fname} 처리 중 오류 발생: {e}")
        except Exception as e:
            logger.error(f"파일 처리 중 예상치 못한 오류 ({fname}): {e}")
            raise HTTPException(status_code=500, detail=f"{fname} 처리 중 서버 오류 발생")
    # 데이터 업데이트 함수
    def update_cctv(self) -> None:
        if self.dataset.cctv is None:
            logger.warning("CCTV 데이터가 로드되지 않아 업데이트를 건너뛰니다.")
            return
        logger.info("CCTV 데이터 업데이트 중...")
        self.dataset.cctv = self.dataset.cctv.drop(['2013년도 이전', '2014년', '2015년', '2016년'], axis=1)
        logger.debug(f"CCTV 데이터 헤드 (업데이트 후): {self.dataset.cctv.head()}")
        cctv = self.dataset.cctv
        cctv = cctv.rename(columns={'기관명': '자치구'})
        self.dataset.cctv = cctv
  
    def update_crime(self) -> None:
        if self.dataset.crime is None:
            logger.warning("Crime 데이터가 로드되지 않아 업데이트를 건너뛰니다.")
            return
        gmaps = GoogleMapSchema()

        logger.info("Crime 데이터 업데이트 중... (Google Maps API 호출 포함)")
        logger.debug(f"CRIME 데이터 헤드 (업데이트 전): {self.dataset.crime.head()}")
        crime = self.dataset.crime
        station_names = [] # 경찰서 관서명 리스트

        for name in crime['관서명']:
            station_names.append('서울' + str(name[:-1]) + '경찰서')
        logger.debug(f"🔥💧경찰서 관서명 리스트: {station_names}")

        station_addrs = []
        station_lats = []
        station_lngs = []

        for name in station_names:
            try:
                tmp = gmaps.geocode(name, language='ko')
                if not tmp:
                    logger.warning(f"{name}에 대한 Google Maps 검색 결과 없음")
                    station_addrs.append('주소 없음')
                    station_lats.append(np.nan)
                    station_lngs.append(np.nan)
                    continue

                logger.debug(f"{name}의 검색 결과: {tmp[0].get('formatted_address')}")
                station_addrs.append(tmp[0].get('formatted_address'))
                tmp_loc = tmp[0].get('geometry')
                station_lats.append(tmp_loc['location']['lat'])
                station_lngs.append(tmp_loc['location']['lng'])
            except Exception as e:
                logger.error(f"Google Maps API 호출 중 오류 ({name}): {e}")
                station_addrs.append('오류 발생')
                station_lats.append(np.nan)
                station_lngs.append(np.nan)

        logger.debug(f"💧💧💧💧💧주소 리스트: {station_addrs}")
        gu_names = []
        for addr in station_addrs:
            if addr in ['주소 없음', '오류 발생']:
                gu_names.append('구 정보 없음')
                continue
            try:
                tmp = addr.split()
                tmp_gu_list = [gu for gu in tmp if gu.endswith('구')]
                if tmp_gu_list:
                    gu_names.append(tmp_gu_list[0])
                else:
                    logger.warning(f"주소 '{addr}'에서 '구' 정보를 찾을 수 없음")
                    gu_names.append('구 정보 없음')
            except Exception as e:
                logger.error(f"주소 '{addr}'에서 '구' 정보 추출 중 오류: {e}")
                gu_names.append('구 정보 오류')

        crime['자치구'] = gu_names

        crime_output_path = os.path.join(save_dir, 'crime_in_seoul_updated.csv')
        try:
            crime.to_csv(crime_output_path, index=False)
            logger.info(f"업데이트된 Crime 데이터를 CSV 파일로 저장: {crime_output_path}")
        except Exception as e:
            logger.error(f"업데이트된 Crime 데이터 저장 중 오류: {e}")

        self.dataset.crime = crime
    
    def update_police(self) -> None:
        if self.dataset.crime is None:
            logger.warning("Crime 데이터가 없어 Police 데이터 업데이트를 건너뛰니다.")
            return
        logger.info("Police 데이터 업데이트 및 정규화 중...")
        crime = self.dataset.crime

        try:
            valid_crime_data = crime[crime['자치구'].str.contains('구')]
            if valid_crime_data.empty:
                logger.error("Police 데이터 업데이트 불가: 유효한 자치구 정보가 포함된 Crime 데이터가 없습니다.")
                self.dataset.police = pd.DataFrame()
                return

            police = pd.pivot_table(valid_crime_data, index='자치구', aggfunc=np.sum)

            for crime_type in ['살인', '강도', '강간', '절도', '폭력']:
                occur_col = f'{crime_type} 발생'
                arrest_col = f'{crime_type} 검거'
                rate_col = f'{crime_type}검거율'

                if occur_col not in police.columns or arrest_col not in police.columns:
                    logger.warning(f"검거율 계산 불가: '{occur_col}' 또는 '{arrest_col}' 컬럼이 없습니다.")
                    police[rate_col] = 0
                    continue

                police[rate_col] = np.where(
                    police[occur_col] > 0,
                    (police[arrest_col] / police[occur_col]) * 100,
                    0
                )

            for col in self.crime_rate_columns:
                if col in police.columns:
                    police[col] = police[col].apply(lambda x: min(x, 100))
                else:
                    logger.warning(f"검거율 조정 불가: '{col}' 컬럼이 없습니다.")

            police.reset_index(inplace=True)
            available_rate_columns = [col for col in self.crime_rate_columns if col in police.columns]
            police = police[['자치구'] + available_rate_columns]
            police = police.round(1)

            police_output_path = os.path.join(save_dir, 'police_in_seoul.csv')
            police.to_csv(police_output_path, index=False)
            logger.info(f"Police 데이터를 CSV 파일로 저장: {police_output_path}")

            if not available_rate_columns:
                logger.warning("정규화할 검거율 데이터가 없어 Police Norm 데이터 생성을 건너뛰니다.")
                self.dataset.police = police
                return

            x = police[available_rate_columns].values
            min_max_scalar = preprocessing.MinMaxScaler()
            x_scaled = min_max_scalar.fit_transform(x.astype(float))

            police_norm_cols = [f'{col}_norm' for col in available_rate_columns]
            police_norm = pd.DataFrame(x_scaled, columns=police_norm_cols, index=police.index)
            police_norm['자치구'] = police['자치구']

            for col in available_rate_columns:
                police_norm[col] = police[col]

            police_norm['검거'] = np.sum(police_norm[police_norm_cols], axis=1)

            crime_occur_cols = [f'{t} 발생' for t in self.crime_columns if f'{t} 발생' in valid_crime_data.columns]
            if crime_occur_cols:
                crime_sum = pd.pivot_table(valid_crime_data, index='자치구', values=crime_occur_cols, aggfunc=np.sum)
                crime_sum['범죄발생총합'] = crime_sum.sum(axis=1)
                police_norm = pd.merge(police_norm, crime_sum[['범죄발생총합']], on='자치구', how='left')
                police_norm['범죄'] = police_norm['범죄발생총합']
                police_norm.drop(columns=['범죄발생총합'], inplace=True)
            else:
                logger.warning("'범죄' 컬럼 계산 불가: 발생 건수 데이터 부족")
                police_norm['범죄'] = 0

            police_norm_output_path = os.path.join(save_dir, 'police_norm_in_seoul.csv')
            police_norm.to_csv(police_norm_output_path, index=False)
            logger.info(f"정규화된 Police 데이터를 CSV 파일로 저장: {police_norm_output_path}")

            self.dataset.police = police

        except KeyError as e:
            logger.error(f"Police 데이터 업데이트 중 오류: 필요한 컬럼({e})이 없습니다.")
            raise HTTPException(status_code=400, detail=f"Police 데이터 처리 중 필요한 컬럼({e})이 없습니다.")
        except Exception as e:
            logger.error(f"Police 데이터 업데이트 중 예상치 못한 오류: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Police 데이터 처리 중 서버 오류 발생: {str(e)}")

    def update_pop(self) -> None:
        if self.dataset.pop is None:
            logger.warning("Population 데이터가 로드되지 않아 업데이트를 건너뛰니다.")
            return
        logger.info("Population 데이터 업데이트 중...")
        pop = self.dataset.pop

        try:
            pop = pop.rename(columns={
                pop.columns[0]: '구별',
                pop.columns[1]: '인구수',   
                pop.columns[2]: '한국인',
                pop.columns[3]: '외국인',
                pop.columns[4]: '고령자',
            })

            pop = pop[pop['구별'] != '합계']

            # ✅ 경고 제거를 위한 .loc 사용
            pop.loc[:, '인구수'] = pd.to_numeric(pop['인구수'], errors='coerce')
            pop.loc[:, '외국인'] = pd.to_numeric(pop['외국인'], errors='coerce')
            pop.loc[:, '고령자'] = pd.to_numeric(pop['고령자'], errors='coerce')
            pop = pop.fillna(0)

            pop.loc[:, '외국인비율'] = np.where(pop['인구수'] > 0, (pop['외국인'] / pop['인구수']) * 100, 0)
            pop.loc[:, '고령자비율'] = np.where(pop['인구수'] > 0, (pop['고령자'] / pop['인구수']) * 100, 0)

            self.dataset.pop = pop  # 데이터 저장은 마지막에 수행

            if (
                self.dataset.cctv is not None and 
                isinstance(self.dataset.cctv, pd.DataFrame) and 
                not self.dataset.cctv.empty
            ):
                if '자치구' not in self.dataset.cctv.columns:
                    logger.warning("CCTV 데이터에 '자치구' 컬럼이 없어 인구 데이터와 병합 및 상관계수 분석을 건너뛰니다.")
                else:
                    if '구별' in self.dataset.cctv.columns and '자치구' not in self.dataset.cctv.columns:
                        cctv_temp = self.dataset.cctv.rename(columns={'구별': '자치구'})
                    else:
                        cctv_temp = self.dataset.cctv

                    pop_temp = pop.rename(columns={'구별': '자치구'})

                    if '소계' not in cctv_temp.columns:
                        logger.warning("CCTV 데이터에 '소계' 컬럼이 없어 상관계수 분석을 건너뛰니다.")
                    else:
                        cctv_pop = pd.merge(cctv_temp, pop_temp, on='자치구')

                        if len(cctv_pop) > 1:
                            cor1 = np.corrcoef(cctv_pop['고령자비율'], cctv_pop['소계'])
                            cor2 = np.corrcoef(cctv_pop['외국인비율'], cctv_pop['소계'])
                            logger.info(f'고령자비율과 CCTV의 상관계수 {str(cor1)} \n'
                                        f'외국인비율과 CCTV의 상관계수 {str(cor2)} ')
                        else:
                            logger.warning("상관계수 계산 불가: 병합된 데이터가 부족합니다.")
            else:
                logger.warning("CCTV 데이터가 없어 상관계수 분석을 건너뛰니다.")

            logger.debug(f"🔥💧인구 데이터 헤드 (업데이트 후): {self.dataset.pop.head()}")

        except KeyError as e:
            logger.error(f"Population 데이터 업데이트 중 오류: 필요한 컬럼({e})이 없습니다.")
            raise HTTPException(status_code=400, detail=f"Population 데이터 처리 중 필요한 컬럼({e})이 없습니다.")
        except Exception as e:
            logger.error(f"Population 데이터 업데이트 중 예상치 못한 오류: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Population 데이터 처리 중 서버 오류 발생: {str(e)}")

    def draw_crime_map(self) -> dict:
        """범죄 지도를 생성하고 결과를 반환합니다."""
        try:
            map_creator = CrimeMapCreator()
            map_file_path = map_creator.create_map()
            return {"status": "범죄지도를 완성했습니다", "file_path": map_file_path}
        except HTTPException as e:
            logger.error(f"지도 생성 실패 (HTTPException): {e.status_code} - {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"지도 생성 중 예상치 못한 오류 발생: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"지도 생성 중 예상치 못한 서버 오류: {type(e).__name__}")

        