#-*-coding:utf-8-*-
import font_init
import matplotlib.pyplot as plt
# 여기서 부터는 직접 만든 모듈들 임포트
from load_data import *
from user_func import *

def main():

    # 그냥 임시로 만든 함수들 적어놓음
    # 나중에는 main 안에 데이터 로드하고 plot 그리는 것만

    # ## 전체 데이터 가져올때
    # print('1')
    # df_covid = load_covid()
    # print(df_covid)
    # plt.bar(df_covid.index[1:], df_covid['누적(명)'][1:], align='center')
    # plt.show()
    #
    # print('2')
    # ## 특정 날짜만 데이터 가져올때
    # df_covid = load_covid(['2020.1.20'])
    # print(df_covid)
    #
    # print('3')
    # ## 기간에 대한 데이터 가져올때 Warning은 확인 필요함
    # df_covid = load_covid(['2020.1.20', '2020.2.23'])
    # print(df_covid)
    #
    # print('4')
    # ## 시도별 병원수 가져오는 함수
    # df_hospital = load_hospital()
    # print(df_hospital)
    #
    # print('5')
    # ## 간호사 데이터 가져오기 case 1 병원까지 나오는거
    # df_nurse = load_nurse('2019-1')
    # print(df_nurse)
    #
    # print('6')
    # ## 간호사 데이터 가져오기 case 2
    # df_nurse = load_nurse('2019-1','시도별')
    # print(df_nurse)


    # print('7')
    # ## 간호사 데이터 분기별 변화율 확인
    # df_nurse_diff = nurse_diff(['2019-1', '2021-3'])
    # print(df_nurse_diff)
    # print(df_nurse_diff[df_nurse_diff['지역 총 변화율'] >= 0.2])


    print('8')
    ## 병상수 증가량 체크 8월과 11월 데이터 2개의 차이 체크
    print('8월 병상수\n', load_hospital_bed(0))
    print('11월 병상수\n', load_hospital_bed(1))
    print('8->11월 병상수 변화\n', hospital_bed_diff())


    print('9')
    print('코로나 api로 불러온 데이터\n', load_covid_api(['2021.11.13']))




main()