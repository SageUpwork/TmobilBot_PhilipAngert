#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
import imaplib
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
    driver = webdriver.Firefox(executable_path="driver/geckodriver")
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
    ActionChains(driver).send_keys(tmob_username + Keys.ENTER).perform()
    time.sleep(1.2*5)
    ActionChains(driver).send_keys(tmob_password + Keys.ENTER).perform()
    time.sleep(1.2*10)
    OTP = fetchOTP_Mail(imap_url, imap_password, imap_user)[0][0].split(">")[-1]
    ActionChains(driver).send_keys(OTP + Keys.ENTER).perform()
    time.sleep(1.2*20)
    for x in range(10):
        if driver.current_url != "https://tfb.t-mobile.com/apps/tfb_billing/dashboard":
            time.sleep(1.2*10)
            logger.debug("Waiting login")
        else:
            logger.debug("Login Success.")
            break
    cookies = {x['name']: x['value'] for x in driver.get_cookies()}
    # headers = fetchHeaderAuthToken()

    return cookies

#
# def runSearchRequests(param):
#
#     headers = {
#         'Connection': 'keep-alive',
#         'Pragma': 'no-cache',
#         'Cache-Control': 'no-cache',
#         'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
#         'DNT': '1',
#         'B2b-Client': 'SKAVA-SSP',
#         'sec-ch-ua-platform': '"Linux"',
#         'authType': 'iam',
#         'B2b-userId': '2-3XTCPALM',
#         'sec-ch-ua-mobile': '?0',
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36',
#         'authToken': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlVGSlBSRVJCVkMweU1ESXkifQ.eyJpYXQiOjE2NDk4ODc5NjksImV4cCI6MTY0OTg5MTU2OCwiaXNzIjoiaHR0cHM6Ly9icmFzcy5hY2NvdW50LnQtbW9iaWxlLmNvbSIsImF1ZCI6IlRGQkJpbGxpbmciLCJBVCI6ImV5SnJhV1FpT2lJeU5UQTJOR05qTVRFMU5qUTBaamt4WWpJeFpqVTNNR0UzTWpObFpqRTROeUlzSW5SNWNDSTZJbUYwSzJwM2RDSXNJbUZzWnlJNklsSlRNalUySW4wLmV5SnpkV0lpT2lKVkxUa3hPRFEzTmpGbUxXSTFPVGt0TkdOaFpTMDRObU5tTFRKaU5XTTNORFE1TURRNFl5SXNJbUYxWkNJNklsUkdRa0pwYkd4cGJtY2lMQ0p6WTI5d1pTSTZJbFJOVDE5SlJGOXdjbTltYVd4bElHVnRZV2xzSUdWNGRHVnVaR1ZrWDJ4cGJtVnpJRzl3Wlc1cFpDQnliMnhsSWl3aWFYTnpJam9pYUhSMGNITTZMeTlwWVcwdWJYTm5MblF0Ylc5aWFXeGxMbU52YlNJc0ltVjRjQ0k2TVRZME9UZzVNVFUyT0N3aWFXRjBJam94TmpRNU9EZzNPVFk0TENKcWRHa2lPaUl3TVM1VlUxSXVUMWwxUlRSUE5WcDJNVXRHVWpWMlNsSWlMQ0pqYkdsbGJuUmZhV1FpT2lKVVJrSkNhV3hzYVc1bklpd2lZM051ZEY5cFpDSTZJams1TWpRek1qVmtabUpqTlRSalltRTVaalZtT1dFelkyUXhaV0ptTW1WaUlpd2lZWHBuSWpvaVkyOWtaVG8zWm1Rd00yWXhPVGxpTWpZM1pqUTVZVEUzTnprNU1EQmhNREU0WW1RNU1UazJZV001TTJaaklpd2ljMmxrSWpvaU1GQkhOalpFUldGS1oxWnhiVmhXYjFkelRrcEVkbTFUV1VaM01YUkhTUzEzYjJwVmIyOVpTR0kxWTBkdExXWnNkWEpKTFhWNk5tWk1ZMGhXTjNaUE5pNWxlVXB5WVZkUmFVOXBTbnBrVjBwbVlWZFNNR0l5ZEd4aWJVWnNZek5DZVdJeVVXbE1RMG95U1dwdmFXUnFUV2xtVVQwOUluMC5BT05NeUYxY3ZVc18wa3FSa0FBZVdxblI0YkhFTlJLbzk0NXR5eHNOaDVObE43TnNoeTUtOXRPZk1wUWpDcDBZMlRGUE9lbExPRDhuUFg5c0k5R3A1enQ1ckxHT0xGOEpuNnpoV0I0TzVJVHplRlY5WE95Ykl4Rmhkb3JRVUZsQnpkTFhSVndOQzFrOUdDRGh1YXJmUDR1ck1MQjVIdWJNX1BZUHRSUFliNXZxOTluMHdxRUtzRjhkbnBGMkhUZjNNTkNiMjJDcDhUSDBQLW0xM0N1cXlSYzB6YmYyYnJHTVlpbGQ3cEgya29vUVJMS3VCYXVwckZwbkt4YzdRTW1vVzFDckVSTmpMSmlrME8yenZaX2lPanhPVVl4bHQzU2dDVFZjWHRXYmRtTjFqeHpQbE1IRWFSRGV4TjFnMXlrMVY5MS12US1yazRtb0JaZHVCMVlIU3ciLCJzdWIiOiJVLTkxODQ3NjFmLWI1OTktNGNhZS04NmNmLTJiNWM3NDQ5MDQ4YyIsImFjciI6ImxvYTNzYSIsImFtciI6WyJwYXNzd29yZCIsImVtYWlsX3RlbXBfcGluIl0sInVzbiI6IjczY2Q4ODBiZmVjOTNkYTEifQ.mKojg7U7hMavd3sV5Am6hhURWb_pQR8GRUzCHFnwAFu37jccvQZ9bU-lntX54UjxIk0OHogSiXJ0i8WFOjjCxY8-c7ygLBur2GvrAbDxt8WKVBSDbs6PMUjYYBIKVVzXql4PJPh4_pT6xNAV223NUq6gVfY6Q1jluFkJxJU04xVNzoW6EPWb8g1b0MC76eAnOpi_fLRtR79q7Vb7yQ5-85xz7guiFCB9nYRO35Cp3OYdw4qKnP31KYNkzdwv0V5nLFWkPB7iJWHJOzfQXoUiyLHyHK4zAGMPKECeMssZt1Bz_fzz4NedoVZ15wNKyX1QcVV-9g2ySt9vQD2_XJi7lw',
#         'Accept': 'application/json',
#         'B2b-Org': '2-36WG28BS',
#         'B2b-ccid': '2-36WG28BS',
#         # 'transactionID': '1649888033535',
#         'Origin': 'https://tfb.t-mobile.com',
#         'Sec-Fetch-Site': 'same-origin',
#         'Sec-Fetch-Mode': 'cors',
#         'Sec-Fetch-Dest': 'empty',
#         'Referer': 'https://tfb.t-mobile.com/apps/tfb_acctmgmt/account-management/lines',
#         'Accept-Language': 'en-US,en;q=0.9',
#     }
#
#     json_data = {
#         'pageNumber': '1',
#         'pageSize': 999,
#         'billingAccount': '967526621',
#     }
#
#     response = requests.post(
#         'https://tfb.t-mobile.com/xhr/tfb-acctmgmt/nodehap/manage-lines/billing-accounts/subscriber-line-details',
#         headers=headers, cookies=cookies, json=json_data)
#
#     dataout = response.json()
#     return dataout
#
#
# def suspendEntry(mobileNum):
#     headers = {
#         'Connection': 'keep-alive',
#         'Pragma': 'no-cache',
#         'Cache-Control': 'no-cache',
#         'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
#         'DNT': '1',
#         # Already added when you pass json=
#         # 'Content-Type': 'application/json',
#         'B2b-Client': 'SKAVA-SSP',
#         'sec-ch-ua-platform': '"Linux"',
#         'authType': 'iam',
#         'B2b-userId': '2-3XTCPALM',
#         'sec-ch-ua-mobile': '?0',
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36',
#         'authToken': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlVGSlBSRVJCVkMweU1ESXkifQ.eyJpYXQiOjE2NDk4ODc5NjksImV4cCI6MTY0OTg5MTU2OCwiaXNzIjoiaHR0cHM6Ly9icmFzcy5hY2NvdW50LnQtbW9iaWxlLmNvbSIsImF1ZCI6IlRGQkJpbGxpbmciLCJBVCI6ImV5SnJhV1FpT2lJeU5UQTJOR05qTVRFMU5qUTBaamt4WWpJeFpqVTNNR0UzTWpObFpqRTROeUlzSW5SNWNDSTZJbUYwSzJwM2RDSXNJbUZzWnlJNklsSlRNalUySW4wLmV5SnpkV0lpT2lKVkxUa3hPRFEzTmpGbUxXSTFPVGt0TkdOaFpTMDRObU5tTFRKaU5XTTNORFE1TURRNFl5SXNJbUYxWkNJNklsUkdRa0pwYkd4cGJtY2lMQ0p6WTI5d1pTSTZJbFJOVDE5SlJGOXdjbTltYVd4bElHVnRZV2xzSUdWNGRHVnVaR1ZrWDJ4cGJtVnpJRzl3Wlc1cFpDQnliMnhsSWl3aWFYTnpJam9pYUhSMGNITTZMeTlwWVcwdWJYTm5MblF0Ylc5aWFXeGxMbU52YlNJc0ltVjRjQ0k2TVRZME9UZzVNVFUyT0N3aWFXRjBJam94TmpRNU9EZzNPVFk0TENKcWRHa2lPaUl3TVM1VlUxSXVUMWwxUlRSUE5WcDJNVXRHVWpWMlNsSWlMQ0pqYkdsbGJuUmZhV1FpT2lKVVJrSkNhV3hzYVc1bklpd2lZM051ZEY5cFpDSTZJams1TWpRek1qVmtabUpqTlRSalltRTVaalZtT1dFelkyUXhaV0ptTW1WaUlpd2lZWHBuSWpvaVkyOWtaVG8zWm1Rd00yWXhPVGxpTWpZM1pqUTVZVEUzTnprNU1EQmhNREU0WW1RNU1UazJZV001TTJaaklpd2ljMmxrSWpvaU1GQkhOalpFUldGS1oxWnhiVmhXYjFkelRrcEVkbTFUV1VaM01YUkhTUzEzYjJwVmIyOVpTR0kxWTBkdExXWnNkWEpKTFhWNk5tWk1ZMGhXTjNaUE5pNWxlVXB5WVZkUmFVOXBTbnBrVjBwbVlWZFNNR0l5ZEd4aWJVWnNZek5DZVdJeVVXbE1RMG95U1dwdmFXUnFUV2xtVVQwOUluMC5BT05NeUYxY3ZVc18wa3FSa0FBZVdxblI0YkhFTlJLbzk0NXR5eHNOaDVObE43TnNoeTUtOXRPZk1wUWpDcDBZMlRGUE9lbExPRDhuUFg5c0k5R3A1enQ1ckxHT0xGOEpuNnpoV0I0TzVJVHplRlY5WE95Ykl4Rmhkb3JRVUZsQnpkTFhSVndOQzFrOUdDRGh1YXJmUDR1ck1MQjVIdWJNX1BZUHRSUFliNXZxOTluMHdxRUtzRjhkbnBGMkhUZjNNTkNiMjJDcDhUSDBQLW0xM0N1cXlSYzB6YmYyYnJHTVlpbGQ3cEgya29vUVJMS3VCYXVwckZwbkt4YzdRTW1vVzFDckVSTmpMSmlrME8yenZaX2lPanhPVVl4bHQzU2dDVFZjWHRXYmRtTjFqeHpQbE1IRWFSRGV4TjFnMXlrMVY5MS12US1yazRtb0JaZHVCMVlIU3ciLCJzdWIiOiJVLTkxODQ3NjFmLWI1OTktNGNhZS04NmNmLTJiNWM3NDQ5MDQ4YyIsImFjciI6ImxvYTNzYSIsImFtciI6WyJwYXNzd29yZCIsImVtYWlsX3RlbXBfcGluIl0sInVzbiI6IjczY2Q4ODBiZmVjOTNkYTEifQ.mKojg7U7hMavd3sV5Am6hhURWb_pQR8GRUzCHFnwAFu37jccvQZ9bU-lntX54UjxIk0OHogSiXJ0i8WFOjjCxY8-c7ygLBur2GvrAbDxt8WKVBSDbs6PMUjYYBIKVVzXql4PJPh4_pT6xNAV223NUq6gVfY6Q1jluFkJxJU04xVNzoW6EPWb8g1b0MC76eAnOpi_fLRtR79q7Vb7yQ5-85xz7guiFCB9nYRO35Cp3OYdw4qKnP31KYNkzdwv0V5nLFWkPB7iJWHJOzfQXoUiyLHyHK4zAGMPKECeMssZt1Bz_fzz4NedoVZ15wNKyX1QcVV-9g2ySt9vQD2_XJi7lw',
#         'Accept': 'application/json',
#         'B2b-Org': '2-36WG28BS',
#         'B2b-ccid': '2-36WG28BS',
#         'transactionID': '1649888033535',
#         'Origin': 'https://tfb.t-mobile.com',
#         'Sec-Fetch-Site': 'same-origin',
#         'Sec-Fetch-Mode': 'cors',
#         'Sec-Fetch-Dest': 'empty',
#         'Referer': 'https://tfb.t-mobile.com/apps/tfb_acctmgmt/account-management/lines',
#         'Accept-Language': 'en-US,en;q=0.9',
#     }
#
#     json_data = {
#         'ban': '967526621',
#         'reasonCode': 'ELST',
#         'suspendStartDate': '2022-04-14',
#         'restoreDate': '2022-04-15',
#         'extendContract': None,
#         'validatorType': 'SALES_DIRECTOR',
#         'logonId': 'Shop@switchboxcontrol.com',
#         'email': 'Shop@switchboxcontrol.com',
#         'dealerCode': '5007856',
#         # 'mobileNumber': '3239706103',
#         'mobileNumber': mobileNum,
#     }
#
#     response = requests.post('https://tfb.t-mobile.com/xhr/tfb-acctmgmt/nodehap/manage-lines/service-suspension',
#                              headers=headers, cookies=cookies, json=json_data)
#     susStatus = response.json()
#
# def resumeEntry(mobileNum):
#     headers = {
#         'Connection': 'keep-alive',
#         'Pragma': 'no-cache',
#         'Cache-Control': 'no-cache',
#         'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
#         'DNT': '1',
#         'B2b-Client': 'SKAVA-SSP',
#         'sec-ch-ua-platform': '"Linux"',
#         'authType': 'iam',
#         'B2b-userId': '2-3XTCPALM',
#         'sec-ch-ua-mobile': '?0',
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36',
#         'authToken': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlVGSlBSRVJCVkMweU1ESXkifQ.eyJpYXQiOjE2NDk4ODc5NjksImV4cCI6MTY0OTg5MTU2OCwiaXNzIjoiaHR0cHM6Ly9icmFzcy5hY2NvdW50LnQtbW9iaWxlLmNvbSIsImF1ZCI6IlRGQkJpbGxpbmciLCJBVCI6ImV5SnJhV1FpT2lJeU5UQTJOR05qTVRFMU5qUTBaamt4WWpJeFpqVTNNR0UzTWpObFpqRTROeUlzSW5SNWNDSTZJbUYwSzJwM2RDSXNJbUZzWnlJNklsSlRNalUySW4wLmV5SnpkV0lpT2lKVkxUa3hPRFEzTmpGbUxXSTFPVGt0TkdOaFpTMDRObU5tTFRKaU5XTTNORFE1TURRNFl5SXNJbUYxWkNJNklsUkdRa0pwYkd4cGJtY2lMQ0p6WTI5d1pTSTZJbFJOVDE5SlJGOXdjbTltYVd4bElHVnRZV2xzSUdWNGRHVnVaR1ZrWDJ4cGJtVnpJRzl3Wlc1cFpDQnliMnhsSWl3aWFYTnpJam9pYUhSMGNITTZMeTlwWVcwdWJYTm5MblF0Ylc5aWFXeGxMbU52YlNJc0ltVjRjQ0k2TVRZME9UZzVNVFUyT0N3aWFXRjBJam94TmpRNU9EZzNPVFk0TENKcWRHa2lPaUl3TVM1VlUxSXVUMWwxUlRSUE5WcDJNVXRHVWpWMlNsSWlMQ0pqYkdsbGJuUmZhV1FpT2lKVVJrSkNhV3hzYVc1bklpd2lZM051ZEY5cFpDSTZJams1TWpRek1qVmtabUpqTlRSalltRTVaalZtT1dFelkyUXhaV0ptTW1WaUlpd2lZWHBuSWpvaVkyOWtaVG8zWm1Rd00yWXhPVGxpTWpZM1pqUTVZVEUzTnprNU1EQmhNREU0WW1RNU1UazJZV001TTJaaklpd2ljMmxrSWpvaU1GQkhOalpFUldGS1oxWnhiVmhXYjFkelRrcEVkbTFUV1VaM01YUkhTUzEzYjJwVmIyOVpTR0kxWTBkdExXWnNkWEpKTFhWNk5tWk1ZMGhXTjNaUE5pNWxlVXB5WVZkUmFVOXBTbnBrVjBwbVlWZFNNR0l5ZEd4aWJVWnNZek5DZVdJeVVXbE1RMG95U1dwdmFXUnFUV2xtVVQwOUluMC5BT05NeUYxY3ZVc18wa3FSa0FBZVdxblI0YkhFTlJLbzk0NXR5eHNOaDVObE43TnNoeTUtOXRPZk1wUWpDcDBZMlRGUE9lbExPRDhuUFg5c0k5R3A1enQ1ckxHT0xGOEpuNnpoV0I0TzVJVHplRlY5WE95Ykl4Rmhkb3JRVUZsQnpkTFhSVndOQzFrOUdDRGh1YXJmUDR1ck1MQjVIdWJNX1BZUHRSUFliNXZxOTluMHdxRUtzRjhkbnBGMkhUZjNNTkNiMjJDcDhUSDBQLW0xM0N1cXlSYzB6YmYyYnJHTVlpbGQ3cEgya29vUVJMS3VCYXVwckZwbkt4YzdRTW1vVzFDckVSTmpMSmlrME8yenZaX2lPanhPVVl4bHQzU2dDVFZjWHRXYmRtTjFqeHpQbE1IRWFSRGV4TjFnMXlrMVY5MS12US1yazRtb0JaZHVCMVlIU3ciLCJzdWIiOiJVLTkxODQ3NjFmLWI1OTktNGNhZS04NmNmLTJiNWM3NDQ5MDQ4YyIsImFjciI6ImxvYTNzYSIsImFtciI6WyJwYXNzd29yZCIsImVtYWlsX3RlbXBfcGluIl0sInVzbiI6IjczY2Q4ODBiZmVjOTNkYTEifQ.mKojg7U7hMavd3sV5Am6hhURWb_pQR8GRUzCHFnwAFu37jccvQZ9bU-lntX54UjxIk0OHogSiXJ0i8WFOjjCxY8-c7ygLBur2GvrAbDxt8WKVBSDbs6PMUjYYBIKVVzXql4PJPh4_pT6xNAV223NUq6gVfY6Q1jluFkJxJU04xVNzoW6EPWb8g1b0MC76eAnOpi_fLRtR79q7Vb7yQ5-85xz7guiFCB9nYRO35Cp3OYdw4qKnP31KYNkzdwv0V5nLFWkPB7iJWHJOzfQXoUiyLHyHK4zAGMPKECeMssZt1Bz_fzz4NedoVZ15wNKyX1QcVV-9g2ySt9vQD2_XJi7lw',
#         'Accept': 'application/json',
#         'B2b-Org': '2-36WG28BS',
#         'B2b-ccid': '2-36WG28BS',
#         'transactionID': '1649888033535',
#         'Origin': 'https://tfb.t-mobile.com',
#         'Sec-Fetch-Site': 'same-origin',
#         'Sec-Fetch-Mode': 'cors',
#         'Sec-Fetch-Dest': 'empty',
#         'Referer': 'https://tfb.t-mobile.com/apps/tfb_acctmgmt/account-management/lines',
#         'Accept-Language': 'en-US,en;q=0.9',
#     }
#
#     json_data = {
#         'mobileNumber': mobileNum,
#         'ban': '967526621',
#         'reasonCode': 'SSQ',
#         'restoreDate': '2022-04-13',
#         'logonId': 'Shop@switchboxcontrol.com',
#         'email': 'Shop@switchboxcontrol.com',
#         'dealerCode': '0000002',
#         'orgId': '2-36WG28BS',
#     }
#
#     response = requests.post('https://tfb.t-mobile.com/xhr/tfb-acctmgmt/nodehap/manage-lines/service-restoration',
#                              headers=headers, cookies=cookies, json=json_data)
#     resumeStatus = response.json()
#


