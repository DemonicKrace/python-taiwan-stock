# -*- coding: utf-8 -*-
"""
Created on 2017/3/21 12:20

@author: demonickrace
"""
import time
import datetime
import requests
from bs4 import BeautifulSoup


# http://mops.twse.com.tw/mops/web/ajax_t05st48
# 擷取上市上櫃之權證訊息，一次一個
# 公開資訊觀測站之資料無法連續爬取，每筆查詢之間隔至少需要1秒，否則會拒絕查詢20~30秒
def warrant_info_fetch(warrant_no, twse=False, otc=False):
    if twse and otc:
        print("error: 參數需要 twse=True 或 otc=True ")
        return None

    if not twse and not otc:
        print("error: 參數不可同時 twse=False 和 otc=False ")
        return None

    # http://mops.twse.com.tw/mops/web/ajax_t05st48 上市上櫃之權證資料之查詢
    url = "http://mops.twse.com.tw/mops/web/ajax_t05st48"
    if twse:
        type = "sii"
    elif otc:
        type = "otc"

    html_class = "odd"

    # 查詢資料
    formData = {
        "encodeURIComponent": "1",
        "run": "Y",
        "step": "1",
        "TYPEK": type,
        "GOOD_ID": warrant_no,
        "firstin": "true",
        "off": "1"
    }
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept-Encoding': 'utf-8'
    }

    # 重傳次數
    times = 5
    # 間隔時間
    seconds = 3

    # if failed , retry 5 times
    for i in range(0, times):
        try:
            print("warrant_no:{} is loading...".format(warrant_no))
            count = 0
            while True:
                count += 1
                html = requests.post(url, data=formData, headers=header, timeout=20)
                # 每筆查詢間隔
                time.sleep(1)
                soup = BeautifulSoup(html.content.decode("utf8"), "html.parser")
                all_td = soup.find_all("td", html_class)
                tr = soup.find("tr", html_class)
                if len(all_td) != 0 and len(tr) != 0:
                    break
                else:
                    time.sleep(seconds)
                # 最多嘗試一百次
                if count > 100:
                    from data_fetch.log import Log
                    log = Log()
                    log.write_fetch_err_log("warrant_info warrant_no:{} was no found!".format(warrant_no))
                    return None
            break
        except Exception as e:
            msg = "{}. otc warrant_no:{} , error = {}\n".format(i, warrant_no, e.message)
            print(msg)
            time.sleep(seconds)
        if i == times - 1:
            from data_fetch.log import Log
            log = Log()
            log.write_db_err_log(msg)
            return None

    warrant_data = [warrant_no]
    for i, td in enumerate(all_td, 1):
        if i > 13:
            break
        if i == 2 or i == 6:
            continue
        elif i == 1:
            if td.text.strip().encode("utf8") == "認購權證":
                warrant_data.append('buy')
            elif td.text.strip().encode("utf8") == "認售權證":
                warrant_data.append('sell')
            else:
                return None
        elif 7 <= i <= 11:
            temp = td.text.strip().encode("utf8").replace("年", "/").replace("月", "/").replace("日", "") \
                .replace("民國", "").split("/")
            date = "{}/{}/{}".format((int(temp[0]) + 1911), temp[1], temp[2])
            warrant_data.append(date)
        else:
            warrant_data.append(td.text.strip().encode("utf8").replace(" ", "").replace(",", "").replace("+", ""))

    for i, td in enumerate(tr.find_all("td"), 1):
        if i > 2:
            break
        warrant_data.append(td.text.strip().encode("utf8"))

    if twse:
        warrant_data.append('1')
        warrant_data.append('0')
    else:
        warrant_data.append('0')
        warrant_data.append('1')

        # print(warrant_data)

    #    for r in warrant_data:
    #        print r
    return warrant_data


