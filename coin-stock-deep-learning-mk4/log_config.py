import logging
import os

def setup_logging():
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_directory, 'trading.log'), encoding='utf-8'),
            logging.StreamHandler()  # 콘솔 출력도 유지
        ]
    )
