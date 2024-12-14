import os
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import datetime
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import Dropout, Dense, LSTM
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm
from upbit_market import Choose_coin

def coin_predict(local_path = None, coin_list = None):
    # train Parameters
    timesteps = 60
    training_data_rate = 0.7
    KRW_coin_dic = Choose_coin(coin_list = coin_list)

    result_increase_rate = []
    for stock in KRW_coin_dic.keys():
        df_price = pd.read_csv(os.path.join(local_path, 'data', stock + ".csv"), encoding = 'utf8')
        scaler = MinMaxScaler()
        scale_cols = df_price.columns[1:].tolist()
        df_price[scale_cols] = df_price[scale_cols].fillna(0)
        scaled = scaler.fit_transform(df_price[scale_cols])

        test_data = scaled[int(len(scaled) * training_data_rate):]
        X_test, Y_test = [], []
        print("test data splitting")
        for i in tqdm(range(0, len(test_data) - timesteps)):
            X_test.append(test_data[i:i+timesteps])
            Y_test.append(test_data[i+timesteps, scale_cols.index('trade_price')])
        X_test.append(test_data[-timesteps:])
        X_test, Y_test = np.array(X_test), np.array(Y_test)
        print("data split done")

        """
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dense(units=25))
        model.add(Dense(units=1))
        """
        model = Sequential()
        model.add(LSTM(units=256, return_sequences=True, input_shape=(X_test.shape[1], X_test.shape[2])))
        model.add(LSTM(units=256, return_sequences=False))
        model.add(Dense(units=25))
        model.add(Dense(units=1))
#        model.compile(optimizer=Adam(learning_rate= learning_rate), loss='mean_squared_error')


        filename = os.path.join(local_path, "checkpoint", stock + '.ckpt')
        try:
            model.load_weights(filename)
        except:
            print(filename + "존재하지 않습니다.")

        pred = model.predict(X_test)
        timeline = df_price.iloc[int(len(scaled) * training_data_rate):,0].values.tolist()
        timeline = [date[:10] for date in timeline]
        timeline.append((datetime.date(int(timeline[-1][:4]), int(timeline[-1][5:7]), int(timeline[-1][-2:])) + datetime.timedelta(days= 1)).strftime('%Y-%m-%d %H:%M:%S')[:10])

        Y_test = np.append(Y_test, Y_test[-1])

        fig, ax=plt.subplots(1,1)
        plt.title(stock)
        plt.xlabel('date')
        ax.plot(timeline[timesteps:],pred, label='pred')
        ax.plot(timeline[timesteps:],Y_test, 'k-', label='real')
        ax.plot([timeline[-2], timeline[-1]], [pred[-2], pred[-1]], 'r-')
        ax.plot([timeline[-2], timeline[-1]], [Y_test[-2], Y_test[-1]], 'w')
        fig.autofmt_xdate(rotation=45)
        for i, tick in enumerate(ax.xaxis.get_ticklabels()):
            tick.set_visible(False)
            if i % int(len(timeline) / 10) == 0 or i == (len(timeline[timesteps:]) - 1):
                tick.set_visible(True)
                plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.5)
        plt.legend()
#        plt.show()
        plt.savefig(os.path.join(local_path, "pred", stock +  "_pred.png"))
        result_increase_rate.append(((pred[-1] - pred[-2]) / pred[-2]) * 100)

    df = pd.DataFrame()
    df = pd.concat([df, pd.DataFrame(result_increase_rate, columns= ["increase rate[%]"], index=KRW_coin_dic.keys())])
    df.to_csv(os.path.join(local_path, 'increase_rate.csv'), mode='w')
