import folium
import numpy as np
from app.domain.model.reader_schema import ReaderSchema
from app.domain.model.data_schema import DataSchema
import pandas as pd
import os
from app.domain.model.google_map_singleton import ApiKeyManager


class CrimeService:
    def __init__(self):
        self.reader = ReaderSchema()
        self.dataschema = DataSchema()
        self.dataset = DataSchema()  # ✅ 핵심 추가

    def preprocess(self, *args) -> object:
        print(f"------------모델 전처리 시작-----------")
        temp = list(args)
        this = self.dataset
        this.cctv = self.new_model(temp[0])
        this = self.save_csv(temp[0], this)
        this.crime = self.new_model(temp[1])
        this = self.save_csv(temp[1], this)
        this.pop = self.new_model(temp[2])
        this = self.save_csv(temp[2], this)
        this = self.update_pop(this)
        this = self.update_crime(this)
        this = self.update_cctv(this)
        return this

    def new_model(self, fname) -> object:
        reader = self.reader
        this = self.dataset
        print(f"Dataset 객체 확인: {this}")
        reader.fname = fname
        if reader.fname.endswith(".csv"):
            print(f"📂 CSV 파일 로드: {reader.fname}")
            return reader.csv_to_dframe()
        elif reader.fname.endswith(".xls"):
            print(f"📂 Excel 파일 로드: {reader.fname}")
            return reader.xls_to_dframe(header=2, usecols='B,D,G,J,N')
        else:
            raise ValueError(f"🚩 지원하지 않는 파일 형식입니다: {fname}")

    def save_csv(self, fname: str, this) -> object:
        base_name = os.path.splitext(fname)[0]
        BASE_DIR = "C:\\Users\\bitcamp\\Documents\\kpmg-250424\\kpmg\\v2\\ai-server\\crime-service\\app\\domain\\stored_data"
        existing_files = [os.path.splitext(f)[0] for f in os.listdir(BASE_DIR)]
        if base_name in existing_files:
            print(f"⚠️ 동일한 이름({base_name})의 파일이 이미 존재합니다. 저장을 건너뜁니다.")
            return this
        keyword = self.extract_keyword_from_fname(fname)
        method = self.get_update_method(keyword)
        if method:
            this = method(self, this)
        return this

    def get_update_method(self, keyword):
        method_name = f"update_{keyword}"
        method = getattr(self, method_name, None)
        print(f"🔍 가져온 메서드: {method_name}")
        return method

    def extract_keyword_from_fname(self, fname):
        return fname.split("_")[0]

    def update_cctv(self, this) -> object:
        this.cctv = this.cctv.drop(['2013년도 이전', '2014년', '2015년', '2016년'], axis=1)
        cctv = this.cctv.rename(columns={'기관명': '자치구'})
        SAVE_DIR = "C:\\Users\\bitcamp\\Documents\\kpmg-250424\\kpmg\\v2\\ai-server\\crime-service\\app\\domain\\updated_data"
        cctv.to_csv(os.path.join(SAVE_DIR, "cctv_seoul.csv"), index=False)
        print(f"😄cctv 데이터 확인:\n{cctv.head()}")
        this.cctv = cctv
        return this

    def update_crime(self, this) -> object:
        crime = this.crime
        station_names = ['서울' + str(name[:-1]) + '경찰서' for name in crime['관서명']]
        gmaps = ApiKeyManager()
        station_addrs = [gmaps.geocode(name, language='ko')[0].get("formatted_address") for name in station_names]
        station_lats = [gmaps.geocode(name, language='ko')[0].get("geometry")['location']['lat'] for name in station_names]
        station_lngs = [gmaps.geocode(name, language='ko')[0].get("geometry")['location']['lng'] for name in station_names]
        gu_names = [addr.split()[[gu.endswith('구') for gu in addr.split()].index(True)] for addr in station_addrs]
        crime['자치구'] = gu_names
        crime = self.crime_modify(crime)
        SAVE_DIR = "C:\\Users\\bitcamp\\Documents\\kpmg-250424\\kpmg\\v2\\ai-server\\crime-service\\app\\domain\\updated_data"
        crime.to_csv(os.path.join(SAVE_DIR, 'crime_seoul.csv'), index=False)
        this.crime = crime
        return this

    def crime_modify(self, crime_df):
        crime_df['발생 합계'] = crime_df.filter(like='발생').sum(axis=1)
        crime_df['검거 합계'] = crime_df.filter(like='검거').sum(axis=1)
        crime_df = crime_df[['자치구', '발생 합계', '검거 합계']]
        print(f"📂범죄 데이터 수정 확인:\n{crime_df.head()}")
        return crime_df

    def update_pop(self, this) -> object:
        pop = this.pop.rename(columns={
            pop.columns[0]: '자치구',
            pop.columns[1]: '인구수',
            pop.columns[2]: '한국인',
            pop.columns[3]: '외국인',
            pop.columns[4]: '고령자'
        })
        pop.drop([26], inplace=True)
        pop['외국인 비율'] = pop['외국인'] / pop['인구수'] * 100
        pop['고령자 비율'] = pop['고령자'] / pop['인구수'] * 100
        pop['한국인 비율'] = pop['한국인'] / pop['인구수'] * 100
        this.pop = pop
        cctv_pop = pd.merge(this.cctv, this.pop, on='자치구')
        cor1 = np.corrcoef(cctv_pop['고령자 비율'], cctv_pop['소계'])
        cor2 = np.corrcoef(cctv_pop['외국인 비율'], cctv_pop['소계'])
        print(f"🔥 고령자비율과 CCTV 상관계수: {cor1}\n🔥 외국인비율과 CCTV 상관계수: {cor2}")
        return this
    
    def draw_crime_map(self, this) -> object:
        file = self.file
        reader = self.reader
        file.context = './saved_data/'
        file.fname = 'police_norm'
        police_norm = reader.csv(file)
        file.context = './data/'
        file.fname = 'geo_simple'
        state_geo = reader.json(file)
        file.fname = 'crime_in_seoul'
        crime = reader.csv(file)
        file.context = './saved_data/'
        file.fname = 'police_pos'
        police_pos = reader.csv(file)
        station_names = []
        for name in crime['관서명']:
            station_names.append('서울' + str(name[:-1] + '경찰서'))
        station_addrs = []
        station_lats = []
        station_lngs = []
        gmaps = reader.gmaps()
        for name in station_names:
            temp = gmaps.geocode(name, language='ko')
            station_addrs.append(temp[0].get('formatted_address'))
            t_loc = temp[0].get('geometry')
            station_lats.append(t_loc['location']['lat'])
            station_lngs.append(t_loc['location']['lng'])

        police_pos['lat'] = station_lats
        police_pos['lng'] = station_lngs
        col = ['살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거']
        tmp = police_pos[col] / police_pos[col].max()
        police_pos['검거'] = np.sum(tmp, axis=1)

        folium_map = folium.Map(location=[37.5502, 126.982], zoom_start=12, title='Stamen Toner')

        folium.Choropleth(
            geo_data=state_geo,
            data=tuple(zip(police_norm['구별'],police_norm['범죄'])),
            columns=["State", "Crime Rate"],
            key_on="feature.id",
            fill_color="PuRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Crime Rate (%)",
            reset=True,
        ).add_to(folium_map)
        for i in police_pos.index:
            folium.CircleMarker([police_pos['lat'][i], police_pos['lng'][i]],
                                radius=police_pos['검거'][i] * 10,
                                fill_color='#0a0a32').add_to(folium_map)

        folium_map.save('./saved_data/crime_map.html')
        return this

    def print_this(self, this):
        print('*' * 100)
        print(f'1. cctv 의 type \n {type(this.cctv)} ')
        print(f'2. cctv 의 column \n {this.cctv.columns} ')
        print(f'3. cctv 의 상위 5개 행\n {this.cctv.head()} ')
        print(f'4. cctv 의 null 의 개수\n {this.cctv.isnull().sum()}개')
        print(f'5. crime 의 type \n {type(this.crime)}')
        print(f'6. crime 의 column \n {this.crime.columns}')
        print(f'7. crime 의 상위 5개 행\n {this.crime.head()}개')
        print(f'8. crime 의 null 의 개수\n {this.crime.isnull().sum()}개')
        print(f'5. pop 의 type \n {type(this.pop)}')
        print(f'6. pop 의 column \n {this.pop.columns}')
        print(f'7. pop 의 상위 5개 행\n {this.pop.head()}개')
        print(f'8. pop 의 null 의 개수\n {this.pop.isnull().sum()}개')
        print('*' * 100)