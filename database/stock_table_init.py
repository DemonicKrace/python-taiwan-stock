# -*- coding: utf-8 -*-
"""
Created on 2017/3/13 00:33

@author: demonickrace
"""

import csv
import time
import datetime

stock_dir = "stock"
twse_dir = stock_dir + "/twse"
otc_dir = stock_dir + "/otc"


# 創建csv
def create_stock_csv(path, stock_no, data):
    file_name = "{}.csv".format(stock_no)
    with open(path + "/" + file_name, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows([row for row in data if row])
    print "{} was loaded...".format(file_name)


# year為西元
def get_months_list(date, twse=False, otc=False):

    now = datetime.datetime.now()

    start_date = datetime.datetime.strptime(date, "%Y/%m/%d")

    # 西元1911年 = 民國1年
    # twse以西元格式做post
    # otc以民國格式做get
    start_year = start_date.year
    start_month = start_date.month

    # www.twse.com.tw，民國81年1月4號起開始提供股票資料
    if twse:
        if start_date.year < 1992:
            start_year = 1992
            start_month = 1
    # www.tpex.org.tw，民國83年1月起開始提供股票資料
    elif otc:
        if start_date.year < 1994:
            start_year = 1994
            start_month = 1

    months_list = []

    for y in range(start_year, now.year + 1):

        # 若是為發行年，起始月為發行年的月份
        if y == start_year:
            start_m = start_month
        else:
            start_m = 1
        # 若為今年，結束月為這個月
        if y == now.year:
            end_m = now.month
        else:
            end_m = 12

        for m in range(start_m, end_m + 1):
            months_list.append([y, m])

    return months_list


# www.twse.com.tw，民國81年1月4號起開始提供股票資料，以天為單位
# year為西元
def get_stock(stock_no, year, month, twse=False, otc=False):
    # 重傳次數
    times = 5
    # 間隔時間
    seconds = 3

    # if failed , retry 5 times
    for i in range(0, times):
        try:
            from data_fetch import stock_fetch
            if twse:
                data = stock_fetch.twse_fetch_a_month(stock_no, year, month)
            elif otc:
                data = stock_fetch.otc_fetch_a_month(stock_no, year, month)
            else:
                return None
            return data
        except Exception as e:
            msg = "{}. {}: {}_{}_{} , error = {}\n".format(i, datetime.datetime.now(), stock_no, year, month, e.message)
            print(msg)
            time.sleep(seconds)
        if i == times - 1:
            from data_fetch.log import Log
            log = Log()
            msg = " stock fetch error: {}_{}_{} , error = {}\n".format(stock_no, year, month, e.message)
            log.write_fetch_err_log(msg)
            return None


# 取得上市或上櫃之公司代號
def get_stock_no_list(csv_file):
    with open(csv_file) as f:
        csv_reader = csv.reader(f)
        stock_no_list = [[row[0], row[2]] for row in csv_reader if len(row[0]) == 4]
        return stock_no_list


def fetch_all_stock_to_db(twse=False, otc=False):

    if twse and otc:
        print("parameter must choose only one, twse=Ture or otc=Ture!")
        return
    elif not twse and not otc:
        print("parameter must choose twse=Ture or otc=Ture!")
        return

    no_file = ""

    # 公司代號，上市日期
    if twse:
        no_file = "../data_fetch/twse_info_list.csv"
    elif otc:
        no_file = "../data_fetch/otc_info_list.csv"

    no_list = get_stock_no_list(no_file)

    if twse:
        print("台灣上市公司總數 = {}".format(len(no_list)))
    elif otc:
        print("台灣上櫃公司總數 = {}".format(len(no_list)))

    for no, company_no in enumerate(no_list, 1):
        # 根據[股號]=twse_no[0]，[發行日期]twse_no[1]=，進行匯入
        stock_no = company_no[0]
        date = company_no[1]

        print ("{} start loading...".format(stock_no))

        if twse:
            months = get_months_list(date, twse=True)
        elif otc:
            months = get_months_list(date, otc=True)

        all_rows = []
        for year, month in months:
            if twse:
                data = get_stock(stock_no, year, month, twse=True)
            elif otc:
                data = get_stock(stock_no, year, month, otc=True)
            if data is None:
                continue
            all_rows.extend(data)
        # 創建csv方式
        # create_stock_csv(twse_dir, stock_no,all_rows)
        import mysql_manager
        manager = mysql_manager.MysqlManager()
        manager.insert_stock(stock_no, all_rows)

        print ("stock_no:{} was loaded... {}/{}\n".format(stock_no, no, len(no_list)))

    if twse:
        print("twse download was finished!\n\n\n")
    elif otc:
        print("otc download was finished!\n\n\n")


if __name__ == '__main__':

    '''
    # 創建資料夾stock，給csv用
    if not os.path.exists(stock_dir):
        os.makedirs(stock_dir)

    # 創建資料夾stock/twse
    if not os.path.exists(twse_dir):
        os.makedirs(twse_dir)

    # 創建資料夾stock/otc
    if not os.path.exists(otc_dir):
        os.makedirs(otc_dir)
    '''

    start_dt = datetime.datetime.now()

    # www.twse.com.tw，民國81年1月4號起開始提供上市股票資料，以天為單位
    # www.tpex.org.tw，民國83年1月起開始提供上櫃股票資料，以天為單位

    # 爬取全部上市公司之歷史股價資料 (至本月)
    # fetch_all_stock_to_db(twse=True)

    # 爬取全部上櫃公司之歷史股價資料 (至本月)
    # fetch_all_stock_to_db(otc=True)

    end_dt = datetime.datetime.now()

    dif = end_dt - start_dt

    print("started at ", start_dt)
    print("finished at ", end_dt)
    print("all time = ", dif)
