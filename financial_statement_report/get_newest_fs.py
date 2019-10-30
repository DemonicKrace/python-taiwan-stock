# coding=utf-8
import requests
import time
import csv
from bs4 import BeautifulSoup
from datetime import datetime

# 目標日期
target_date = datetime.today().strftime('%Y-%m-%d')

# 對應資料夾名稱
temp_dir = "temp"
report_dir = "report"


# it will create_temp
def get_now_company_report_info():
    url = "http://mops.twse.com.tw/mops/web/t51sb10?Stp=R1"

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept-Encoding': 'utf-8'
    }

    match_company_set = set()
    try:
        html = requests.get(url, headers=header, timeout=20)
        soup = BeautifulSoup(html.content, "html.parser")
        buttons = soup.findAll("button")
        save_text = ""
        for b in buttons:
            msg = b.find("u").text
            print(msg)
            save_text += msg.encode('utf8') + "\n"
            match_company_no = match_process(msg.encode('utf8'))
            if match_company_no:
                match_company_set.add(match_company_no)
        #        print(match_company_set)
        create_temp(save_text, target_date)

    except Exception as e:
        print("get_report_info error... ")
        print(e.args)

    return list(match_company_set)


def match_process(msg_str):
    match_str = ["上櫃公司", "上市公司"]
    left_count = 0
    right_count = 0

    left_start_1 = 0
    right_end_1 = 0

    left_start_2 = 0
    right_end_2 = 0

    for i, c in enumerate(msg_str, 0):
        if c is '(' and left_count == 0:
            left_start_1 = i + 1
            left_count += 1
        elif c is ")" and right_count == 0:
            right_end_1 = i
            right_count += 1
        elif c is "(" and left_count > 0:
            left_start_2 = i + 1
        elif c is ")" and right_count > 0:
            right_end_2 = i
            break

    title = msg_str[left_start_1: right_end_1]
    company_no = msg_str[left_start_2: right_end_2]
    #    print(left_start_1, right_end_1)
    #    print(left_start_2, right_end_2)
    #    print("{}, {}\n".format(title, company_no))

    match_word = "IFRSs"
    if match_word in msg_str:
        for tmp in match_str:
            if title == tmp:
                return company_no

    return None


# 創建temp
def create_temp(data, file_name):
    target = "{}/{}.txt".format(temp_dir, file_name)
    with open(target, 'w') as the_file:
        the_file.write(data)
    print("{}.txt was built...".format(file_name))


if __name__ == '__main__':
    all_company_no = get_now_company_report_info()
    print(all_company_no)
