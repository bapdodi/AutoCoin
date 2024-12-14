#Upbit 종목 선택, 종목에 대한 데이터 추출
import requests
import datetime
import pandas as pd
import json
import re
import time
import os
data = 40000

def Choose_coin(coin_list = None):
    """
    KRW-coin의 종목을 korean, english를 dic형태로 반환
    coin_list에는 korean KRW-coin을 리스트형태로 지정해주어야 한다.
    None인 경우 KRW-coin전체를 반환
    """
    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails":"false"}
    response = requests.request("GET", url, params=querystring)
    contents = response.json()
    KRW_coin_dic = {}

    for x in contents:
        if "KRW" in x['market']:
            KRW_coin_dic[str(x['market'])] = x['korean_name']
    if coin_list is not None:
        for key, value in list(KRW_coin_dic.items()):
            if value not in coin_list:
                del(KRW_coin_dic[str(key)])
        return KRW_coin_dic
    else:
        return KRW_coin_dic


def get_url_ohlcv(interval):
    """
    candle에 대한 요청 주소를 얻는 함수
    :param interval: day(일봉), minute(분봉), week(주봉), 월봉(month)
    :return: candle 조회에 사용되는 url
    opening_price : 시가
    high_price : 고가
    low_price : 저가
    trade_price : 종가
    candle_acc_trade_price : 누적 거래 금액
    candle_acc_trade_volume : 누적 거래량
    prev_closing_price : 전일 종가(UTC 0시 기준)
    change_price : 전일 종가 대비 변화 금액
    change_rate : 전일 종가 대비 변화량
    """
    if interval in ["day", "days"]:
        url = "https://api.upbit.com/v1/candles/days"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume", "prev_closing_price", "change_price", "change_rate"]
        timestpe = 24 * 60
    elif interval in ["minute1", "minutes1"]:
        url = "https://api.upbit.com/v1/candles/minutes/1"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
        timestpe = 1
    elif interval in ["minute3", "minutes3"]:
        url = "https://api.upbit.com/v1/candles/minutes/3"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
        timestpe = 3
    elif interval in ["minute5", "minutes5"]:
        url = "https://api.upbit.com/v1/candles/minutes/5"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
        timestpe = 5
    elif interval in ["minute10", "minutes10"]:
        url = "https://api.upbit.com/v1/candles/minutes/10"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
        timestpe = 10
    elif interval in ["minute15", "minutes15"]:
        url = "https://api.upbit.com/v1/candles/minutes/15"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
        timestpe = 15
    elif interval in ["minute30", "minutes30"]:
        url = "https://api.upbit.com/v1/candles/minutes/30"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
        timestpe = 30
    elif interval in ["minute60", "minutes60"]:
        url = "https://api.upbit.com/v1/candles/minutes/60"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
        timestpe = 60
    elif interval in ["minute240", "minutes240"]:
        url = "https://api.upbit.com/v1/candles/minutes/240"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
        timestpe = 240
    elif interval in ["week",  "weeks"]:
        url = "https://api.upbit.com/v1/candles/weeks"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
        timestpe = 24 * 60 * 7
    elif interval in ["month", "months"]:
        url = "https://api.upbit.com/v1/candles/months"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume"]
        timestpe = 24 * 60 * 7 * 30
    else:
        url = "https://api.upbit.com/v1/candles/days"
        candle_list = ["opening_price", "high_price", "low_price", "trade_price", "candle_acc_trade_price", "candle_acc_trade_volume", "prev_closing_price", "change_price", "change_rate"]
        timestpe = 24 * 60
    return url, timestpe, candle_list

def get_coin_data(local_path = None, start_day = None, step = None, coin_list = None):
    """
    start_day =yyyymmdd
    coin_list에 대해 전체 데이터 1day간격 데이터를 추출
    local_path의 data폴더에 저장
    """
    url, timestep, candle_list = get_url_ohlcv(step)
    start_day = datetime.datetime(int(start_day[:4]), int(start_day[4:6]), int(start_day[-2:]), 0, 0)
    time_diff = int(((datetime.datetime.now() - start_day).total_seconds() / 60.0) /timestep)

    KRW_coin_dic = Choose_coin(coin_list = coin_list)
    for market in KRW_coin_dic.keys():
        count = [0, 0, 0]
        df = pd.DataFrame()
        date_now =  datetime.datetime.now()
        for i in range(0, (time_diff - 200), 200):
            date = (date_now - datetime.timedelta(minutes= i * timestep + 9 * 60)).strftime('%Y-%m-%d %H:%M:%S')
            querystring = {"market":market, "to":date, "count":str(200)} #UTC
            response = requests.request("GET", url, params=querystring)
            contents = response.json()
            dt_list = [datetime.datetime.strptime(x['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S") for x in contents]
            df = pd.concat([df, pd.DataFrame(contents, columns= candle_list, index=dt_list)])
            time.sleep(0.1005)
            print("load data: {}, {} / {}".format(market, i + 1, time_diff))            
            df[::-1].to_csv(os.path.join(local_path,'data',market + '.csv'), mode='w')
            count[0] = count[0] + 1

        for i in range((200 * count[0]), (time_diff - 100), 100):
            date = (date_now - datetime.timedelta(minutes= i * timestep + 9 * 60)).strftime('%Y-%m-%d %H:%M:%S')
            querystring = {"market":market, "to":date, "count":str(100)} #UTC
            response = requests.request("GET", url, params=querystring)
            contents = response.json()
            dt_list = [datetime.datetime.strptime(x['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S") for x in contents]
            df = pd.concat([df, pd.DataFrame(contents, columns= candle_list, index=dt_list)])
            time.sleep(0.1005)
            print("load data: {}, {} / {}".format(market, i + 1, time_diff))            
            df[::-1].to_csv(os.path.join(local_path,'data',market + '.csv'), mode='w')
            count[1] = count[1] + 1

        for i in range((200 * count[0] + 100 * count[1]), (time_diff - 10), 10):
            date = (date_now - datetime.timedelta(minutes= i * timestep + 9 * 60)).strftime('%Y-%m-%d %H:%M:%S')
            querystring = {"market":market, "to":date, "count":str(10)} #UTC
            response = requests.request("GET", url, params=querystring)
            contents = response.json()
            dt_list = [datetime.datetime.strptime(x['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S") for x in contents]
            df = pd.concat([df, pd.DataFrame(contents, columns= candle_list, index=dt_list)])
            time.sleep(0.1005)
            print("load data: {}, {} / {}".format(market, i + 1, time_diff))            
            df[::-1].to_csv(os.path.join(local_path,'data',market + '.csv'), mode='w')
            count[2] = count[2] + 1

        for i in range((200 * count[0] + 100 * count[1] + 10 * count[2]), time_diff):
            date = (date_now - datetime.timedelta(minutes= i * timestep + 9 * 60)).strftime('%Y-%m-%d %H:%M:%S')
            querystring = {"market":market, "to":date, "count":str(1)} #UTC
            response = requests.request("GET", url, params=querystring)
            contents = response.json()
            dt_list = [datetime.datetime.strptime(x['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S") for x in contents]
            df = pd.concat([df, pd.DataFrame(contents, columns= candle_list, index=dt_list)])
            time.sleep(0.1005)
            print("load data: {}, {} / {}".format(market, i + 1, time_diff))            
            df[::-1].to_csv(os.path.join(local_path,'data',market + '.csv'), mode='w')
    return KRW_coin_dic