# http://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_print.php?l=zh-tw&d=106/03/15&se=WW&s=0,asc,0
# 取得該日期之所有上櫃權證
# 自民國96年7月起開始提供
def otc_warrant_fetch(date):
    temp = date.split("/")
    y = temp[0]
    m = temp[1]
    d = temp[2]
    url = "http://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_print.php?l=zh-tw&d={}/{}/{}" \
          "&se=WW&s=0,asc,0".format(int(y) - 1911, m, d)

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept-Encoding': 'utf-8'
    }

    # 重傳次數
    times = 5
    # 間隔時間
    seconds = 3

    # if failed , retry 5 times
    for i in range(0, times):
        try:
            html = requests.get(url, headers=header, timeout=20)
            break
        except Exception as e:
            msg = "{}. otc warrant date:{} , error = {}\n".format(i, date, e.message)
            print(msg)
            time.sleep(seconds)
        if i == times - 1:
            from data_fetch.log import Log
            log = Log()
            log.write_fetch_err_log(msg)
            return None

    soup = BeautifulSoup(html.content, "html.parser")

    table = soup.find("table")

    if table is None:
        print("{} is no data!".format(date))
        return None

    data = []
    for n, tr in enumerate(table.find_all("tr"), 1):
        if n > 2:
            tds = tr.find_all("td")
            if len(tds) < 15:
                break
            row = []
            for i, td_ in enumerate(tds, 0):
                if i == 0:
                    row.append(tds[i].text.strip().encode("utf8"))
                else:
                    col = tds[i].text.strip().encode("utf8").replace("+", "").replace(",", "").replace("＊", "") \
                        .replace("X", "").replace(" ", "")
                    if not is_float_try(col):
                        row.append("0")
                    else:
                        row.append(col)

            data.append([row[0], date, row[7], row[8], row[4], row[5], row[6], row[2], row[3], row[9], '0', '1'])

        #    for r in data:
        #        print r

    return data


# http://www.twse.com.tw/ch/trading/exchange/MI_INDEX/MI_INDEX.php
# 取得該日期之所有上市權證
# 自民國93年2月11日起提供
def twse_warrant_fetch(date):
    temp = date.split("/")
    y = temp[0]
    m = temp[1]
    d = temp[2]

    tagret_date = "{}/{}/{}".format(int(y) - 1911, m, d)

    url = "http://www.twse.com.tw/ch/trading/exchange/MI_INDEX/MI_INDEX.php"

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept-Encoding': 'utf-8'
    }

    # 認購查詢資料
    buyFormData = {
        "download": "",
        "qdate": tagret_date,
        "selectType": "0999"
    }

    # 認售查詢資料
    sellFormData = {
        "download": "",
        "qdate": tagret_date,
        "selectType": "0999P"
    }

    # 重傳次數
    times = 5
    # 間隔時間
    seconds = 3

    # if failed , retry 5 times
    for i in range(0, times):
        try:
            html_buy = requests.post(url, data=buyFormData, headers=header, timeout=20)
            time.sleep(0.5)
            html_sell = requests.post(url, data=sellFormData, headers=header, timeout=20)
            break
        except Exception as e:
            msg = "{}. {}, twse warrant date:{} , error = {}\n".format(i, datetime.datetime.now(), date, e.message)
            print(msg)
            time.sleep(seconds)
        if i == times - 1:
            from data_fetch.log import Log
            log = Log()
            log.write_fetch_err_log(msg)
            return None

    soup_buy = BeautifulSoup(html_buy.content, "html.parser")
    soup_sell = BeautifulSoup(html_sell.content, "html.parser")

    table_buy = soup_buy.find("table")
    table_sell = soup_sell.find("table")

    if table_buy is None:
        print("{} table_buy is no data!".format(date))
        return None

    if table_sell is None:
        print("{} table_sell is no data!".format(date))
        return None

    data = []
    data_buy = twse_warrant_format(date, table_buy)
    data_sell = twse_warrant_format(date, table_sell)
    data.extend(data_buy)
    data.extend(data_sell)
    return data


# twse 認購認售權證之表格，資料格式化處理
def twse_warrant_format(date, table):
    data = []
    for n, tr in enumerate(table.find_all("tr"), 1):
        if n > 2:
            tds = tr.find_all("td")
            if len(tds) < 20:
                break
            row = []
            negative = False
            for i, td_ in enumerate(tds, 0):
                if i == 0:
                    continue
                if i == 1:
                    row.append(tds[i].text.strip().encode("utf8"))
                else:
                    col = tds[i].text.strip().encode("utf8").replace("+", "").replace(",", "").replace("＊", "") \
                        .replace("X", "").replace(" ", "")
                    if i == 10 and col == "－":
                        negative = True
                    if i == 11 and negative:
                        col = "-" + col
                    if not is_float_try(col):
                        row.append("0")
                    else:
                        if col == "0.00":
                            col = "0"
                        row.append(col)

            data.append([row[0], date, row[2], row[4], row[5], row[6], row[7], row[8], row[10], row[3], '1', '0'])

            #    for i, r in enumerate(data, 1):
            #        print("{}.{}".format(i, r))
    return data


def is_float_try(str_data):
    try:
        float(str_data)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    # warrant_info_fetch("047197", twse=True)
    # warrant_info_fetch("70001X", otc=True)

    # data = otc_warrant_fetch("2017/03/15")
    # data = twse_warrant_fetch("2017/03/15")

    '''
    data = []
    data.append(warrant_info_fetch("05649P", twse=True))
    from database import mysql_manager
    manager = mysql_manager.MysqlManager()
    manager.insert_warrant_info(data)
    '''
