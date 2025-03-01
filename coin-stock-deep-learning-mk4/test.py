import jwt  # PyJWT
import uuid
import websocket  # websocket-client
import json

def on_message(ws, message):
    # do something
    print(message)
    data = message.decode('utf-8')
    print(data)


def on_connect(ws):
    print("connected!")
    # Request after connection
    # 웹소켓 연결 시 구독 메시지 전송
    # subscribe_message = [
    #     {
    #         "ticket": "UNIQUE_TICKET",
    #         "type": "ticker",
    #         "codes": ["KRW-BTC", "KRW-ETH"],  # 구독할 코인 심볼
    #         "is_only_realtime": True
    #     }
    # ]
    # ws.send(json.dumps(subscribe_message))
    ws.send('[{"ticket":"test example"},{"type":"ticker"},{"codes": "KRW-BTC"}]')


def on_error(ws, err):
    print(err)


def on_close(ws, status_code, msg):
    print("closed!")


payload = {
    'access_key': "SgbY6dhLItWDn1q0hsTLxH9Y4FXj1vxKYjsH0wQM",
    'nonce': str(uuid.uuid4()),
}

jwt_token = jwt.encode(payload, "AgQLDdNvp8GY3Jb5hJ2Wc4pJHq6JWp1LqOtyY61E")
authorization_token = 'Bearer {}'.format(jwt_token)
headers = {"Authorization": authorization_token}

ws_app = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1/private",
                                header=headers,
                                on_message=on_message,
                                on_open=on_connect,
                                on_error=on_error,
                                on_close=on_close)
ws_app.run_forever()