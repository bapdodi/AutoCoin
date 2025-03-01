import requests
import datetime
import pandas as pd
import json
import re
import time
import os

def Choose_coin(coin_list=None):
    """
    KRW-coin의 종목을 korean, english를 dic형태로 반환
    coin_list에는 korean KRW-coin을 리스트형태로 지정해주어야 한다.
    None인 경우 KRW-coin전체를 반환
    """
    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails": "false"}
    response = requests.get(url, params=querystring)
    contents = response.json()
    KRW_coin_dic = {}

    for x in contents:
        if "KRW" in x['market']:
            KRW_coin_dic[str(x['market'])] = x['korean_name']
    if coin_list is not None:
        return {key: value for key, value in KRW_coin_dic.items() if value in coin_list}
    return KRW_coin_dic


def get_url_ohlcv(interval):
    """
    candle에 대한 요청 주소를 얻는 함수
    :param interval: day(일봉), minute(분봉), week(주봉), 월봉(month)
    :return: candle 조회에 사용되는 url
    """
    intervals = {
        "day": ("https://api.upbit.com/v1/candles/days", 24 * 60),
        "minute1": ("https://api.upbit.com/v1/candles/minutes/1", 1),
        "minute3": ("https://api.upbit.com/v1/candles/minutes/3", 3),
        "minute5": ("https://api.upbit.com/v1/candles/minutes/5", 5),
        "minute10": ("https://api.upbit.com/v1/candles/minutes/10", 10),
        "minute15": ("https://api.upbit.com/v1/candles/minutes/15", 15),
        "minute30": ("https://api.upbit.com/v1/candles/minutes/30", 30),
        "minute60": ("https://api.upbit.com/v1/candles/minutes/60", 60),
        "minute240": ("https://api.upbit.com/v1/candles/minutes/240", 240),
        "week": ("https://api.upbit.com/v1/candles/weeks", 24 * 60 * 7),
        "month": ("https://api.upbit.com/v1/candles/months", 24 * 60 * 7 * 30),
    }

    url, timestep = intervals.get(interval, intervals["day"])
    candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
    return url, timestep, candle_list


def get_coin_data(local_path=None, start_day=None, step=None, coin_list=None):
    """
    coin_list에 대해 전체 데이터를 1day간격으로 추출하고, 
    local_path의 data폴더에 저장
    """
    url, timestep, candle_list = get_url_ohlcv(step)
    start_day = datetime.datetime(int(start_day[:4]), int(start_day[4:6]), int(start_day[6:]), 0, 0)
    time_diff = int(((datetime.datetime.now() - start_day).total_seconds() / 60.0) / timestep)

    KRW_coin_dic = Choose_coin(coin_list=coin_list)
    
    for market in KRW_coin_dic.keys():
        df = pd.DataFrame()
        date_now = datetime.datetime.now()
        
        # 필요한 부분만 한번에 처리할 수 있도록 loop 수정
        for i in range(0, time_diff, 200):
            date = (date_now - datetime.timedelta(minutes=i * timestep + 9 * 60)).strftime('%Y-%m-%d %H:%M:%S')
            querystring = {"market": market, "to": date, "count": "200"}  # UTC
            response = requests.get(url, params=querystring)
            contents = response.json()
            dt_list = [datetime.datetime.strptime(x['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S") for x in contents]
            df = pd.concat([df, pd.DataFrame(contents, columns=candle_list, index=dt_list)])
            time.sleep(0.1005)

            print(f"load data: {market}, {i + 1} / {time_diff}")  
        
        # 데이터를 파일로 저장
        df[::-1].to_csv(os.path.join(local_path, 'data', market + '.csv'), mode='w')

    return KRW_coin_dic


def get_data(stock, step="day", start_day=None):
    """
    주어진 기간(start_day부터 60일 전까지) 동안의 과거 데이터를 자동으로 가져오는 함수
    """
    url, timestep, candle_list = get_url_ohlcv(step)
    
    # 60일 전부터 데이터를 가져오도록 설정
    if start_day is None:
        start_day = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime("%Y%m%d")  # 60일 전 날짜
    
    # 시작 날짜를 datetime 형식으로 변환
    start_day = datetime.datetime(int(start_day[:4]), int(start_day[4:6]), int(start_day[6:]), 0, 0)
    
    # 현재 날짜와 start_day의 차이 계산
    time_diff = int(((datetime.datetime.now() - start_day).total_seconds() / 60.0) / timestep)
    
    df = pd.DataFrame()
    
    # 200개씩 데이터를 받아오는 방식
    for i in range(0, time_diff, 200):
        date = (datetime.datetime.now() - datetime.timedelta(minutes=i * timestep + 9 * 60)).strftime('%Y-%m-%d %H:%M:%S')
        querystring = {"market": stock, "to": date, "count": "200"}  # UTC
        response = requests.get(url, params=querystring)
        contents = response.json()
        
        # 데이터프레임에 추가
        dt_list = [datetime.datetime.strptime(x['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S") for x in contents]
        df = pd.concat([df, pd.DataFrame(contents, columns=candle_list, index=dt_list)])
        
        time.sleep(0.1005)  # API 호출 제한을 지키기 위한 대기 시간
        
        print(f"데이터 로드 중: {stock}, {i + 1} / {time_diff}")
    
    # 데이터 역순으로 정렬하여 반환
    return df[::-1]