import os
import logging
from datetime import date


log_folder = os.path.join(os.getcwd(), 'Logs')
log_file = os.path.join(log_folder, 'Log File.txt')
today_date = date.today().strftime('%Y-%m-%d')

if not os.path.exists(log_folder):
    os.mkdir(log_folder)
handler = logging.FileHandler(os.path.join(log_folder, log_file), mode='a+', encoding='UTF-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info('-' * 100)
