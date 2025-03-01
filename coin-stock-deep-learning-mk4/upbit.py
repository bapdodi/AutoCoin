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



# 프로그램 시작 -> 현재 지갑 확인 -> 현재 투자중인 코인이 있는지?
# 투자중이면 계속 그거 써
# 아니면 새 투자 시작 -> 학습 시작 -> 정해진 코인(5개) 중 예측상승률이 가장 높은 코인에 전량 매수





# 업비트 API 키 설정
ACCESS_KEY = "SgbY6dhLItWDn1q0hsTLxH9Y4FXj1vxKYjsH0wQM"
SECRET_KEY = "AgQLDdNvp8GY3Jb5hJ2Wc4pJHq6JWp1LqOtyY61E"
SERVER_URL = "https://api.upbit.com"

# 현재 투자중인 코인
CURRENT_COIN = None
CURRENT_STATUS = 'IDLE'
LAST_RESULT = None

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
        print(f"잔고 조회 중 오류 발생: {e}")
        return None

def place_order(market, side, volume, price, ord_type="limit"):
    """주문을 실행한다."""
    try:
        query = {
            'market': market,
            'side': side,  # 'bid' for buy, 'ask' for sell
            'volume': str(volume),
            'price': str(price),
            'ord_type': ord_type,
        }

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
        return response.json()
    except Exception as e:
        print(f"주문 중 오류 발생: {e}")
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

        print(query)

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
        return response.json()
    except Exception as e:
        print(f"주문 중 오류 발생: {e}")
        return None

def 작업_시작():
    upbit_main()
    print("\n\n학습 완료")
    os.system("cls")

    file_path = ".\increase_rate.csv"
    data = pd.read_csv(file_path)
    balance_map = {item['currency']: item for item in get_balance()}
    if(data.get('increase rate[%]')[0] > 0.25):
        print(place_order("KRW-BTC", "bid", price=balance_map.get('KRW')['balance'], ord_type="price")) # 매수
        return '매수'
    else:
        print(place_order("KRW-BTC", "ask", volume=balance_map.get('BTC')['balance'], ord_type="market")) # 매도
        return '매도'



def 씨발():
    print("실행됨")
        
async def upbit_websocket():
    url = "wss://api.upbit.com/websocket/v1"
    subscribe_message = [
        {
            "ticket": "UNIQUE_TICKET",
            "type": "ticker",
            "codes": ["KRW-BTC"],  # 구독할 코인 심볼
        }
    ]
    
    async with websockets.connect(url) as websocket:
        # 구독 메시지 전송
        await websocket.send(json.dumps(subscribe_message))
        
        while True:
            # 서버로부터 메시지 수신
            message = await websocket.recv()
            data = json.loads(message)
            print(data)
            for ticker_data in data:
                code = ticker_data['code']  # 코인 심볼
                price = ticker_data.get('trade_price', 0)  # 현재가
                print(f"코드: {code}, 현재가: {price}") 


# 사용 예시
if __name__ == "__main__":
    print("봇 시작됨")
    # time.sleep(2)
    # 계좌 잔고 조회
    # print(get_balance())
    # # upbit_main()
    # balance_map = {item['currency']: item for item in get_balance()}
    # print(balance_map.get('KRW')['balance'])
    # file_path = "coin-stock-deep-learning-mk4\increase_rate.csv"
    # data = pd.read_csv(file_path)
    # 지갑 = get_balance()
    # for temp in 지갑:
    #     if not temp['currency'] == 'KRW' and not temp['currency'] == 'SRN':
    #         CURRENT_COIN = temp['currency']
    #         CURRENT_STATUS = 'BUY'
    #         print(f'현재 매수중인 코인 :', CURRENT_COIN)

    # if CURRENT_COIN == None:
    #     print('현재 투자중인 코인이 없음')

    # schedule.every(1).seconds.do(씨발)
    # 작업_시작()
    # CURRENT_COIN = 'KRW-BTC'
    # while True:
    #     # schedule.run_pending()
    #     os.system('cls')
    #     now = datetime.now()
    #     print(f'{now}\n{CURRENT_COIN} / {CURRENT_STATUS}\n마지막 판단 : {LAST_RESULT}')
    #     if now.minute == 0 and now.second == 0:
    #         LAST_RESULT = 작업_시작()

    #     time.sleep(1)
    
    # 이벤트 루프 실행
    asyncio.run(upbit_websocket())
    # # 매수 주문 (BTC-KRW 시장에서 0.001 BTC를 50,000,000 KRW에 구매)
    # buy_result = place_order("KRW-BTC", "bid", 0.001, 50000000)
    # print("매수 결과:", buy_result)

    # # 매도 주문 (BTC-KRW 시장에서 0.001 BTC를 55,000,000 KRW에 판매)
    # sell_result = place_order("KRW-BTC", "ask", 0.001, 55000000)
    # print("매도 결과:", sell_result)

    # # 현재 시장 가격에 매수 (50,000 KRW만큼 BTC를 매수)
    # buy_market_result = place_order("KRW-BTC", "bid", price=50000, ord_type="price")
    # print("시장가 매수 결과:", buy_market_result)

    # # 현재 시장 가격에 매도 (0.001 BTC를 시장가로 매도)
    # sell_market_result = place_order("KRW-BTC", "ask", volume=0.001, ord_type="market")
    # print("시장가 매도 결과:", sell_market_result)