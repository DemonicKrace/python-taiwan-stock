# -*- coding: utf-8 -*-
"""
Created on 2017/3/23 18:06

@author: demonickrace
"""
import datetime
import csv


# 讀取自csv
def read_warrant_info_csv(file_name):
    with open(file_name) as f:
        csv_reader = csv.reader(f)
        data = []
        for row in csv_reader:
            data.append(row[0])
            print (row[0])
        return data


# 匯入上市上櫃全部之認購認售權證資料
def fetch_all_warrant_info_to_db():
    from database import mysql_manager
    from data_fetch import warrant_fetch

    manager = mysql_manager.MysqlManager()

    # 從第幾個開始
    twse_target_no = 0
    otc_target_no = 0

    # 每50筆在匯入資料庫
    count = 50

    n = count
    twse_data = []
    # 取得全部上市權證代號
    all_twse_warrant_no = manager.select_all_warrant_no(twse=True)

    for i, no in enumerate(all_twse_warrant_no, 1):
        if i >= twse_target_no:
            data = warrant_fetch.warrant_info_fetch(no[0], twse=True)
            print(data)
            if data is None:
                print("twse warrant_no:{} loaded fail, {}/{}...".format(no[0], i, len(all_twse_warrant_no)))
            else:
                twse_data.append(data)
                print("twse warrant_no:{} was load, {}/{}...".format(no[0], i, len(all_twse_warrant_no)))
            if i >= n:
                manager.insert_warrant_info(twse_data)
                twse_data = []
                n += count
            print("\n")
    manager.insert_warrant_info(twse_data)
    print("all twse warrant info was loaded, {} rows was inserted".format(len(all_twse_warrant_no)))

    n = count
    otc_data = []
    # 取得全部上櫃權證代號
    all_otc_warrant_no = manager.select_all_warrant_no(otc=True)
    for i, no in enumerate(all_otc_warrant_no, 1):
        if i >= otc_target_no:
            data = warrant_fetch.warrant_info_fetch(no[0], otc=True)
            print(data)
            if data is None:
                print("otc warrant_no:{} loaded fail, {}/{}...".format(no[0], i, len(all_otc_warrant_no)))
            else:
                otc_data.append(data)
                print("otc warrant_no:{} was load, {}/{}...".format(no[0], i, len(all_otc_warrant_no)))
            if i >= n:
                manager.insert_warrant_info(otc_data)
                otc_data = []
                n += count
            print("\n")
    manager.insert_warrant_info(otc_data)
    print("all otc warrant info was loaded, {} rows was inserted".format(len(all_otc_warrant_no)))


if __name__ == "__main__":

    print("{} start loading...".format(datetime.datetime.now()))
#    fetch_all_warrant_info_to_db()
    print("{} loaded finish...".format(datetime.datetime.now()))
