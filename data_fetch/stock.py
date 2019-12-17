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
import lib.tool
from bs4 import BeautifulSoup
import database.config
import database.mysql_manager

db_manager = database.mysql_manager.MysqlManager()

otc_info_file = data_fetch.config.STOCK_INFO_SAVE_PATH + "/{}".format(data_fetch.config.OTC_INFO_FILENAME)
twse_info_file = data_fetch.config.STOCK_INFO_SAVE_PATH + "/{}".format(data_fetch.config.TWSE_INFO_FILENAME)

# www.twse.com.tw，民國81年1月4號起開始提供股票股價資料

# 當日最新之收盤資訊在三點以後公布 (2018-05-18為例)
# www.tpex.org.tw，民國83年1月起開始提供股票股價資料

"""
上市上櫃股票資訊 - 官方資料格式

    [股票代號, 公司名稱, 上櫃/市日期,    產業別]
ex: [   5209,    新鼎, 2002/02/25, 資訊服務業]
"""
stock_info_columns = [
    "stock_no",
    "company_name",
    "date",
    "business_type",
    "market_type"
]

stock_price_columns = [
    "stock_no",
    "date",
    "shares",
    "turnover",
    "open",
    "high",
    "low",
    "close",
    "bid_ask_spread",
    "deal"
]


def update_latest_all_stock_info_to_db_and_temp():
    inserted_rows = 0
    download_latest_twse_stock_info()
    lib.tool.delay_short_seconds()
    download_latest_otc_stock_info()
    lib.tool.delay_short_seconds()
    rows = get_stock_info_from_temp('all', return_dict=False)
    if rows:
        table_name = database.config.STOCK_INFO_TABLE
        sql = "TRUNCATE TABLE {};".format(table_name)
        result = db_manager.sql_dml_query(sql)
        if result:
            inserted_rows = db_manager.insert_rows(stock_info_columns, rows, table_name)
    return inserted_rows


# 下載最新twse公司資訊為csv檔
def download_latest_twse_stock_info():
    try:
        header = data_fetch.config.HEADER
        html = requests.get(data_fetch.config.TWSE_STOCK_INFO_URL, headers=header,
                            timeout=data_fetch.config.TIMEOUT_SECONDS)
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
        msg = 'download_latest_twse_stock_info error, msg = {}'.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)


# 下載最新otc公司資訊為csv檔
def download_latest_otc_stock_info():
    try:
        header = data_fetch.config.HEADER
        html = requests.get(data_fetch.config.OTC_STOCK_INFO_URL, headers=header,
                            timeout=data_fetch.config.TIMEOUT_SECONDS)
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
        print('{} was download.'.format(otc_info_file))
    except Exception as e:
        msg = 'download_latest_otc_stock_info error, msg = {}'.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)


# 由已下載的csv檔取得上市櫃公司資訊
# file_type = 'all' | 'twse | 'otc'
def get_stock_info_from_temp(file_type='all', return_dict=False):
    if 'twse' == file_type:
        info_file = twse_info_file
    elif 'otc' == file_type:
        info_file = otc_info_file
    elif 'all' == file_type:
        return get_stock_info_from_temp('twse', return_dict) + get_stock_info_from_temp('otc', return_dict)
    else:
        return None

    data = []
    try:
        stock_type = ''
        if 'twse' == file_type:
            stock_type = 'twse'
            if not os.path.exists(info_file):
                download_latest_twse_stock_info()
        elif 'otc' == file_type:
            stock_type = 'otc'
            if not os.path.exists(info_file):
                download_latest_otc_stock_info()
        # read csv
        with open(info_file) as f:
            csv_reader = csv.reader(f)
            for i, row in enumerate(csv_reader, 1):
                if i == 1:
                    continue
                if return_dict:
                    data.append({
                        "stock_no": row[0],
                        "company_name": row[1],
                        "date": row[2].replace('/', '-'),
                        "business_type": row[3],
                        "market_type": stock_type
                    })
                else:
                    data.append([
                        row[0],
                        row[1],
                        row[2].replace('/', '-'),
                        row[3],
                        stock_type
                    ])
    except Exception as e:
        msg = 'get_stock_info_from_temp error, msg = {}'.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)

    return data


def get_all_stock_info_from_db():
    table_name = database.config.STOCK_INFO_TABLE
    table_columns = stock_info_columns
    table_columns[2] = 'CAST(date AS CHAR) AS date'
    columns_str = ', '.join(table_columns)
    sql = 'SELECT {} FROM {};'.format(columns_str, table_name)
    result = db_manager.select_query(sql, return_dict=True)
    if result:
        return lib.tool.byteify(result)
    return None


def get_all_stock_info(return_type='array'):
    result = get_stock_info_from_temp(file_type='all')
    if 'array' == return_type and not result:
        result = get_all_stock_info_from_db()
    if 'dict' == return_type:
        result = {
            row[0]: {
                stock_info_columns[1]: row[1],
                stock_info_columns[2]: row[2],
                stock_info_columns[3]: row[3],
                stock_info_columns[4]: row[4]
            } for row in result
        }
    return result


# 取得該日期的全部上市櫃股價資料
def get_all_stock_price_by_a_day_from_url(date='2000-01-01'):
    return get_all_twse_stock_price_by_a_day_from_url(date) + get_all_otc_stock_price_by_a_day_from_url(date)


