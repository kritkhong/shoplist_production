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
        print("[utils.get_session_info initiated on LOCAL]")
        load_dotenv()
        driver = webdriver.Chrome()
    else:
        print("[utils.get_session_info initiated on RENDER]")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://mickeycafe19.vrich619.com/sale')

    input_user = driver.find_element(By.NAME, 'username')
    input_user.send_keys(os.environ['VRICH_USER'])
    input_pass = driver.find_element(By.NAME, 'password')
    input_pass.send_keys(os.environ['VRICH_PASS'])
    button = driver.find_element(
        By.XPATH, '/html/body/div/b/div/form/div[3]/div[2]/button')
    button.click()

    # toggle sales-monitor view
    is_product_list = driver.find_element(By.ID, 'product-list').is_displayed()
    if (is_product_list):
        print('[utils.get_session_info]: toggle sales monitor view...')
        monitor_toggle = driver.find_element(By.ID, 'monitor-toggle')
        monitor_toggle.click()

    sale_date_ele = driver.find_element(By.ID, 'search_date')
    date_str = sale_date_ele.get_attribute('value')
    target_date_str = target_date.strftime("%d/%m/%Y")

    # sale_date is not the most recent
    if (target_date_str != date_str):
        print('[utils.get_session_info]: changing sale date...')
        sale_date_ele.clear()
        sale_date_ele.send_keys(target_date_str)
        sale_date_ele.send_keys(Keys.ENTER)
        # this button indicate sale date has changed and Javascipt finish loading
        add_stock_btn = driver.find_element(By.ID, 'add_from_stock')
        wait = WebDriverWait(add_stock_btn, timeout=10)
        wait.until(lambda btn: btn.get_attribute('style') == "display: none;")
        # driver.save_screenshot('./image1_5.png')

    wait = WebDriverWait(driver, timeout=10)
    wait.until(lambda d: len(d.find_elements(
        By.CLASS_NAME, 'monitor-item')) > 1)
    monitor_items = driver.find_elements(By.CLASS_NAME, 'monitor-item')
    print(
        f'[utils.get_session_info]: Total monitor-items found = {len(monitor_items)}')
    # driver.save_screenshot('./image2.png')  # screenshot

    output = []
    for monitor_item in monitor_items:
        is_hide = monitor_item.get_attribute('hide')
        if not is_hide:
            code = monitor_item.get_attribute('data-code')
            caption = monitor_item.get_attribute('data-description')
            count = monitor_item.get_attribute('data-details_count')
            output.append((code, caption, count))
    print(f'[utils.get_session_info]: Monitor-items used = {len(output)}')
    '''
    OLD VERSION
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
# for tuple in output:
#     print(tuple)
