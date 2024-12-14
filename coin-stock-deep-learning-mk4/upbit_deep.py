import tensorflow as tf
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import Dropout, Dense, LSTM
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm
from upbit_market import Choose_coin

def coin_train(local_path = None, coin_list = None):
    # train Parameters
    timesteps = 60
    training_data_rate = 0.7
    learning_rate = 0.001
    batch_size = 32
    epochs = 20

    KRW_coin_dic = Choose_coin(coin_list = coin_list)

    for stock in KRW_coin_dic.keys():
        df_price = pd.read_csv(os.path.join(local_path, 'data', stock + ".csv"), encoding = 'utf8')
        scaler = MinMaxScaler()
        scale_cols = df_price.columns[1:].tolist()
#        scale_cols = ['opening_price', 'high_price', 'low_price', 'trade_price', 'candle_acc_trade_volume']
        df_price[scale_cols] = df_price[scale_cols].fillna(0)
        scaled = scaler.fit_transform(df_price[scale_cols])

        train_data = scaled[:int(len(scaled) * training_data_rate)]
        test_data = scaled[int(len(scaled) * training_data_rate):]

        X_train, Y_train = [], []
        X_test, Y_test = [], []

        print("training data splitting")
        for i in tqdm(range(0, len(train_data) - timesteps)):
            X_train.append(train_data[i:i+timesteps])
            Y_train.append(train_data[i+timesteps, scale_cols.index('trade_price')])
        X_train, Y_train = np.array(X_train), np.array(Y_train)
        print("test data splitting")
        for i in tqdm(range(0, len(test_data) - timesteps)):
            X_test.append(test_data[i:i+timesteps])
            Y_test.append(test_data[i+timesteps, scale_cols.index('trade_price')])
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
        model.add(LSTM(units=256, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
        model.add(LSTM(units=256, return_sequences=False))
        model.add(Dense(units=25))
        model.add(Dense(units=1))

#        tf.keras.utils.plot_model(model, to_file=os.path.join(local_path, "model.png"), show_shapes=True, show_layer_names=True)

        model.compile(optimizer=Adam(learning_rate= learning_rate), loss='mean_squared_error')

        # earlystopping은 2번 epoch통안 val_loss 개선이 없다면 학습을 멈춥니다.
        earlystopping = EarlyStopping(monitor='val_loss', patience = 3)
        # val_loss 기준 체크포인터도 생성합니다.
        filename = os.path.join(local_path, 'checkpoint', stock + '.ckpt')
        checkpoint = ModelCheckpoint(filename, 
                                save_weights_only=True, 
                                save_best_only=True, 
                                monitor='val_loss', 
                                verbose=1)

        history = model.fit(X_train, Y_train,
                        validation_data=(X_test, Y_test),
                        epochs=epochs,
                        batch_size= batch_size,
                        callbacks=[checkpoint, earlystopping])

        fig, loss_ax = plt.subplots()
        acc_ax = loss_ax.twinx()

        loss_ax.plot(history.history['loss'], 'y', label='train loss')
        loss_ax.plot(history.history['val_loss'], 'r', label='val loss')
        loss_ax.set_xlabel('epoch')
        loss_ax.set_ylabel('loss')
        loss_ax.legend(loc='upper left')
        plt.savefig(os.path.join(local_path,"loss",  stock +  "_loss.png"))