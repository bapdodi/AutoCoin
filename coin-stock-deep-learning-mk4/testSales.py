import pandas as pd
from upbit import *

if __name__ == '__main__':
    file_path = "coin-stock-deep-learning-mk4\increase_rate.csv"
    data = pd.read_csv(file_path)
    balance_map = {item['currency']: item for item in get_balance}
    if(data.get('increase rate[%]')[0] > 1):
        print(place_order("KRW-BTC", "bid", price=balance_map.get('KRW')['balance'], ord_type="price"))
    else:
        print(place_order("KRW-BTC", "ask", price=balance_map.get('BTC')['balance'], ord_type="price"))