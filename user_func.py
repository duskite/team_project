#-*-coding:utf-8-*-
import numpy as np
import pandas as pd
from load_data import *
import csv


def nurse_diff(quarter_list): # 분기 2가지를 입력받아서 2개의 차이를 구해줌 예시 ['2020-1','2020-2']

    tmp_df = load_nurse(quarter_list[0], '시도별')
    tmp_df2 = load_nurse(quarter_list[1], '시도별')

    df_diff = tmp_df2 - tmp_df
    df_diff = df_diff.rename(columns={'간호사':'간호사 변동(명)', '간호조무사':'간호조무사 변동(명)','합계':'지역 총 변동(명)'})

    df_diff_percent = (tmp_df2 / tmp_df) - 1 # 기존 분기 대비 변화 퍼센트 / 양수-증가, 음수-감소
    df_diff_percent = df_diff_percent.rename(columns={'간호사':'간호사 변화율', '간호조무사':'간호조무사 변화율','합계':'지역 총 변화율'})

    # 데이터 프레임 합치고 순서만 좀 정렬함
    df_diff_all = pd.concat([df_diff,df_diff_percent], axis=1)
    df_diff_all = df_diff_all[['간호사 변동(명)','간호사 변화율','간호조무사 변동(명)','간호조무사 변화율', '지역 총 변동(명)','지역 총 변화율']]

    return df_diff_all


def hospital_bed_diff(): #8월 병상수 -> 11월 병상수 변화량 구하는 함수
    tmp_df = load_hospital_bed(0) #첫번째 데이터 로드
    tmp_df2 = load_hospital_bed(1) #두번째 데이터 로드

    columns_1_2 = tmp_df[['수도권 여부','상세 지역']] #앞부분만 따로 붙히려고
    hospital_bed_diff = tmp_df2.iloc[:,2:] - tmp_df.iloc[:,2:] # 숫자끼리만 연산

    df_hospital_bed_diff = pd.concat([columns_1_2,hospital_bed_diff], axis=1)

    return df_hospital_bed_diff #최종적으로 8월에서 10월 병상수 변화량을 보여줌

def sort_region(df): # 데이터 프레임 입력 받아서 정해진 index로 순서 맞춰서 리턴

    regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기',
               '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
    if len(df) > 17: # 그냥 지역명만 있으면 17이고, 검역까지 있으면 18임
        regions.append('검역')

    sorted_df = df.reindex(index=regions)

    return sorted_df

def weight_danger(region_list):

    # 60세 기준 이하 감염자중 사망자 비율 / 이상 감염자중 사망자 비율을 구함
    # 0.0833 / 3.5106
    # 1 / 42 로 가중치 잡음
    undder60 = 1
    upper60 = 42

    weighted_region = []
    weighted_region.append(region_list[0] * undder60)
    weighted_region.append(region_list[1] * upper60)

    return sum(weighted_region)

def percent_covid(df_population, df_covid_api, region):

    return ((int(df_covid_api['확진자 수'].loc[region]) / int(df_population['총인구수'].loc[region])) * 100)

# 잠깐 테스트중
# df = load_population()
# df2 = load_covid_api(['2021.11.20'])
#
# seoul = [0.7, 0.3]
# x = [0.3, 0.7]
# print(weight_danger(seoul) * percent_covid(df, df2, '서울'))
# print(weight_danger(x) * percent_covid(df, df2, '경기'))


def Nomalization():
    name = pd.read_excel("./resource/file.xlsx", header=3, usecols='B', thousands=',')
    f = pd.read_excel("./resource/file.xlsx", header=3, usecols='E:J', thousands=',')
    f2 = pd.read_excel("./resource/file.xlsx", header=3, usecols='K:O', thousands=',')
    country = pd.read_excel("./resource/file.xlsx", header=3, usecols='C', thousands=',')
    name_list = name.values
    c = []
    for name in name_list:
        name = str(name)
        val = name.replace(' ', '').replace('[', '').replace(']', '').replace('\'', '')

        c.append(val)
    df_sum = list(f.sum(axis=1).values)
    df2_sum = list(f2.sum(axis=1).values)
    con = list(country.sum(axis=1).values)

    regions = ['전국','서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기',
               '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
    result = dict()

    for i in range(len(con)):
        val = (round(df_sum[i] / con[i], 3), round(df2_sum[i] / con[i], 3))
        # str_ = c[i] + str(val)
        # print(str_)

        result[regions[i]] = val
        #
        # result.append(str_)

    del result['전국']  # 전국 우선 필요없어서 지움

    return result # 딕셔너리로 리턴
