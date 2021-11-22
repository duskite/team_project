#-*-coding:utf-8-*-
import pandas as pd
import numpy as np
import requests
import json
import xmltodict
import platform


def load_covid(period=None): # 도별 확진환자수 데이터 로드
    missing_values = ['--', '-', 'na'] #nan값 설정

    df_covid = pd.read_csv('./resource/코로나바이러스감염증-19_확진환자_발생현황_211122.csv', index_col='일자',
                           na_values=missing_values)
    df_covid = df_covid.transpose().fillna("0") # rows 지역, columns 일자로 전치함
    df_covid = df_covid.apply(lambda x: x.apply(lambda y:y.replace(",",""))).astype(np.int64) # 데이터프레임 내부의 모든값을 숫자로 바꿈

    if period == None:
        return df_covid
    elif len(period) == 1: #하루만 보는 경우
        print(period)
        return df_covid[period[0]]
    else:
        tmp_df = df_covid.loc[:, period[0]:period[1]]
        tmp_df['기간 총합'] = tmp_df.sum(axis=1) # Warning 확인해볼 필요가 있음
        return tmp_df


def load_hospital(): # 도별 병원수 데이터 로드
    missing_values = ['--', '-', 'na']  # nan값 설정

    df_hospital = pd.read_csv('./resource/건강보험심사평가원_의료기관별 감염병 및 중증환자 치료시설 현황_20210630.csv', index_col='시도명',
                              na_values=missing_values)
    df_hospital = df_hospital.groupby('시도명').agg(sum)
    df_hospital['총 병상수'] = df_hospital.sum(axis=1)

    # covid 데이터 프레임과 인덱스명 통일시킴
    name_match = {'강원도':'강원','경기도':'경기','경상남도':'경남','경상북도':'경북','광주광역시':'광주','대구광역시':'대구',
                  '대전광역시':'대전','부산광역시':'부산','서울특별시':'서울','세종특별자치시':'세종','울산광역시':'울산',
                  '인천광역시':'인천','전라남도':'전남','전라북도':'전북','제주특별자치도':'제주','충청남도':'충남','충청북도':'충북'}
    df_hospital = df_hospital.rename(index=name_match)

    return df_hospital


def load_nurse(period, option=None): # 간호인력 데이터 로드 분기별로, 옵션은 시도별로 묶어서 보여줄지 여부
    missing_values = ['--', '-', 'na']

    year, quarter  = period.split("-")
    dir = './resource/의료인력_간호사/' + year + '년' + quarter + '분기.csv' # 입력값에 맞는 분기의 csv 파일 로드
    df_nurse = pd.read_csv(dir, na_values=missing_values, index_col='시도')

    hospital_or_public_health = df_nurse['요양기관종별'].str.contains('상급종합병원|종합병원|보건소') #해당하는 문자열 있는지 판단
    # 병원을 포함하는 단어가 요양병원, 치과병원 등도 있어서 병원은 따로 체크함
    df_nurse = df_nurse[['요양기관종별','간호사','간호조무사']][hospital_or_public_health | (df_nurse['요양기관종별']=='병원')]

    df_nurse = df_nurse.fillna("0") # 아래에서 문자열 치환하기 위해서 임시로 nan부분도 문자열 0으로 바꿔놓음
    #숫자가 있는 부분부터만 모두 숫자로 바꿈
    df_nurse.iloc[:,1:] = df_nurse.iloc[:,1:].apply(lambda x: x.apply(lambda y: y.replace(",", ""))).astype(np.int64)


    if option == '시도별' : # 시도별로 묶여있는 데이터 만듦
        df_nurse = df_nurse.groupby('시도').agg(sum).reset_index().set_index('시도') #시도별 총 간호사, 간호조무사 데이터
        df_nurse['합계'] = df_nurse.sum(axis=1, numeric_only=True)
    else:
        df_nurse['합계'] = df_nurse.sum(axis=1, numeric_only=True)

    return df_nurse


def load_hospital_bed(select): # 데이터 어짜피 2개뿐이라 0 or 1로 필요한 데이터 리턴
    missing_values = ['--', '-',' - ' 'na']  # nan값 설정

    if select == 0:
        df_hospital_bed = pd.read_csv('resource/격리병실 관련자료/지역_종류별_보유_병상과_가용_병상(8월 기준).csv', na_values=missing_values)
    elif select == 1:
        df_hospital_bed = pd.read_csv('resource/격리병실 관련자료/지역_종류별_보유_병상과_가용_병상(11월 기준).csv', na_values=missing_values)

    df_hospital_bed.fillna(0, inplace=True)
    df_hospital_bed.iloc[:, 2:] = df_hospital_bed.iloc[:, 2:].astype(np.int64)

    return df_hospital_bed



# 아직은 날짜 하루밖에 못보게 만들었음, 필요하면 기간에 대해서 뽑을수 있도록 할 예정
def load_covid_api(period):  # ['2021.10.11']

    if len(period) == 1:
        period += period  # 리스트끼리 더함 시작날짜와 종료날짜 필요해서

    period[0] = period[0].replace('.', '')
    period[1] = period[1].replace('.', '')

    key_decoding = 'saEBBtfCp5LEcTo0MsOzAk+F1mVEm/STDsIdGUSMemDDmzhaAT1IH0z8xurajnfPo3zMlnyeJhjiADX2B4s70g=='

    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
    params = {'serviceKey': key_decoding, 'pageNo': '1', 'numOfRows': '1', 'startCreateDt': period[0],
              'endCreateDt': period[1]}

    response = requests.get(url, params=params)
    data = xmltodict.parse(response.content)

    df = pd.DataFrame(data['response']['body']['items']['item'])

    df.rename(columns={'gubun': '구분', 'deathCnt': '사망자 수', 'defCnt': '확진자 수', 'incDec': '전일대비 증감 수',
                       'isolIngCnt': '격리중 환자수', 'isolClearCnt': '격리 해제 수', 'qurRate': '10만명당 발생률',
                       'localOccCnt': '지역발생 수',
                       'overFlowCnt': '해외유입 수'}, inplace=True)
    df.index = df['구분']
    df = df.drop(['구분', 'createDt', 'gubunCn', 'gubunEn', 'seq', 'stdDay', 'updateDt'], axis=1)  # 필요없는거 드랍

    return df


def load_population(): # 인구 통계 csv 로드

    # csv 파일을 만들 떄 전국 명을 표기해 두었는데, 다른 자료에서는 없는 것 같아서 drop 시킴.
    if platform.system() == 'Darwin':
        df_population = pd.read_csv('./resource/인구.csv', index_col='지역명').drop(['전국'])
    elif platform.system() == 'Windows':
        df_population = pd.read_csv('./resource/인구.csv',index_col = '지역명').drop(['전국'])
    
    return df_population
