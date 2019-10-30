# -*- coding: utf-8 -*-
"""
Created on 2017/4/5 12:41

@author: demonickrace
"""
import config
import csv
import random
import requests
import os
from bs4 import BeautifulSoup
import json
import time
from database import mysql_manager
manager = mysql_manager.MysqlManager()

dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
otc_file = dir_path + "otc_info_list.csv"
twse_file = dir_path + "twse_info_list.csv"

max_retry_seconds = config.MAX_RETRY_SECONDS
min_retry_seconds = config.MIN_RETRY_SECONDS

max_wait_seconds = config.MAX_WAIT_SECONDS
min_wait_seconds = config.MIN_WAIT_SECONDS


# www.twse.com.tw，民國81年1月4號起開始提供股票資料
# year 為西元
def twse_fetch_a_month(stock_no, year, month):

    if year < 1911:
        year += 1911

    if month < 10:
        d = str(year) + "0" + str(month) + "01"
    else:
        d = str(year) + str(month) + "01"

    url = "http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}&_=1520857382948"\
        .format(d, str(stock_no))

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept-Encoding': 'utf-8'
    }

    data_list = None
    r = None

    try:
        r = requests.get(url, headers=header, timeout=20)
    except Exception as e:
        print("HTTP GET error... ")
        print(e.args)
        time.sleep(max_retry_seconds)
        return twse_fetch_a_month(stock_no, year, month)

    try:
        json_data = json.loads(r.text)
        data_list = json_data['data']
    except Exception as e:
        print("find no data...")
        return None

    data = []
#    print(data_list)
    # 日期	成交股數	成交金額	開盤價	最高價	最低價	收盤價	漲跌價差	成交筆數
    if data_list is not None:
        for row in data_list:
            r = []
            for i, col in enumerate(row, 1):
                if i == 1:
                    date = col.split("/")
                    new_date = str((int(str(date[0])) + 1911)) + "/" + str(date[1]) + "/" + str(date[2])
                    r.append(new_date)
                else:
                    r.append(str(col).replace(",", "").replace("+", ""))
            data.append(r)
    #        print(r)
        return data
    else:
        return None


# 當日最新之收盤資訊在三點以後公布 (2018-05-18為例)
# www.tpex.org.tw，民國83年1月起開始提供股票資料
# year為西元
def otc_fetch_a_month(stock_no, year, month, data_format=True):
    # year - 1911，西元需轉換為民國
    url = "http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_print.php?l=zh-tw&d={}/{}&stkno={}&s" \
          "=0,asc,0".format(int(year) - 1911, month, str(stock_no))

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept-Encoding': 'utf-8'
    }

    all_tr = None
    try:
        html = requests.get(url, headers=header, timeout=20)

        soup = BeautifulSoup(html.content, "html.parser")
        table = soup.find("table")
        all_tr = table.find_all("tr")
    except Exception as e:
        print(e.args)

    if all_tr is not None:
        data = []
        for i, row in enumerate(all_tr, 1):
            # 是否為資料修正格式
            if data_format:
                # 若第三行不是股票資料，代表此月無資料，回傳None
                if i == 3 and len(row.find_all("td")) < 9:
                    return None
                # 第二行開始為股票資料
                if i > 2 and len(row.find_all("td")) >= 9:
                    # ＊ 為全型星號
                    temp = [col.text.strip().encode("utf8").replace("+", "").replace(",", "").replace("＊", "")
                                .replace("X", "") for col in row.find_all("td") if col.text]
                    # 檢查是否為數字
                    for t in range(1, 9):
                        if not is_float_try(temp[t]):
                            temp[t] = '0'
                    data.append(temp)
            else:
                data.append([col.text.strip().encode("utf8") for col in row.find_all("td") if col.text])

        return data
    return None


def is_float_try(str_data):
    try:
        float(str_data)
        return True
    except ValueError:
        return False


def twse_list_fetch(create_csv=True):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept-Encoding': 'utf-8'
    }

    html = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2", headers=headers, timeout=20)

    soup = BeautifulSoup(html.text, "html.parser")

    table = soup.find("table", attrs={"class": "h4"})

    rows = []

    for row in table.find_all('tr'):
        rows.append([val.text.strip().encode("utf8") for val in row.find_all('td')])

    if create_csv:
        with open(twse_file, 'w+') as f:
            writer = csv.writer(f)
            writer.writerows([["有價證券代號", "名稱", "上市日", "產業別"]])
            for row in rows:
                if row[0] == "上市認購(售)權證":
                    break
                if len(row) > 5 and row[0] != "有價證券代號及名稱":
                    list = unicode(row[0], "utf-8").split()
                    row_list = []
                    row_list.append(list[0].encode("utf8"))
                    row_list.append(list[1].encode("utf8"))
                    row_list.append(row[2])
                    row_list.append(row[4])
                    writer.writerows([row_list])

    return rows


