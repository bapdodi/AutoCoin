import numpy as np
import pandas as pd
import tensorflow as tf
import datetime
import os
from sklearn.preprocessing import MinMaxScaler
from upbit_market import get_new_data_sequence

# GPU 설정
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print("GPU is available")
    tf.config.experimental.set_memory_growth(gpus[0], True)
else:
    print("GPU is not available")

# 학습된 모델 로드 함수
def load_model(local_path, stock):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input(shape=(60, 6)))  # 예시 입력 크기 (timesteps=60, features=6)
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
    return model

# 새로운 데이터 예측 함수
def predict_new_data(local_path, stock, new_data_sequence):
    # 모델 로드
    model = load_model(local_path, stock)

    # 기존 학습에 사용된 스케일러를 불러오고, 새 데이터에 동일한 변환을 적용해야 합니다.
    # 학습 시에 사용된 scaler를 저장했다면, 이를 로드하여 사용해야 합니다.
    scaler = MinMaxScaler()
    scaler.fit(new_data_sequence)  # 학습된 scaler가 있다면 여기서 적용
    new_data_scaled = scaler.transform(new_data_sequence)  # 학습 시와 동일한 방식으로 변환
    
    # 예측 (입력 데이터를 (1, timesteps, features) 형태로 변환)
    new_data_scaled = np.array([new_data_scaled])  # (1, timesteps, features)
    prediction = model.predict(new_data_scaled)

    return prediction

# 예측 실행
stock = 'KRW-BTC'  # 예시: 예측하려는 코인
local_path = './'  # 실제 경로로 변경
new_data_sequence = get_new_data_sequence(stock)

prediction = predict_new_data(local_path, stock, new_data_sequence)
print(f"새로운 데이터에 대한 예측값: {prediction}")
