import requests
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

# 업비트 API 키 설정
ACCESS_KEY = "H3BlgXZi4CUAyw42K8m6siSWgHi7ObTRXgWWYmA6"
SECRET_KEY = "xTmJ7CWkGAhx3wyifn6tOMYzWSssAiTczn1xYaiN"
SERVER_URL = "https://api.upbit.com"

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
            query['price'] = str(price)
        # 매도: price 대신 volume 필요
        elif ord_type == "market" and side == "ask":
            query['volume'] = str(volume)
        # 지정가 주문: price와 volume 모두 필요
        else:
            query['volume'] = str(volume)
            query['price'] = str(price)

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




# 사용 예시
if __name__ == "__main__":
    # 계좌 잔고 조회
    balance = get_balance()
    print("잔고:", balance)

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