def core(mobileNums, tmob_username, tmob_password, imap_url, imap_password, imap_user):
    driver = seleniumLiteTrigger()
    cookies = login(tmob_username, tmob_password, driver, imap_url, imap_password, imap_user)
    if "tfb_billing/dashboard" not in driver.current_url:
        raise Exception("Login Failed")
    for mobileNum in mobileNums:
        driver.get("https://tfb.t-mobile.com/apps/tfb_acctmgmt/account-management/lines")
        time.sleep(1.2*5)
        driver.find_element(by=By.ID, value="tmobilelisting-search").send_keys(mobileNum + Keys.ENTER)
        for _ in range(10):
            if "Acct #967526621" not in driver.page_source:
                time.sleep(1.2*2)

        selectedEntry = [x for x in driver.find_elements(by=By.CLASS_NAME, value="ng-star-inserted") if
                         ((x.text.startswith(mobileNum)) & (x.text.endswith('\n•••')))][0]
        selectedEntry.find_elements(by=By.CLASS_NAME, value="action-ball-margin")[0].click()
        # selectedEntry.find_elements_by_class_name("action-ball-margin")[0].click()
        driver.find_element(by=By.ID, value="lineMeatBall0").find_elements(by=By.TAG_NAME, value="li")[3].click()
        time.sleep(1.2*5)
        driver.find_element_by_id("managePopUp").find_elements_by_class_name("mat-checkbox-inner-container")[
            0].find_elements_by_tag_name("input")[0].send_keys(" ")
        time.sleep(1.2*3)
        driver.find_element_by_id("managePopUp").find_elements(by=By.TAG_NAME, value="button")[-1].click()
        time.sleep(1.2*10)
        if "Restore-line request complete" in driver.page_source:
            logger.debug("Request generated for " + mobileNum + " with transaction number: " + driver.find_element(by=By.ID, value="old-number").text)
        else:
            logger.debug("Request failed for" + mobileNum + ". Need manual intervention")
        time.sleep(1.2*5)
    driver.quit()

if __name__ == '__main__':
    pass
    # imap_user = 'shop@switchboxcontrol.com'
    # imap_password = 'Support33!'
    # imap_url = 'imap.gmail.com'
    # username, password = "shop@switchboxcontrol.com", "Support33!"
    # mobileNums = ['3238615908']
    # core(mobileNums, username, password)
