from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chrome_options
from selenium.webdriver.firefox.options import Options as firefox_options
from selenium.webdriver.common.by import By
import os
import time
import pandas as pd

SELENIUM_SESSION_FILE_CHROME = './selenium_session_chrome'
SELENIUM_SESSION_FILE_FIREFOX = './selenium_session_firefox'
PHONE_FILE = './data.csv'
SELENIUM_PORT=9515

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
        driver = webdriver.Remote(command_executor=executor_url, desired_capabilities=capabilities)
        # prevent annoying empty chrome windows
        driver.close()
        driver.quit() 

        # attach to existing session
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

def build_driver_firefox():
    options = firefox_options()
    print(options.to_capabilities())
    options.add_argument("--disable-infobars")
    options.add_argument("--enable-file-cookies")

    if os.path.isfile(SELENIUM_SESSION_FILE_FIREFOX):
        session_file = open(SELENIUM_SESSION_FILE_FIREFOX)
        session_info = session_file.readlines()
        session_file.close()
        executor_url = session_info[0].strip()
        session_id = session_info[1].strip()

        # capabilities = options.to_capabilities()
        driver = webdriver.Remote(command_executor=executor_url+'/', options=options)
        # prevent annoying empty chrome windows
        driver.close()
        driver.quit() 

        # attach to existing session
        driver.session_id = session_id
        return driver

    driver = webdriver.Firefox(options=options,)

    session_file = open(SELENIUM_SESSION_FILE_FIREFOX, 'w')
    session_file.writelines([
        driver.command_executor._url,
        "\n",
        driver.session_id,
        "\n",
    ])
    session_file.close()

    return driver

def validate_message(driver, phone):
    url = "https://web.whatsapp.com/send?phone={phone}"
    message = "'El número de teléfono compartido a través de la dirección URL es inválido'"
    driver.get(url.format(phone = phone))
    time.sleep(4)
    item = driver.find_element(By.XPATH, value='//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/div[1]')
    result = item.text
    # print(result)
    not_valid = result in message
    return not_valid


df = pd.read_csv(PHONE_FILE)
print(df)
count = 0
if os.path.isfile(SELENIUM_SESSION_FILE_CHROME) and os.path.isfile(SELENIUM_SESSION_FILE_FIREFOX):
    driver_chrome = build_driver_chrome()
    wa_status = []
    for index, row in df.iterrows():
        result = validate_message(driver_chrome, row['phone'])
        wa_status.append(result)
        if not result:
            count = count + 1
        print("Se validaron {fila} números y {cantidad} tienen wa".format(fila = index + 1, cantidad = count))
    df['wa_status'] = wa_status
    df.to_csv('processed_data.csv')
    # driver_firefox = build_driver_firefox()
    # result = validate_message(driver_firefox, '+51123456789')
    # print(result)
else:
    url = "https://web.whatsapp.com/"
    driver_chrome = build_driver_chrome()
    driver_chrome.get(url)
    # driver_firefox = build_driver_firefox()
    # driver_firefox.get(url)

