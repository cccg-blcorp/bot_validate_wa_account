import os
from time import time
import logging
from urllib import request
import pandas as pd
import requests

## INPUT
FILE_NAME = 'perudata' # nombre del archivo sin la extensión

COLUMN_NUMBER = 'number'
COLUMN_WA_STATUS = 'wa_status'
COLUMN_NUMBER_STATUS = 'status'
PHONE_FILE = './{file_name}.csv'.format(file_name=FILE_NAME)
TIME_VALUE = time()
SELENIUM_PORT = 9515
URL = "http://localhost:5555/whatsapp/?phone={phone}"

def validate_account(phone):
    response = requests.get(URL.format(phone = phone))
    if response.status_code == 200:
        return response.json()['result']

def save_file(file_name, data, status_data):
    data[COLUMN_WA_STATUS] = status_data
    data[[COLUMN_NUMBER, COLUMN_WA_STATUS]].to_csv(file_name, index=False)
    print(file_name)

root_path=os.path.dirname(__file__)

df = pd.read_csv(PHONE_FILE, encoding='UTF-8', sep=',', dtype = str)
df = df[df[COLUMN_NUMBER_STATUS] == "True"]
count_processed = 0
count_valid = 0

wa_status = []
t1_start = time()
print("Se inicia proceso de validación de wa ...")
for index, row in df.iterrows():
    result = validate_account(row[COLUMN_NUMBER].replace('+', ''))
    count_processed = count_processed + 1
    if result:
        count_valid = count_valid + 1
    if count_processed % 100 == 0:
        print("Se validaron {fila} números de {total} y {cantidad} tienen wa".format(fila=count_processed, cantidad=count_valid, total = len(df)))
    wa_status.append(result)

t1_stop = time()
logging.basicConfig(filename="{time_exec}-proccess.log".format(time_exec = TIME_VALUE), level=logging.INFO)
logging.info("Tiempo de ejecucion: {execution_duration} (seg)".format(execution_duration = t1_stop-t1_start)) 
print("Proceso terminado con {fila} registros procesados y {cantidad} cuentas de whatsapp validas".format(fila=count_processed, cantidad=count_valid))
save_file('processed_{file_name}.csv'.format(file_name= FILE_NAME), df, wa_status)
# print("Se encontró que el {:.0%} de contactos tienen whatsapp".format((count_valid/count_processed)))

