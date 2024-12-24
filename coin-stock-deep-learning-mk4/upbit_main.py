

import os
import tensorflow as tf
from upbit_market import get_coin_data
from upbit_deep import coin_train
from upbit_deep_test import coin_predict
tf.keras.backend.clear_session()
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True

if __name__ == '__main__':
    local_path = os.getcwd()
    coin_list_path = os.path.join(local_path, "./coin_list.txt")
    if os.path.isfile(coin_list_path) is False:
        print(coin_list_path)
        exit('coin_list.txt file does not exist.')
    f = open(coin_list_path, 'r', encoding='UTF8')
    lines = f.readlines()
    coin_list = []
    for line in lines:
        for coin in line.split():
            coin_list.append(coin)
    f.close()
    get_coin_data(local_path = local_path, start_day="20170901", step = 'days', coin_list = coin_list)
    coin_train(local_path = local_path, coin_list = coin_list)
    coin_predict(local_path= local_path, coin_list = coin_list) 
    
