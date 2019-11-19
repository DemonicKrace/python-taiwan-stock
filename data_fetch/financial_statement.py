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


# 取得公開觀測站當天最新公布財報的公司代號
def get_newest_company_report_info():
    url = data_fetch.config.NEWEST_REPORT_INFO_URL
    header = data_fetch.config.HEADER
    match_company_set = set()
    try:
        html = requests.get(url, headers=header, timeout=data_fetch.config.TIMEOUT_SECONDS)
        soup = BeautifulSoup(html.content, "html.parser")
        buttons = soup.findAll("button")
        save_text = ""
        print('get data from {}'.format(url))
        print('data start...')
        for b in buttons:
            msg = b.find("u").text
            print(msg)
            save_text += msg.encode('utf8') + "\n"
            match_company_no = match_process(msg.encode('utf8'), ["上櫃公司", "上市公司"])
            if match_company_no:
                match_company_set.add(match_company_no)
        print('data end...')
        create_newest_company_report_info_temp(save_text, datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S'))
    except Exception as e:
        msg = 'get_newest_company_report_info error, msg = {}'.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)

    return list(match_company_set)


# 將公開觀測站當天最新公布財報的公司代號存入temp
def create_newest_company_report_info_temp(data, file_name):
    target = "{}/{}.txt".format(data_fetch.config.NEWEST_REPORT_INFO_SAVE_PATH, file_name)
    with open(target, 'w') as the_file:
        the_file.write(data)
    print("{}.txt was built...".format(target))


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


if __name__ == "__main__":
    # import pprint as pp
    # r = get_newest_company_report_info()
    # pp.pprint(r)

    pass
