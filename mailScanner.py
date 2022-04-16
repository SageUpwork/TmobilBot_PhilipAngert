#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
import os
import logging

import imaplib, email
import re
from datetime import datetime
import pytz
import time
from calendar import timegm

from config import *
from tmob_bot import core


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


logger = loggerInit(logFileName="mailScanner.log")


user = 'shop@switchboxcontrol.com'
password = 'Support33!'
imap_url = 'imap.gmail.com'

# Function to get email content part i.e its body part
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)


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


def connectAndFetchMails(mailFrom):
    con = imaplib.IMAP4_SSL(imap_url, timeout=10)
    con.login(user, password)
    con.select('Inbox')
    msgs = get_emails(search('FROM', mailFrom, con), con)
    return msgs


def parsedMails(msgs):
    # printing them by the order they are displayed in your gmail
    msgDataset = []
    for msg in msgs[::-1]:
        for sent in msg:
            if type(sent) is tuple:
                content = str(sent[1], 'utf-8')
                data = str(content)
                try:
                    indexstart = data.find("ltr")
                    data2 = data[indexstart + 5: len(data)]
                    indexend = data2.find("</div>")
                    msgDataset.append(data2[0: indexend])
                except UnicodeEncodeError as e:
                    pass
    return msgDataset

if __name__ == '__main__':
    msgs = connectAndFetchMails(mailFrom)
    msgDataset = parsedMails(msgs)

    try: lastUpdatedMailTimestamp = float(open("lastUpdatedMail.timestamp","r").read())
    except:
        logger.debug("First run policy triggered.")
        lastUpdatedMailTimestamp = 0

    extractedData = []
    for x in msgDataset:
        entry = {}
        entry["MobileNum"] = re.findall("(\d+) needs to be activated",x)[0]
        mailTime = re.findall(r"\w+, \d{1,2} \w+ \d+ [\d\:]+ -0700 \(PDT\)",x)[0]
        mailTimeObj = time.strptime(mailTime.rstrip(" -0700 (PDT)"), "%a, %d %b %Y %H:%M:%S")
        entry["Date"] = datetime.fromtimestamp(time.mktime(mailTimeObj)).timestamp()
        extractedData.append(entry)

    mobileNums = []
    for y in extractedData:
        if y['Date'] > lastUpdatedMailTimestamp:
            mobileNums.append(y["MobileNum"])


    logger.debug(mobileNums)
    # core(mobileNums, tmob_username, tmob_password, imap_url, imap_password, imap_user)


    open("lastUpdatedMail.timestamp", "w").write(str(max([x['Date'] for x in extractedData])))