# -*- coding: utf-8 -*-
"""
Created on 2017/9/18 09:59

@author: demonickrace
"""
import requests
import datetime
import data_fetch.config
import data_fetch.log
from bs4 import BeautifulSoup

company_type = [
    "上櫃公司",
    "上市公司"
]


# 取得公開觀測站當天最新公布財報的公司代號
def get_newest_company_report_info():
    global company_type
    print('get_newest_company_report_info start...')
    url = data_fetch.config.NEWEST_REPORT_INFO_URL
    header = data_fetch.config.HEADER
    match_company_set = set()
    try:
        html = requests.get(url, headers=header, timeout=data_fetch.config.TIMEOUT_SECONDS)
        soup = BeautifulSoup(html.content, "html.parser")
        buttons = soup.findAll("button")
        save_text = ""
        print('get data from {}'.format(url))
        for b in buttons:
            msg = b.find("u").text
            print(msg)
            save_text += msg.encode('utf8') + "\n"
            match_company_no = match_process(msg.encode('utf8'), company_type)
            if match_company_no:
                match_company_set.add(match_company_no)
        create_newest_company_report_info_temp(save_text, datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S') + '.txt')
    except Exception as e:
        msg = 'get_newest_company_report_info error, msg = {}'.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)
    print('get_newest_company_report_info end...')
    return list(match_company_set)


# 將公開觀測站當天最新公布財報的公司代號存入temp
def create_newest_company_report_info_temp(data, filename):
    target = data_fetch.config.NEWEST_REPORT_INFO_SAVE_PATH + '/' + filename
    with open(target, 'w') as the_file:
        the_file.write(data)
    print("{} was built...".format(target))


# 字串處理，過濾字串
def match_process(msg_str, match_list):
    left_count = 0
    right_count = 0

    left_start_1 = 0
    right_end_1 = 0

    left_start_2 = 0
    right_end_2 = 0

    for i, c in enumerate(msg_str, 0):
        if c == '(' and left_count == 0:
            left_start_1 = i + 1
            left_count += 1
        elif c == ")" and right_count == 0:
            right_end_1 = i
            right_count += 1
        elif c == "(" and left_count > 0:
            left_start_2 = i + 1
        elif c == ")" and right_count > 0:
            right_end_2 = i
            break
    title = msg_str[left_start_1: right_end_1]
    company_no = msg_str[left_start_2: right_end_2]
    match_word = "IFRSs"
    if match_word in msg_str:
        for tmp in match_list:
            if title == tmp:
                return company_no
    return None


# 從暫存檔取得公司代號資訊
def get_stockno_from_temp(filename):
    global company_type
    print('get_stockno_from_temp start...')
    filename = data_fetch.config.NEWEST_REPORT_INFO_SAVE_PATH + '/' + filename
    print('temp = {}'.format(filename))
    with open(filename) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    match_company_set = set()
    for row in content:
        print(row)
        match_company_no = match_process(row, company_type)
        if match_company_no:
            match_company_set.add(match_company_no)
    data = list(match_company_set)
    print('get_stockno_from_temp end...')
    return data


if __name__ == "__main__":
    import pprint as pp

    # r = get_newest_company_report_info()
    # pp.pprint(r)

    # temp = '2019-12-04_16-21-07.txt'
    # r = get_stockno_from_temp(temp)
    # pp.pprint(r)

    pass
