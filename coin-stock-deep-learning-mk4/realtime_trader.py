import asyncio
import websockets
import json
from upbit import place_order, get_balance
import datetime
import os
import logging
from log_config import setup_logging

setup_logging()
logger = logging.getLogger('realtime_trader')

class RealtimeTrader:
    def __init__(self, market="KRW-BTC", target_profit=None, stop_loss=None):
        self.market = market
        self.target_profit = target_profit
        self.stop_loss = stop_loss
        self.buy_price = 0
        self.trading = False
        self.reconnect_attempts = 100
        self.connection = None
        self.ping_timeout = 20
        self.ping_interval = 15
        self.reconnect_delay = 5
        
    async def connect_websocket(self):
        uri = "wss://api.upbit.com/websocket/v1"
        while self.trading:
            try:
                async with websockets.connect(
                    uri,
                    ping_interval=self.ping_interval,
                    ping_timeout=self.ping_timeout
                ) as websocket:
                    self.connection = websocket
                    subscribe_fmt = [
                        {"ticket":"UNIQUE_TICKET"},
                        {
                            "type": "ticker",
                            "codes": [self.market],
                            "isOnlyRealtime": True
                        }
                    ]
                    await websocket.send(json.dumps(subscribe_fmt))
                    
                    while True:
                        try:
                            data = await websocket.recv()
                            data = json.loads(data)
                            current_price = float(data['trade_price'])
                            current_profit = ((current_price - self.buy_price) / self.buy_price) * 100
                            os.system("cls")
                            logger.info(f"현재가: {current_price}, 상승률: {current_profit:.2f}%")

                            if current_profit >= self.target_profit:
                                logger.info(f"목표 상승률 도달 : {current_profit:.2f}%")
                                balance = get_balance()
                                balance_map = {item['currency']: item for item in balance}
                                place_order(self.market, "ask", volume=balance_map.get('BTC')['balance'], ord_type="market")
                                self.trading = False
                                break
                            
                            elif current_profit <= self.stop_loss:
                                logger.warning(f"손실가 도달 : {current_profit:.2f}%")
                                balance = get_balance()
                                balance_map = {item['currency']: item for item in balance}
                                place_order(self.market, "ask", volume=balance_map.get('BTC')['balance'], ord_type="market")
                                self.trading = False
                                break
                        
                        except websockets.exceptions.ConnectionClosed:
                            logger.warning("WebSocket 연결이 끊어졌습니다. 재연결 시도중...")
                            break
                            
            except Exception as e:
                logger.error(f"WebSocket 에러 발생: {e}")
                if not self.trading:
                    break
                await asyncio.sleep(self.reconnect_delay)
                logger.info("재연결 시도중...")
                continue

    async def cleanup(self):
        if self.connection:
            await self.connection.close()

    def start_monitoring(self, buy_price):
        self.buy_price = buy_price
        self.trading = True
        asyncio.get_event_loop().run_until_complete(self.connect_websocket())

if __name__ == "__main__":
    trader = RealtimeTrader(market="KRW-BTC", target_profit=0.25, stop_loss=-0.1)
    trader.start_monitoring(126099000) # 현재가 입력