def otc_list_fetch(create_csv=True):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept-Encoding': 'utf-8'
    }

    html = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=4", headers=headers, timeout=20)

    soup = BeautifulSoup(html.text, "html.parser")

    table = soup.find("table", attrs={"class": "h4"})

    rows = []

    for row in table.find_all('tr'):
        rows.append([val.text.strip().encode("utf8") for val in row.find_all('td')])

    if create_csv:
        with open(otc_file, 'w+') as f:
            writer = csv.writer(f)
            writer.writerows([["有價證券代號", "名稱", "上市日", "產業別"]])
            start = False
            for row in rows:
                if row[0] == "特別股":
                    break
                if start:
                    list = unicode(row[0], "utf-8").split()
                    row_list = []
                    row_list.append(list[0].encode("utf8"))
                    row_list.append(list[1].encode("utf8"))
                    row_list.append(row[2])
                    row_list.append(row[4])
                    writer.writerows([row_list])
                if row[0] == "股票":
                    start = True

    return rows


"""
上市上櫃股票資訊 初始化/更新 創建csv 且 存入db

    [股票代號, 公司名稱, 上櫃/市日期,    產業別]
ex: [   5209,    新鼎, 2002/02/25, 資訊服務業]
"""


def get_all_stock_info_from_csv():
    data = []

    with open(twse_file) as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, 1):
            if i == 1:
                continue
            data.append([row[0], row[1], row[2], row[3], '1', '0'])
    #            print (row[0], row[1], row[2], row[3])

    with open(otc_file) as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, 1):
            if i == 1:
                continue
            data.append([row[0], row[1], row[2], row[3], '0', '1'])

    return data


def get_all_twse_stock_info_from_csv():
    data = []

    with open(twse_file) as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, 1):
            if i == 1:
                continue
            data.append([row[0], row[1], row[2], row[3], '1', '0'])

    return data


def get_all_otc_stock_info_from_csv():
    data = []

    with open(otc_file) as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, 1):
            if i == 1:
                continue
            data.append([row[0], row[1], row[2], row[3], '0', '1'])

    return data


def stock_info_update():
    # twse_list_fetch
    twse_list_fetch()

    # otc_list_fetch
    otc_list_fetch()

    data = get_all_stock_info_from_csv()

    from database import mysql_manager
    manager = mysql_manager.MysqlManager()
    manager.sql_dml_query("DELETE FROM stock_info WHERE 1=1")
    manager.insert_stock_info(data)


def is_stock_exist_the_month(stock_no, year, month):
    if int(month) < 10:
        month = '0' + str(month)
    d = str(year) + "-" + str(month)
    sql = "SELECT stock_no FROM stock where stock_no = '{}' and date like '{}%';".format(stock_no, d)
    result = manager.select_query(sql)

    if len(result) > 0:
        return True

    return False


def insert_stock_data_by_months(months):

    if len(months) == 0:
        return

    all_twse_stock_info = get_all_twse_stock_info_from_csv()
    print("twse stock data start loading...")
    n = 0
    all_twse_counts = len(all_twse_stock_info)
    for row_info in all_twse_stock_info:
        n += 1
        print("twse: {}/{}...".format(n, all_twse_counts))
        print("stock_no: {}, stock_list_date: {}".format(row_info[0], row_info[2]))
        for row in months:
            if is_stock_exist_the_month(row_info[0], row[0], row[1]):
                continue
            print("stock_no: {}, year: {}, month: {} , data is loading...".format(row_info[0], row[0], row[1]))
            data = twse_fetch_a_month(row_info[0], row[0], row[1])
            time.sleep(random.randint(min_retry_seconds, max_retry_seconds))
            if data is None:
                continue
            manager.insert_stock(row_info[0], data)
            # time.sleep(min_wait_seconds, max_wait_seconds)
            print("\n")
    print("twse stock data loading finish...")

    all_otc_stock_info = get_all_otc_stock_info_from_csv()
    print("otc stock data start loading...")
    n = 0
    all_otc_counts = len(all_otc_stock_info)
    for row_info in all_otc_stock_info:
        n += 1
        print("otc: {}/{}...".format(n, all_otc_counts))
        print("stock_no: {}, stock_list_date: {}".format(row_info[0], row_info[2]))
        for row in months:
            if is_stock_exist_the_month(row_info[0], row[0], row[1]):
                continue
            print("stock_no: {}, year: {}, month: {} , data is loading...".format(row_info[0], row[0], row[1]))
            data = otc_fetch_a_month(row_info[0], row[0], row[1])
            if data is None:
                continue
            manager.insert_stock(row_info[0], data)
            # time.sleep(min_wait_seconds, max_wait_seconds)
            time.sleep(random.randint(min_retry_seconds, max_retry_seconds))
            print("\n")
    print("otc stock data loading finish...")


