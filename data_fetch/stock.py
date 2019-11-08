# -*- coding: utf-8 -*-
"""
Created on 2017/4/5 12:41

@author: demonickrace
"""
import csv
import requests
import os
import data_fetch.config
import data_fetch.log
from bs4 import BeautifulSoup
import database.mysql_manager

db_manager = database.mysql_manager.MysqlManager()

current_dir_path = os.path.dirname(os.path.realpath(__file__))
otc_info_file = current_dir_path + "/{}".format(data_fetch.config.TWSE_INFO_FILENAME)
twse_info_file = current_dir_path + "/{}".format(data_fetch.config.OTC_INFO_FILENAME)

# www.twse.com.tw，民國81年1月4號起開始提供股票股價資料

# 當日最新之收盤資訊在三點以後公布 (2018-05-18為例)
# www.tpex.org.tw，民國83年1月起開始提供股票股價資料

"""
上市上櫃股票資訊 初始化/更新 創建csv 且 存入db

    [股票代號, 公司名稱, 上櫃/市日期,    產業別]
ex: [   5209,    新鼎, 2002/02/25, 資訊服務業]
"""


def download_twse_stock_info():
    try:
        header = data_fetch.config.HEADER
        html = requests.get(data_fetch.config.TWSE_STOCK_INFO_URL, headers=header, timeout=data_fetch.config.TIMEOUT_SECONDS)
        soup = BeautifulSoup(html.text, "html.parser")
        table = soup.find("table", attrs={"class": "h4"})

        rows = []
        for row in table.find_all('tr'):
            rows.append([val.text.strip().encode("utf8") for val in row.find_all('td')])

        with open(twse_info_file, 'w+') as f:
            writer = csv.writer(f)
            writer.writerows([["有價證券代號", "名稱", "上市日", "產業別"]])
            for row in rows:
                if row[0] == "上市認購(售)權證":
                    break
                if len(row) > 5 and row[0] != "有價證券代號及名稱":
                    stock_info = unicode(row[0], "utf-8").split()
                    row_list = [
                        stock_info[0].encode("utf8"),
                        stock_info[1].encode("utf8"),
                        row[2],
                        row[4]
                    ]
                    writer.writerows([row_list])
            print('{} was download.'.format(twse_info_file))
    except Exception as e:
        msg = 'download_twse_stock_info error, msg = {}'.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)


def download_otc_stock_info():
    try:
        header = data_fetch.config.HEADER
        html = requests.get(data_fetch.config.OTC_STOCK_INFO_URL, headers=header, timeout=data_fetch.config.TIMEOUT_SECONDS)
        soup = BeautifulSoup(html.text, "html.parser")
        table = soup.find("table", attrs={"class": "h4"})

        rows = []
        for row in table.find_all('tr'):
            rows.append([val.text.strip().encode("utf8") for val in row.find_all('td')])

        with open(otc_info_file, 'w+') as f:
            writer = csv.writer(f)
            writer.writerows([["有價證券代號", "名稱", "上市日", "產業別"]])
            start = False
            for row in rows:
                if row[0] == "特別股":
                    break
                if start:
                    stock_info = unicode(row[0], "utf-8").split()
                    row_list = [
                        stock_info[0].encode("utf8"),
                        stock_info[1].encode("utf8"),
                        row[2],
                        row[4]
                    ]
                    writer.writerows([row_list])
                if row[0] == "股票":
                    start = True
    except Exception as e:
        msg = 'download_otc_stock_info error, msg = {}'.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)


def get_stock_info_from_csv(file_type='twse'):
    if 'twse' == file_type:
        info_file = twse_info_file
    elif 'otc' == file_type:
        info_file = otc_info_file
    elif 'all' == file_type:
        return get_stock_info_from_csv('twse') + get_stock_info_from_csv('otc')
    else:
        return None

    try:
        stock_type = ''
        if 'twse' == file_type:
            stock_type = 'twse'
            if not os.path.exists(info_file):
                download_twse_stock_info()
        elif 'otc' == file_type:
            stock_type = 'otc'
            if not os.path.exists(info_file):
                download_otc_stock_info()
        # read csv
        data = []
        with open(info_file) as f:
            csv_reader = csv.reader(f)
            for i, row in enumerate(csv_reader, 1):
                if i == 1:
                    continue
                data.append([row[0], row[1], row[2], row[3], stock_type])
        return data
    except Exception as e:
        msg = 'get_twse_stock_info_by_csv error, msg = {}'.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)

    return []


def stock_info_update():
    data = get_stock_info_from_csv('all')
    db_manager.sql_dml_query("TRUNCATE TABLE stock_info;")
    db_manager.insert_stock_info(data)


# 取得該日期的全部上市櫃股價資料
def get_all_stock_price_by_a_day(date='2000-01-01'):
    return get_all_twse_stock_price_by_a_day(date) + get_all_otc_stock_price_by_a_day(date)


# 取得該日期的全部上市股價資料
def get_all_twse_stock_price_by_a_day(date='2000-01-01'):
    url = data_fetch.config.TWSE_STOCK_BY_A_DAY_URL.format(date.replace('-', ''))
    header = data_fetch.config.HEADER
    result = []
    try:
        r = requests.get(url, headers=header, timeout=data_fetch.config.TIMEOUT_SECONDS)
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
def get_all_otc_stock_price_by_a_day(date='2000-01-01'):
    year = str(int(date.split('-')[0]) - 1911)
    month = date.split('-')[1]
    day = date.split('-')[2]
    url = data_fetch.config.OTC_STOCK_BY_A_DAY_URL.format(year + '/' + month + '/' + day)
    header = data_fetch.config.HEADER
    result = []
    try:
        r = requests.get(url, headers=header, timeout=data_fetch.config.TIMEOUT_SECONDS)
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


# 確認該日期的上市櫃股價資料是否存在於資料庫
def check_all_stock_price_exist_in_db_by_date(date='2000-01-01'):
    sql = "SELECT stock_no FROM stock where date = '{}';".format(date)
    result = db_manager.select_query(sql)
    if len(result) > 0:
        return True
    return False


# 藉由日期從資料庫查股價
def get_stock_price_from_db_by_a_date(stock_no='2330', date='2000-01-01'):
    sql = "SELECT * FROM month_revenue WHERE stock_no = '{}' AND date = '{}';".format(stock_no, date)
    result = db_manager.select_query(sql, True)
    if result:
        return result[0]
    return None
    pass


if __name__ == '__main__':
    # import pprint as pp

    # # test get_all_twse_stock_price_by_a_day
    # r = get_all_twse_stock_price_by_a_day('2019-11-06')
    # pp.pprint(r)
    # print(len(r))
    #
    # # test get_all_otc_stock_price_by_a_day
    # r = get_all_otc_stock_price_by_a_day('2019-11-06')
    # pp.pprint(r)
    # print(len(r))
    #
    # # test get_all_stock_price_by_a_day
    # r = get_all_stock_price_by_a_day('2019-11-06')
    # pp.pprint(r)
    # print(len(r))

    # # test check_all_stock_price_exist_by_date
    # r = check_all_stock_price_exist_in_db_by_date('2019-11-06')
    # print(r)

    # # test download_twse_stock_info
    # r = download_twse_stock_info()
    # print(len(r))

    # # test download_otc_stock_info
    # r = download_otc_stock_info()
    # pp.pprint(r)

    # # test get_stock_info_from_csv
    # r = get_stock_info_from_csv('all')
    # pp.pprint(r)
    # print(len(r))

    # # test stock_info_update
    # stock_info_update()

    pass