# 從資料庫取得該日全部股價資料
# get_all_stock_price_by_a_day_from_db
#
# :return
#
# {
# '2019-12-04-2330': {'bid_ask_spread': '-1.00',
#                      'close': 306.0,
#                      'deal': 9989,
#                      'high': 306.0,
#                      'low': 304.0,
#                      'open': 305.0,
#                      'shares': 34911686,
#                      'turnover': 10652239802}, ...
# }
def get_all_stock_price_by_a_day_from_db(date='2000-01-01', return_type='array'):
    select_columns = stock_price_columns
    select_columns[1] = 'CAST(date AS CHAR) AS date'
    columns_str = ', '.join(select_columns)
    table_name = database.config.STOCK_PRICE_TABLE
    sql = "SELECT {} FROM {} WHERE date='{}';".format(columns_str, table_name, date)
    result = db_manager.select_query(sql, return_dict=False)
    if result:
        if 'array' == return_type:
            result = [list(row) for row in result]
        elif 'dict' == return_type:
            result = {
                row[1] + "-" + row[0]: {
                    stock_price_columns[2]: row[2],
                    stock_price_columns[3]: row[3],
                    stock_price_columns[4]: row[4],
                    stock_price_columns[5]: row[5],
                    stock_price_columns[6]: row[6],
                    stock_price_columns[7]: row[7],
                    stock_price_columns[8]: row[8],
                    stock_price_columns[9]: row[9]
                } for row in result
            }
    return result


# 取得該日期的全部上市股價資料
def get_all_twse_stock_price_by_a_day_from_url(date='2000-01-01'):
    url = data_fetch.config.TWSE_STOCK_BY_A_DAY_URL.format(date.replace('-', ''))
    header = data_fetch.config.HEADER
    result = []
    try:
        response = requests.get(url, headers=header, timeout=data_fetch.config.TIMEOUT_SECONDS)
        data = response.json()
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
            new_row = [
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
            result.append(new_row)
    except Exception as e:
        print(e.args)
    return lib.tool.byteify(result)


# 取得該日期的全部上櫃股價資料
def get_all_otc_stock_price_by_a_day_from_url(date='2000-01-01'):
    year = str(int(date.split('-')[0]) - 1911)
    month = date.split('-')[1]
    day = date.split('-')[2]
    url = data_fetch.config.OTC_STOCK_BY_A_DAY_URL.format(year + '/' + month + '/' + day)
    header = data_fetch.config.HEADER
    result = []
    try:
        response = requests.get(url, headers=header, timeout=data_fetch.config.TIMEOUT_SECONDS)
        data = response.json()
        for row in data['aaData']:
            if '--' in row[4]:
                row[4] = '0'
                row[5] = '0'
                row[6] = '0'
                row[2] = '0'
                row[3] = '0'
            new_row = [
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
            result.append(new_row)
    except Exception as e:
        print(e.args)
    return lib.tool.byteify(result)


# 確認該日期的上市櫃股價資料是否存在於資料庫
def is_all_stock_price_exist_in_db_by_date(date='2000-01-01'):
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


def update_all_stock_price_a_day_to_db(date='2000-01-01'):
    inserted_rows = 0
    if is_all_stock_price_exist_in_db_by_date(date):
        print('stock price is already exist, date = {}'.format(date))
    else:
        rows = get_all_stock_price_by_a_day_from_url(date)
        inserted_rows = save_all_stock_price_a_day_to_db(rows)
        lib.tool.delay_short_seconds()
    return inserted_rows


def save_all_stock_price_a_day_to_db(data=None):
    inserted_row = 0
    if data:
        table_name = database.config.STOCK_PRICE_TABLE
        inserted_row = db_manager.insert_rows(stock_price_columns, data, table_name)
    return inserted_row


if __name__ == '__main__':
    import pprint as pp

    # # test get_all_twse_stock_price_by_a_day_from_url
    # r = get_all_twse_stock_price_by_a_day_from_url('2019-11-06')
    # pp.pprint(r)
    # print(len(r))

    # # test get_all_otc_stock_price_by_a_day_from_url
    # r = get_all_otc_stock_price_by_a_day_from_url('2019-11-06')
    # pp.pprint(r)
    # print(len(r))

    # # test get_all_stock_price_by_a_day_from_url
    # r = get_all_stock_price_by_a_day_from_url('2019-11-06')
    # pp.pprint(r)
    # print(len(r))

    # # test check_all_stock_price_exist_by_date
    # r = is_all_stock_price_exist_in_db_by_date('2019-11-06')
    # print(r)

    # # test download_latest_twse_stock_info
    # download_latest_twse_stock_info()
    #
    # # test download_latest_otc_stock_info
    # download_latest_otc_stock_info()

    # # test get_stock_info_from_temp
    # r = get_stock_info_from_temp('all', return_dict=False)
    # pp.pprint(r)
    # print(len(r))

    # # test get_all_stock_info_from_db
    # r = get_all_stock_info_from_db()
    # pp.pprint(r)

    # test get_all_stock_info
    # r = get_all_stock_info(return_type='array')
    # pp.pprint(r)
    # r = get_all_stock_info(return_type='dict')
    # pp.pprint(r)

    # # test update_latest_all_stock_info
    # r = update_latest_all_stock_info()
    # pp.pprint(r)

    # # test update_all_stock_price_a_day_to_db
    # r = update_all_stock_price_a_day_to_db('2019-11-07')
    # pp.pprint(r)

    # # test get_all_stock_price_by_a_day_from_db
    # r = get_all_stock_price_by_a_day_from_db('2019-11-04', return_type='dict')
    # pp.pprint(r)
    # print(len(r))

    pass
