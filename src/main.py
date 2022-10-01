from selenium import webdriver

driver = webdriver.Chrome()

executor_url = driver.command_executor._url
session_id = driver.session_id
driver.get("https://github.com/Ankit404butfound/PyWhatKit/blob/master/pywhatkit/whats.py")

print(session_id)
print(executor_url)

def create_driver_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver

driver2 = create_driver_session(session_id, executor_url)
print(driver2.current_url)

# url = driver.command_executor._url       #"http://127.0.0.1:60622/hub"
# session_id = driver.session_id            #'4e167f26-dc1d-4f51-a207-f761eaf73c31'
# driver.get(url = 'https://web.whatsapp.com/send?phone=+51123456789')

# print(session_id)
# print(url)


# driver2 = webdriver.Remote(command_executor=url,desired_capabilities={})
# # driver.close()   # this prevents the dummy browser
# driver2.session_id = session_id
# print(driver2.current_url)
# print(driver2.session_id)

# # item = driver.find_element_by_class_name('_2Nr6U')
# # print(item)
# # popup-contents
