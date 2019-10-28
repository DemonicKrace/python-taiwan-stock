# -*- coding: utf-8 -*-
"""
Created on 2017/3/27 13:57

@author: demonickrace
上市上櫃股票資訊 初始化/更新

    [股票代號, 公司名稱, 上櫃/市日期,    產業別]
ex: [   5209,    新鼎, 2002/02/25, 資訊服務業]

"""


def fetch_stock_info_to_csv_db():
    import csv

    data = []

    twse_file = "../data_fetch/twse_info_list.csv"

    with open(twse_file, 'w+') as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, 1):
            if i == 1:
                continue
            data.append([row[0], row[1], row[2], row[3], '1', '0'])
#            print (row[0], row[1], row[2], row[3])

    otc_file = "../data_fetch/otc_info_list.csv"

    with open(otc_file, 'w+') as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, 1):
            if i == 1:
                continue
            data.append([row[0], row[1], row[2], row[3], '0', '1'])
#            print (row[0], row[1], row[2], row[3])

    print("stock update finished...")
    from database import mysql_manager
    manager = mysql_manager.MysqlManager()
    manager.insert_stock_info(data)


if __name__ == '__main__':
    print("start...")
    # fetch_stock_info_to_csv_db()
