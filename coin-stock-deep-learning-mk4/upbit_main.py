import os
import tensorflow as tf
import logging
from log_config import setup_logging
from upbit_market import get_coin_data
from upbit_deep import coin_train
from upbit_deep_test import coin_predict

# 시작 부분에 로깅 설정 추가
setup_logging()
logger = logging.getLogger('upbit_main')

tf.keras.backend.clear_session()
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True


def upbit_main():
    local_path = os.getcwd()
    coin_list_path = os.path.join(local_path, ".\coin_list.txt")
    if os.path.isfile(coin_list_path) is False:
        logger.error(f"coin_list.txt 파일이 존재하지 않습니다: {coin_list_path}")
        exit('coin_list.txt file does not exist.')
    f = open(coin_list_path, 'r', encoding='UTF8')
    lines = f.readlines()
    coin_list = []
    for line in lines:
        for coin in line.split():
            coin_list.append(coin)
    f.close()

    get_coin_data(local_path = local_path, start_day="20170901", step = 'minute60', coin_list = coin_list)
    coin_train(local_path = local_path, coin_list = coin_list)
    coin_predict(local_path= local_path, coin_list = coin_list) 

if __name__ == "__main__":
    upbit_main()