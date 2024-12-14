import tensorflow as tf

# GPU가 인식되지 않더라도 강제로 GPU 설정
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    tf.config.set_visible_devices(physical_devices[0], 'GPU')
    print("GPU is being used.")
else:
    print("GPU is not available.")