# 取得該日期的全部上市櫃股價資料
def get_all_stock_by_a_day(date='2000-01-01'):
    return get_all_twse_by_a_day(date) + get_all_otc_by_a_day(date)


# 取得該日期的全部上市股價資料
def get_all_twse_by_a_day(date='2000-01-01'):
    url = config.TWSE_STOCK_BY_A_DAY_URL.format(date.replace('-', ''))
    header = config.HEADER
    result = []
    try:
        r = requests.get(url, headers=header, timeout=config.TIMEOUT_SECONDS)
        data = r.json()
        if 'data9' not in data:
            return result
        for row in data['data9']:
            bid_ask_spread = ''
            if '-' in row[9]:
                bid_ask_spread = '-'
            if '--' in row[5]:
                row[5] = '0'
                row[6] = '0'
                row[7] = '0'
                row[8] = '0'
                row[10] = '0'
            r = [
                row[0],
                date,
                row[2].replace(',', ''),
                row[4].replace(',', ''),
                row[5].replace(',', ''),
                row[6].replace(',', ''),
                row[7].replace(',', ''),
                row[8].replace(',', ''),
                bid_ask_spread + row[10].replace(',', ''),
                row[3].replace(',', '')
            ]
            result.append(r)
    except Exception as e:
        print(e.args)
    return result


# 取得該日期的全部上櫃股價資料
def get_all_otc_by_a_day(date='2000-01-01'):
    year = str(int(date.split('-')[0]) - 1911)
    month = date.split('-')[1]
    day = date.split('-')[2]
    url = config.OTC_STOCK_BY_A_DAY_URL.format(year + '/' + month + '/' + day)
    header = config.HEADER
    result = []
    try:
        r = requests.get(url, headers=header, timeout=config.TIMEOUT_SECONDS)
        data = r.json()
        for row in data['aaData']:
            if '--' in row[4]:
                row[4] = '0'
                row[5] = '0'
                row[6] = '0'
                row[2] = '0'
                row[3] = '0'
            r = [
                row[0],
                date,
                row[7].replace(',', ''),
                row[8].replace(',', ''),
                row[4].replace(',', ''),
                row[5].replace(',', ''),
                row[6].replace(',', ''),
                row[2].replace(',', ''),
                row[3].replace(',', '').replace('+', ''),
                row[9].replace(',', '')
            ]
            result.append(r)
    except Exception as e:
        print(e.args)
    return result


# 插入該日期全部上市櫃股價資料到資料庫
def insert_all_stock_by_a_day(date='2000-01-01'):
    data = get_all_stock_by_a_day(date)
    manager.insert_all_stock_by_a_day(date, data)


# 確認該日期的上市櫃股價資料是否存在
def check_all_stock_exist_by_date(date='2000-01-01'):
    sql = "SELECT stock_no FROM stock where date = '{}';".format(date)
    result = manager.select_query(sql)
    if len(result) > 0:
        return True
    return False


if __name__ == '__main__':

    # get_all_twse_by_a_day('2019-10-29')
    # get_all_otc_by_a_day('2019-10-29')
    # print(get_all_stock_by_a_day('2019-10-27'))
    # insert_all_stock_by_a_day('2019-10-29')
    # print(check_all_stock_exist_by_date('2019-10-30'))
    # stock_info_update()

    # data = twse_fetch_a_month('2330', 2019, 10)
    # print(data)

    # 1235 2000 9 bid_ask_spread = "X0.00"

    # this_year = datetime.datetime.now().year
    # this_month = datetime.datetime.now().month

    # 對所有股票要爬取的月份
    # months = [[2017, 3], [2017, 4], [2017, 5], [2017, 6], [2017, 7], [2017, 8], [2017, 9], [2017, 10], [2017, 11],
    #          [2017, 12], [2018, 1], [2018, 2], [2018, 3], [2018, 4]]
    # months = [[2018, 3]]
    # insert_stock_data_by_months(months)

    pass


