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
    # driver = webdriver.Firefox(executable_path="driver/geckodriver")
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

def fetchDBDatapoint(cookies=None):
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'B2b-Client': 'SKAVA-SSP',
        'B2b-Org': '2-36WG28BS',
        'B2b-ccid': '2-36WG28BS',
        'B2b-userId': '2-3XTCPALM',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
        # Requests sorts cookies= alphabetically
        # 'Cookie': f"visid_incap_1835273=dkpmHV4bTt2pgkZbekPsc/R/T2IAAAAAQUIPAAAAAABAxfAsMJ0keOVdPejgGemj; ext_name=ojplmecpdpgccookcobabopnaifgidhf; visid_incap_385986=+ZsbBcltS9WjVlXDrscp3fp/T2IAAAAAQUIPAAAAAACZ9AMzRMjBeyNR7mhKHR4T; MP_LANG=en; mtc=%7B%22m%22%3A%22c%3A0%2Ca%3A0%2Cl%3A0%2Cv%3A0%22%2C%22t%22%3A%22c%3A0%2Ca%3A0%2Cl%3A1%2Cv%3A0%22%7D; visid_incap_850966=caxI41z8R4q90TtEaldqpHDTVmIAAAAAQUIPAAAAAABahFjpYIAjKJ3lyuH+nOKy; bizTID=U-9184761f-b599-4cae-86cf-2b5c7449048c; biz=1; incap_ses_1226_1835273=MS5fLUWeCjqI/TzNKKEDEYAuy2IAAAAAEY/tnjs8eSTewwuyczgeSg==; lpc=n; check=true; AMCVS_1358406C534BC94D0A490D4D%40AdobeOrg=1; incap_ses_886_850966=vMnYazd4Vyy58eDiA7VLDIwuy2IAAAAAzPmtlvLO4Zqz88xyGao8ag==; nlbi_385986=zaQZQ9tlVSMWYe+l5oLgEAAAAABGqlCnCPJkMDbKPL7z+z/q; incap_ses_485_385986=O5Z3L+ttkn7VOHRrthG7Bowuy2IAAAAA1HQ537CF7qyhPbuk8X0CGg==; incap_ses_2104_2669135=ynBKEyGC9FOHgGxL7+gyHZAuy2IAAAAAdrW7KGUYW8cJZ5lInZ1VkQ==; s_cc=true; HRERITRUL=P2; visid_incap_2669135=YtbzrxATQEiTciXMGjM/daAuy2IAAAAAQUIPAAAAAABege0jtfcvqjTjwrPxLMvw; incap_ses_2103_2669135=gACHJqKrEyJdY8ancFsvHaAuy2IAAAAAT9y+yqi5+DlBmqO5dVjcCw==; utag_main=v_id:0180068be9b90001359e4665ddd703068001906000bd0{_sn:7$_ss:0$_st:1657484780488$vapi_domain:t-mobile.com$_se:1$ses_id:1657482891759%3Bexp-session$_pn:4%3Bexp-session;} OptanonConsent=isGpcEnabled=0&datestamp=Mon+Jul+11+2022+01%3A26%3A21+GMT%2B0530+(India+Standard+Time)&version=6.34.0&isIABGlobal=false&hosts=&consentId=d52911a3-77ec-4bab-bda0-fa91f8a80373&interactionCount=0&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1%2Cgpc%3A1&AwaitingReconsent=false; mbox=PC#ed3f86dd58144ba1a0bf065d45a08b39.31_0#1720727783|session#bab4fafca08b4ff88e7c686e1a0974f0#1657484752; org_user_details=eyJvcmdJZCI6IjItMzZXRzI4QlMiLCJ1c2VySWQiOiIyLTNYVENQQUxNIiwicm9sZUlkIjoiMzU1ODAzIiwicm9sZU5hbWUiOiJCTyIsImZpcnN0TmFtZSI6IlBoaWxsaXAiLCJsYXN0TmFtZSI6IkFuZ2VydCIsImxvZ29uSWQiOiJTaG9wQHN3aXRjaGJveGNvbnRyb2wuY29tIiwiaW90IjpmYWxzZX0%3D; iid=151941024024238008701911086347; incap_ses_485_1835273=G36jOXPqRhtfaHRrthG7BvMuy2IAAAAA4Iw4tuCtHZbnhTDNONmb0Q==; nlbi_1835273=58MVRLLG1DPwzsXit817vQAAAAAh6vOQFwNqc+3rpmGkKXaw; ec=m!0~t!1~l!0~n!0~s!0; pv_pageName=TFB%20AHUB%20%7C%20Manage%20Accounts%20%3A%20Manage%20Lines%20-%20Lines; s_sq=tmobusprod%3D%2526c.%2526a.%2526activitymap.%2526page%253DTFB%252520AHUB%252520%25257C%252520Manage%252520Accounts%252520%25253A%252520Manage%252520Lines%252520-%252520Lines%2526link%253DApply%2526region%253Dmat-select-2-panel%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c; nlbi_850966_2417931=nNeWbC5ruUQheEO6iOSTBwAAAAA398qfSxapXwZauEmtZbF+; AMCV_1358406C534BC94D0A490D4D%40AdobeOrg=-1124106680%7CMCIDTS%7C19184%7CMCMID%7C37268760764000644865630952112670029263%7CMCAID%7CNONE%7CMCOPTOUT-1657492008s%7CNONE%7CvVersion%7C5.2.0",
        'DNT': '1',
        'Origin': 'https://tfb.t-mobile.com',
        'Pragma': 'no-cache',
        'Referer': 'https://tfb.t-mobile.com/apps/tfb_acctmgmt/account-management/lines',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
        'authType': 'iam',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }

    json_data = {
        'pageNumber': '1',
        'pageSize': 999,
        'billingAccount': '967526621',
    }

    response = requests.post(
        'https://tfb.t-mobile.com/xhr/tfb-acctmgmt/nodehap/manage-lines/billing-accounts/subscriber-line-details',
        cookies=cookies, headers=headers, json=json_data)
    aa = response.json()

def core(mobileNums, tmob_username, tmob_password, imap_url, imap_password, imap_user):
    cancelledNums = json.loads(open("CancelledLinesSkipped.txt","r").read())
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
                if atmpt < 2:
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
                cancelledNums.append(mobileNum)
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
        open("CancelledLinesSkipped.txt", "w").write(json.dumps(cancelledNums))
    except Exception as e:
        driver.quit()
        open("failedNums.txt", "w").write(json.dumps(failedNums))
        raise Exception(e)

if __name__ == '__main__':
    pass
    # imap_user = 'shop@switchboxcontrol.com'
    # imap_password = 'Support33!'
    # imap_url = 'imap.gmail.com'
    # tmob_username, tmob_password = "shop@switchboxcontrol.com", "Support33!"
    # mobileNums = ['3232004837']
    # core(mobileNums, username, password)
