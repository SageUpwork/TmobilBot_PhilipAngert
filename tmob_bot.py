#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
import imaplib
import json
import os
import logging
import platform
import re
import time
import requests as requests
from selenium.webdriver import ActionChains
from selenium import webdriver
# from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


# Function to search for a key value pair
def search(key, value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    return data


# Function to get the list of emails under this label
def get_emails(result_bytes, con):
    msgs = []  # all the email data are pushed inside an array
    for num in result_bytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')
        msgs.append(data)

    return msgs



def loggerInit(logFileName):
    try:
        os.makedirs("logs")
    except:
        pass
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    file_handler = logging.FileHandler(f'logs/{logFileName}')
    # file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    # stream_handler.setLevel(logging.ERROR)
    logger.addHandler(stream_handler)
    return logger


logger = loggerInit(logFileName="tmob_bot.log")



def seleniumLiteTrigger_Chromium():
    driver = webdriver.Chrome(executable_path="/Users/phillipangert/Downloads/TmobilBot_PhilipAngert/driver/chromedriver")
    return driver


def seleniumLiteTrigger():
    options = Options()
    # options.headless = True

    if "Windows" in str(platform.system()):
        # WINDOWS
        geckoPath = r"driver\geckodriver.exe"
        moz_profPath = r"C:\Users\SaGe\AppData\Roaming\Mozilla\Firefox\Profiles\jbz9m3sj.default"
        # driver = webdriver.Firefox(options=options, executable_path=geckoPath)

    elif "Linux" in str(platform.system()):
        # Linux
        geckoPath = r"driver/geckodriver_linux"
        moz_profPath = r"/home/sage/.mozilla/firefox/249x8q9b.default-release"

    else:
        # Mac
        geckoPath = r"driver/geckodriver"
        moz_profPath = r"/Users/SaGe/Library/Application Support/Firefox/Profiles/24po1ob3.default-release"

    logger.debug("Mozilla profile path : " + moz_profPath)
    logger.debug("Mozilla gecko path : " + geckoPath)
    # driver = webdriver.Firefox(options=options, executable_path=geckoPath)
    # geckoPath = r"/Users/phillipangert/Downloads/TmobilBot_PhilipAngert/driver/geckodriver"

    driver = webdriver.Firefox(executable_path="/Users/phillipangert/Downloads/TmobilBot_PhilipAngert/driver/geckodriver")
    return driver


def fetchOTP_Mail(imap_url, imap_password, imap_user):
    # this is done to make SSL connection with GMAIL
    con = imaplib.IMAP4_SSL(imap_url)

    # logging the user in
    con.login(imap_user, imap_password)

    # calling function to check for email under this label
    con.select('Inbox')

    # fetching emails from this user "tu**h*****1@gmail.com"
    msgs = get_emails(search('FROM', 'customercare@notifications.t-mobile.com', con),con)
    OTP = re.findall(r"Mobile ID verification code is (\d+|(<strong>?)\d+)",str(msgs[-1][0][1]))
    return OTP

#
# def fetchHeaderAuthToken():
#     headers = {
#         'Connection': 'keep-alive',
#         'Pragma': 'no-cache',
#         'Cache-Control': 'no-cache',
#         'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
#         'DNT': '1',
#         'Accept-Language': 'en-US',
#         'sec-ch-ua-mobile': '?0',
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36',
#         'B2B-Client': 'SKAVA-SSP',
#         'Accept': 'application/json, text/plain, */*',
#         'sec-ch-ua-platform': '"Linux"',
#         'Origin': 'https://tfb.t-mobile.com',
#         'Sec-Fetch-Site': 'same-origin',
#         'Sec-Fetch-Mode': 'cors',
#         'Sec-Fetch-Dest': 'empty',
#         # 'Referer': 'https://tfb.t-mobile.com/implicit/callback?code=01.ne3G4c8unHCUOQ55Q&session_num=39841225b3f53ef2&userId=U-9184761f-b599-4cae-86cf-2b5c7449048c',
#     }
#
#     json_data = {
#         'code': '01.ne3G4c8unHCUOQ55Q',
#         'redirect_uri': 'https://tfb.t-mobile.com/implicit/callback',
#     }
#
#     response = requests.post('https://tfb.t-mobile.com/api/auth/userToken', headers=headers, cookies=cookies, json=json_data)
#     headerAppend = response.json()

def login(tmob_username, tmob_password, driver, imap_url, imap_password, imap_user):
    driver.get("https://tfb.t-mobile.com")
    time.sleep(1.2*5)
    for x in tmob_username:
        ActionChains(driver).send_keys(x).perform()
        time.sleep(0.2)
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    time.sleep(1.2*5)
    for x in tmob_password:
        ActionChains(driver).send_keys(x).perform()
        time.sleep(0.2)
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    for x in range(60):
        if driver.current_url != "https://tfb.t-mobile.com/apps/tfb_billing/dashboard":
            time.sleep(2)
            logger.debug(f"Waiting login. {(x+1)*2}/120 seconds")
        else:
            logger.debug("Login Success.")
            break
    if driver.current_url != "https://tfb.t-mobile.com/apps/tfb_billing/dashboard":
        OTP = fetchOTP_Mail(imap_url, imap_password, imap_user)[0][0].split(">")[-1]
        for x in OTP:
            ActionChains(driver).send_keys(x).perform()
            time.sleep(0.2)
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        time.sleep(1.2*20)
    for x in range(60):
        if driver.current_url != "https://tfb.t-mobile.com/apps/tfb_billing/dashboard":
            time.sleep(1.2*10)
            logger.debug(f"Waiting login. {(x+1)*2}/120 seconds")
        else:
            logger.debug("Login Success.")
            break
    cookies = {x['name']: x['value'] for x in driver.get_cookies()}
    return cookies


def core(mobileNums, tmob_username, tmob_password, imap_url, imap_password, imap_user):
    failedNums = []
    driver = seleniumLiteTrigger()
    try:
        cookies = login(tmob_username, tmob_password, driver, imap_url, imap_password, imap_user)
        if "tfb_billing/dashboard" not in driver.current_url:
            raise Exception("Login Failed")
        time.sleep(2)
        for mobileNum in mobileNums:
            time.sleep(3)
            driver.get("https://tfb.t-mobile.com/apps/tfb_urm/userapproval")
            time.sleep(3)
            driver.get("https://tfb.t-mobile.com/apps/tfb_acctmgmt/account-management/lines")
            found = False
            atmpt = 0
            while found == False:
                if atmpt < 5:
                    try:
                        WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.ID, "tmobilelisting-search")))
                        break
                    except:
                        atmpt += 1
                        driver.refresh()
                else:
                    driver.quit()
                    logger.debug("Platform error, attempting login")
                    failedNums.append(mobileNum)
                    raise Exception("PlatformBonkers")


            time.sleep(2)
            driver.find_element(by=By.ID, value="tmobilelisting-search").send_keys(mobileNum + Keys.ENTER)
            for _ in range(10):
                if "Acct #967526621" not in driver.page_source:
                    time.sleep(1.2*2)

            selectedEntry = [x for x in driver.find_elements(by=By.CLASS_NAME, value="ng-star-inserted") if
                             ((x.text.startswith(mobileNum)) & (x.text.endswith('\n•••')))][0]
            if len(selectedEntry.find_elements(by=By.CLASS_NAME, value="suspended-text")) == 0:
                logger.debug(f"{mobileNum} already active. Skipping")
                continue
            if len(selectedEntry.find_elements(by=By.CLASS_NAME, value="canceled-text")) > 0:
                logger.debug(f"{mobileNum} is cancelled. Skipping")
                continue
            selectedEntry.find_elements(by=By.CLASS_NAME, value="action-ball-margin")[0].click()
            # selectedEntry.find_elements_by_class_name("action-ball-margin")[0].click()
            try:
                driver.find_element(by=By.ID, value="lineMeatBall0").find_elements(by=By.TAG_NAME, value="li")[3].click()
                time.sleep(10)
                driver.find_element(by=By.ID,value="managePopUp").find_elements_by_class_name("mat-checkbox-inner-container")[
                    0].find_elements_by_tag_name("input")[0].send_keys(" ")
                time.sleep(10)
                driver.find_element(by=By.ID,value="managePopUp").find_elements(by=By.TAG_NAME, value="button")[-1].click()
                time.sleep(10)
                WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.ID, "tmobilelisting-search")))
                if "Restore-line request complete" in driver.page_source:
                    logger.debug("Request generated for " + mobileNum + " with transaction number: " + driver.find_element(by=By.ID, value="old-number").text)
                else:
                    logger.debug("Request failed for" + mobileNum + ". Need manual intervention")
                    failedNums.append(mobileNum)
            except:
                logger.debug("Request failed for" + mobileNum + ". Need manual intervention")
                failedNums.append(mobileNum)
            time.sleep(1.2*5)
        driver.quit()
        open("failedNums.txt", "w").write(json.dumps(failedNums))
    except Exception as e:
        driver.quit()
        open("failedNums.txt", "w").write(json.dumps(failedNums))
        raise Exception(e)

if __name__ == '__main__':
    pass
    # imap_user = 'shop@switchboxcontrol.com'
    # imap_password = 'Support33!'
    # imap_url = 'imap.gmail.com'
    # username, password = "shop@switchboxcontrol.com", "Support33!"
    # mobileNums = ['3238615908']
    # core(mobileNums, username, password)
