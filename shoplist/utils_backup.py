from datetime import date, datetime
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


def get_session_info(target_date: date) -> list:

    if ('RENDER' not in os.environ):  # local development
        print("[utils.get_session_info]: initiated on LOCAL...")
        load_dotenv()
    else:
        print("[utils.get_session_info]: initiated on RENDER...")

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://mickeycafe19.vrich619.com/sale')

    input_user = driver.find_element(By.NAME, 'username')
    input_user.send_keys(os.environ['VRICH_USER'])
    input_pass = driver.find_element(By.NAME, 'password')
    input_pass.send_keys(os.environ['VRICH_PASS'])
    button = driver.find_element(
        By.XPATH, '//button[text()=\'Sign In\']')
    button.click()
    print('[utils.get_session_info]: logging in...')

    # toggle sales-monitor view
    wait = WebDriverWait(driver, timeout=10)
    wait.until(lambda d: d.find_element(By.ID, 'product-list'))
    is_product_list = driver.find_element(By.ID, 'product-list').is_displayed()
    if (is_product_list):
        print('[utils.get_session_info]: toggle sales monitor view...')
        monitor_toggle = driver.find_element(By.ID, 'monitor-toggle')
        if (monitor_toggle):
            print('[utils.get_session_info]: monitor toggle button located...')
            monitor_toggle.click()
            print('[utils.get_session_info]: monitor toggle button clicked...')

    sale_date_ele = driver.find_element(By.ID, 'search_date')
    date_str = sale_date_ele.get_attribute('value')
    target_date_str = target_date.strftime("%d/%m/%Y")

    wait.until(lambda d: d.find_element(
        By.XPATH, '//li[@class=\'monitor-item\'][1]').is_displayed())

    first_item_id = driver.find_element(
        By.XPATH, '//li[@class=\'monitor-item\'][1]').get_attribute('id')

    # sale_date is the most recent
    if (target_date_str == date_str):
        print('[utils.get_session_info]: sale date correct, continue...')
    else:
        print('[utils.get_session_info]: changing sale date...')
        sale_date_ele.clear()
        sale_date_ele.send_keys(target_date_str)
        sale_date_ele.send_keys(Keys.ENTER)
        # # this button indicate sale date has changed
        # wait.until_not(lambda d: d.find_element(
        #     By.XPATH, '//button[@id=\'add_from_stock\']').is_displayed())

        wait.until(lambda d: d.find_element(
            By.XPATH, '//li[@class=\'monitor-item\'][1]').get_attribute('id') != first_item_id)
        # driver.save_screenshot('./image1_5.png')
    '''
    VERSION 4: After long session of XPath tutorial/ This still barely work on 512 MB memory server, working fine on localhost.
    '''
    # # iterate one by one
    # output = []
    # idx = 1
    # while (True):
    #     try:
    #         item = driver.find_element(
    #             By.XPATH, f'//li[@class=\'monitor-item\'][{idx}]')
    #     except NoSuchElementException:
    #         print(
    #             f'[utils.get_session_info]: Hit break NoSuchElementException idx={idx}...')
    #         break

    #     is_hide = item.get_attribute('hide')
    #     if not is_hide:
    #         code = item.get_attribute('data-code')
    #         caption = item.get_attribute('data-description')
    #         count = item.get_attribute('data-details_count')
    #         output.append((code, caption, count))
    #         print(f'[utils.get_session_info]: adding{(code, caption, count)}')
    #     idx += 1

    # print(f'[utils.get_session_info]: Total output = {len(output)}')

    '''
    VERSION 3: Refined version 1 -> Still not good enough
    '''
    # wait = WebDriverWait(driver, timeout=10)
    # wait.until(lambda d: len(d.find_elements(By.CLASS_NAME, 'code'))
    #            > 2)  # 2 .code elements already existed as table head

    # codes = driver.find_elements(By.CLASS_NAME, 'code')[2:]
    # remains = driver.find_elements(By.CLASS_NAME, 'remain')[1:]
    # print(
    #     f'[utils.get_session_info]: Total .code elements found = {len(codes)}')
    # output = []
    # for i in range(len(codes)):
    #     if codes[i].text and remains[i].text:
    #         code_des = codes[i].text.strip().split()
    #         code = code_des[0].strip('!')  # sometime code contain '!' in VRIch
    #         description = ' '.join(code_des[1:])
    #         count = remains[i].text.split()[0]
    #         output.append((code, description, count))
    #         print(
    #             f'[utils.get_session_info]: adding{(code, description, count)}')
    #         # driver.save_screenshot('./image2.png')  # screenshot
    # print(f'[utils.get_session_info]: Total output = {len(output)}')

    '''
    VERSION 2: take too much memory server cannot run
    '''
    # wait = WebDriverWait(driver, timeout=10)
    # wait.until(lambda d: len(d.find_elements(
    #     By.CLASS_NAME, 'monitor-item')) > 1)

    monitor_items = driver.find_elements(
        By.XPATH, '//li[@class=\'monitor-item\']')
    print(
        f'[utils.get_session_info]: Total monitor-items found = {len(monitor_items)}')
    # driver.save_screenshot('./image2.png')  # screenshot

    output = []
    for monitor_item in monitor_items:
        # is_hide = monitor_item.get_attribute('hide')
        # if not is_hide:
        code = monitor_item.get_attribute('data-code')
        caption = monitor_item.get_attribute('data-description')
        count = monitor_item.get_attribute('data-details_count')
        output.append((code, caption, count))
        # print(f'[utils.get_session_info]: adding {(code, caption, count)}')
    print(f'[utils.get_session_info]: Sending output len = {len(output)}')

    '''
    VERSION 1
    '''
    # codes = driver.find_elements(By.CLASS_NAME, 'code')
    # remains = driver.find_elements(By.CLASS_NAME, 'remain')
    # # driver.save_screenshot('./image3.png')  # screenshot
    # codes = codes[2:]
    # remains = remains[1:]
    # print('--util.get_session_info debug-- codes:')
    # for i in range(len(codes)):
    #     print(codes[i].text, remains[i].text)
    # output = []

    # for i in range(len(codes)):
    #     text = codes[i].text.split(' ')
    #     if len(text) == 1:
    #         continue  # there are sometimes has display:none that class name = code
    #     code = text[1].replace('!', '')  # sometime code contain '!' in VRIch
    #     caption = ' '.join(text[2:])
    #     count = int(remains[i].text.split(' ')[0])
    #     output.append((code, caption, count))
    driver.quit()
    return output


# ### FOR TEST ###
# sale_date = date(2025, 3, 1)
# output = get_session_info(sale_date)
