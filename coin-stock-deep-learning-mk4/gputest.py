import tensorflow as tf
import numpy as np

# TensorFlow 버전 출력
print("TensorFlow version:", tf.__version__)

# GPU 사용 가능 여부 확인
print("GPU Available: ", tf.config.list_physical_devices('GPU'))
print("GPU Devices: ", tf.config.experimental.list_physical_devices('GPU'))

# GPU 테스트를 위한 간단한 행렬 연산
with tf.device('/GPU:0'):
    # 큰 행렬 생성
    a = tf.random.normal([10000, 10000])
    b = tf.random.normal([10000, 10000])
    
    # 행렬 곱 연산 시간 측정
    import time
    start = time.time()
    c = tf.matmul(a, b)
    end = time.time()
    
    print("\nMatrix multiplication test:")
    print(f"Time taken: {end - start:.2f} seconds")
    print("Shape of result:", c.shape)
