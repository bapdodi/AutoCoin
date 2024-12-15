import numpy as np
import pandas as pd
import tensorflow as tf
import os
from sklearn.preprocessing import MinMaxScaler
from upbit_market import get_data

# 학습된 모델 로드 함수
def load_model(local_path, stock):
    """
    학습된 모델을 로드하는 함수
    """
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input(shape=(60, 6)))  # 입력 형태: (timesteps=60, features=6)
    model.add(tf.keras.layers.LSTM(units=256, return_sequences=True))
    model.add(tf.keras.layers.LSTM(units=256, return_sequences=False))
    model.add(tf.keras.layers.Dense(units=25))
    model.add(tf.keras.layers.Dense(units=1))
    
    # 모델 가중치 로딩
    filename = os.path.join(local_path, "checkpoint", stock + '.weights.h5')
    try:
        model.load_weights(filename)
        print(f"{stock} 모델 가중치 로딩 성공")
    except Exception as e:
        print(f"모델 로드 실패: {e}")
        return None
    return model

# 새로운 데이터 예측 함수
def predict_new_data(local_path, stock, new_data_sequence):
    """
    새로운 데이터를 예측하는 함수
    """
    print(new_data_sequence)
    # 모델 로드
    model = load_model(local_path, stock)
    if model is None:
        return None

    # 예측 수행
    prediction = model.predict(new_data_sequence)
    return prediction

# 예측 실행 예시
stock = 'KRW-BTC'  # 예시: 예측하려는 코인
local_path = './'  # 실제 경로로 변경
new_data_sequence = get_data(stock)  # 새로운 데이터 불러오기

# 예측 실행
prediction = predict_new_data(local_path, stock, new_data_sequence)
if prediction is not None:
    print(f"새로운 데이터에 대한 예측값: {prediction}")
else:
    print("예측을 수행할 수 없습니다.")
