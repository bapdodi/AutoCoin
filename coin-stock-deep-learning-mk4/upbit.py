import requests
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
from upbit_main import *
import pandas as pd
import schedule
import time
from datetime import datetime
import os
import math
import asyncio
import websockets
import json
import configparser
import logging
from log_config import setup_logging

# logging 설정 수정
setup_logging()
logger = logging.getLogger('upbit')

# API 키를 config.ini 파일에서 읽도록 수정
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')

if not os.path.exists(config_path):
    logger.error(f"config.ini 파일을 찾을 수 없습니다. 경로: {config_path}")
    raise FileNotFoundError("config.ini 파일이 없습니다.")

config.read(config_path, encoding='utf-8')

try:
    ACCESS_KEY = config.get('UPBIT', 'ACCESS_KEY')
    SECRET_KEY = config.get('UPBIT', 'SECRET_KEY')
except configparser.NoSectionError:
    logger.error("config.ini 파일에 [UPBIT] 섹션이 없습니다.")
    raise
except configparser.NoOptionError as e:
    logger.error(f"config.ini 파일에 필요한 설정이 없습니다: {str(e)}")
    raise

SERVER_URL = "https://api.upbit.com"

# API 키 검증
if ACCESS_KEY == "YOUR_ACCESS_KEY_HERE" or SECRET_KEY == "YOUR_SECRET_KEY_HERE":
    logger.error("config.ini 파일에 실제 API 키를 입력해주세요.")
    raise ValueError("API 키가 설정되지 않았습니다. config.ini 파일을 확인해주세요.")

def get_balance():
    """계좌 잔고를 조회한다."""
    try:
        payload = {
            'access_key': ACCESS_KEY,
            'nonce': str(uuid.uuid4()),
        }
        jwt_token = jwt.encode(payload, SECRET_KEY)
        headers = {"Authorization": f"Bearer {jwt_token}"}

        response = requests.get(f"{SERVER_URL}/v1/accounts", headers=headers)
        return response.json()
    except Exception as e:
        logger.error(f"잔고 조회 중 오류 발생: {e}")
        return None

def place_order(market, side, volume=None, price=None, ord_type="limit"):
    """
    주문을 실행한다.
    시장 가격에 매수하려면 'ord_type'을 'price'로 설정하고, 'price'에 사용할 금액을 입력.
    시장 가격에 매도하려면 'ord_type'을 'market'으로 설정하고, 'volume'만 입력.
    """
    try:
        query = {
            'market': market,
            'side': side,  # 'bid' for buy, 'ask' for sell
            'ord_type': ord_type,
        }

        # 매수: volume 대신 price 필요
        if ord_type == "price" and side == "bid":
            query['price'] = str(float(price) - float(price) * 0.05 / 100)
        # 매도: price 대신 volume 필요
        elif ord_type == "market" and side == "ask":
            query['volume'] = str(float(volume))
        # 지정가 주문: price와 volume 모두 필요
        else:
            query['volume'] = str(float(volume))
            query['price'] = str(float(price) - float(price) * 0.05 / 100)

        logger.info(f"주문 정보: {query}")

        query_string = urlencode(query).encode()
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': ACCESS_KEY,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, SECRET_KEY)
        headers = {"Authorization": f"Bearer {jwt_token}"}

        response = requests.post(f"{SERVER_URL}/v1/orders", params=query, headers=headers)
        if response.status_code != 200:
            logger.error(f"주문 실패: {response.text}")
            return None
        logger.info(f"주문 성공: {response.json()}")
        return response.json()
    except Exception as e:
        logger.error(f"주문 중 오류 발생: {e}")
        return None

def get_current_price(market):
    url = f"https://api.upbit.com/v1/trades/ticks?market={market}&count=1"
    response = requests.get(url)
    return float(response.json()[0]['trade_price'])

def 작업_시작():
    upbit_main()
    logger.info("학습 완료")
    os.system("cls")

    file_path = ".\increase_rate.csv"
    data = pd.read_csv(file_path)
    balance_map = {item['currency']: item for item in get_balance()}
    
    if(data.get('increase rate[%]')[0] >= 0.25):
        current_price = get_current_price("KRW-BTC")
        logger.info(f"매수 시작 (예측상승률: {data.get('increase rate[%]')[0]}%) - 현재가: {current_price}")
        
        # 매수 주문
        place_order("KRW-BTC", "bid", price=balance_map.get('KRW')['balance'], ord_type="price")
        
        # 실시간 모니터링 시작
        from realtime_trader import RealtimeTrader
        trader = RealtimeTrader(market="KRW-BTC", target_profit=0.25, stop_loss=-0.5)
        trader.start_monitoring(current_price)
        return True
    else:
        logger.info(f"매수 조건이 충족되지 않음 (예측상승률: {data.get('increase rate[%]')[0]}%)")
        return False

# 사용 예시
if __name__ == "__main__":
    logger.info("**** 봇 시작됨 ****")
    logger.info("매 시간 정각에 작업을 시작합니다...")
    
    # 매 시간 정각에 작업_시작 함수 실행
    schedule.every().hour.at(":00").do(작업_시작)
    # 작업_시작()
    
    # 스케줄러 실행
    while True:
        schedule.run_pending()
        time.sleep(1)