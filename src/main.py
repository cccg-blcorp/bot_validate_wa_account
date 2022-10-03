import os
from time import time
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as chrome_options
from selenium.webdriver.firefox.options import Options as firefox_options
from selenium.webdriver.common.by import By
import pandas as pd

## INPUT
FILE_NAME = 'perudata' # nombre del archivo sin la extensión
save_screen = True  # flag para activar la captura de pantalla de cada validación


SELENIUM_SESSION_FILE_CHROME = './selenium_session_chrome.dat'
SELENIUM_SESSION_FILE_FIREFOX = './selenium_session_firefox.dat'
COLUMN_NUMBER = 'number'
COLUMN_WA_STATUS = 'wa_status'
COLUMN_NUMBER_STATUS = 'status'
PHONE_FILE = './{file_name}.csv'.format(file_name=FILE_NAME)
TIME_VALUE = time()
SELENIUM_PORT = 9515
URL = "https://web.whatsapp.com/send?phone={phone}"

def build_driver_chrome():
    options = chrome_options()
    options.add_argument("--disable-infobars")
    options.add_argument("--enable-file-cookies")

    if os.path.isfile(SELENIUM_SESSION_FILE_CHROME):
        session_file = open(SELENIUM_SESSION_FILE_CHROME)
        session_info = session_file.readlines()
        session_file.close()

        executor_url = session_info[0].strip()
        session_id = session_info[1].strip()

        capabilities = options.to_capabilities()
        driver = webdriver.Remote(
            command_executor=executor_url, desired_capabilities=capabilities)
        driver.close()
        driver.quit()

        driver.session_id = session_id
        return driver

    driver = webdriver.Chrome(options=options, port=SELENIUM_PORT)

    session_file = open(SELENIUM_SESSION_FILE_CHROME, 'w')
    session_file.writelines([
        driver.command_executor._url,
        "\n",
        driver.session_id,
        "\n",
    ])
    session_file.close()

    return driver

def validate_account(driver, phone, save_screen, valid_folder, invalid_folder):
    validation = True
    try:
        message = "El número de teléfono compartido a través de la dirección URL es inválido".lower()
        driver.get(URL.format(phone=phone))
        delay = 10
        item = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/div[1]')))
        result = item.text.strip().lower()
        logging.info('resultado find: {text_path}'.format(text_path = item.text))
        
        if result == message:
            if save_screen:
                driver.save_screenshot("{folder}/image_{number}.png".format(folder=invalid_folder, number = phone))
            logging.info('el numero {number} NO tiene wa \n{url}'.format(number = phone, url= URL.format(phone=phone)))
            validation = False            
        else:
            if save_screen:
                driver.save_screenshot("{folder}/image_{number}.png".format(folder=valid_folder, number = phone))
            logging.info('el numero {number} SI tiene wa'.format(number = phone))            
    except Exception as e:
        if save_screen:
            driver.save_screenshot("{folder}/image.png".format(folder=valid_folder))
        logging.info('el numero {number} SI tiene wa'.format(number = phone))
    finally:
        return validation

def save_file(file_name, data, status_data, status_colum):
    data[status_colum] = status_data
    data[[COLUMN_NUMBER,status_colum]].to_csv(file_name, index=False)

root_path=os.path.dirname(__file__)
folder_name = '{file}_{time}'.format(file = FILE_NAME, time = TIME_VALUE)
os.mkdir('{base_dir}/img/{folder}'.format(base_dir= root_path,folder=folder_name))
invalid_folder = '{base_dir}/img/{folder}/invalid'.format(base_dir= root_path,folder=folder_name)
valid_folder = '{base_dir}/img/{folder}/valid'.format(base_dir= root_path,folder=folder_name)
os.mkdir(invalid_folder)
os.mkdir(valid_folder)
df = pd.read_csv(PHONE_FILE, encoding='UTF-8', sep=',', dtype = str)
df = df[df[COLUMN_NUMBER_STATUS] == "True"]
count_processed = 0
count_valid = 0

if os.path.isfile(SELENIUM_SESSION_FILE_CHROME):
    driver_chrome = build_driver_chrome()
    logging.basicConfig(filename="{time_exec}-proccess.log".format(time_exec = TIME_VALUE), level=logging.INFO)
    wa_status = []
    t1_start = time()
    print("Se inicia proceso de validación de wa ...")
    for index, row in df.iterrows():
        result = validate_account(driver_chrome, row[COLUMN_NUMBER], save_screen, valid_folder, invalid_folder)
        wa_status.append(result)
        if result:
            count_valid = count_valid + 1
        count_processed = count_processed + 1
        if count_processed % 10 == 0:
            print("Se validaron {fila} números de {total} y {cantidad} tienen wa".format(
            fila=count_processed, cantidad=count_valid, total = len(df)))
        if count_processed % 500 == 0:
            temp = df.iloc[0:count_processed,]
            save_file('processed_{file_name}.csv'.format(file_name= FILE_NAME), temp, wa_status, COLUMN_WA_STATUS)
    save_file('processed_{file_name}.csv'.format(file_name= FILE_NAME), df, wa_status, COLUMN_WA_STATUS)
    t1_stop = time()
    logging.info("Tiempo de ejecucion: {execution_duration} (seg)".format(execution_duration = t1_stop-t1_start)) 
    print("Proceso terminado con {fila} registros procesados y {cantidad} cuentas de whatsapp validas".format(fila=count_processed, cantidad=count_valid))
    print("Se encontró que el {:.0%} de contactos tienen whatsapp".format((count_valid/count_processed)))
else:
    url = "https://web.whatsapp.com/"
    driver_chrome = build_driver_chrome()
    driver_chrome.get(url)
