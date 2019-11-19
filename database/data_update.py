# -*- coding: utf-8 -*-
"""
Created on 2019/11/6 15:14

@author: demonickrace
"""
import time
import lib.tool
import data_fetch.config
import data_fetch.month_revenue
import data_fetch.stock
import database.mysql_manager

db_manager = database.mysql_manager.MysqlManager()


# 更新月營收資訊至資料庫
def update_month_revenue(dates=None):
    if dates is None:
        dates = []
    for date in dates:
        print('start update month revenue, date={}'.format(date))
        data = data_fetch.month_revenue.get_all_month_revenue(date)
        db_manager.insert_month_revenue_to_db(date, data)
        lib.tool.delay_seconds()()


# 更新股價資料到資料庫
def update_stock_price_by_a_day(dates=None):
    if dates is None:
        dates = []
    for date in dates:
        print('start update stock price, date={}'.format(date))
        data = data_fetch.stock.get_all_stock_price_by_a_day(date)
        db_manager.insert_all_stock_price_by_a_day(date, data)
        lib.tool.delay_seconds()()


# 更新上市櫃公司之資訊
def stock_info_update():
    print('start update stock info...')
    data_fetch.stock.download_twse_stock_info()
    time.sleep(1)
    data_fetch.stock.download_otc_stock_info()
    time.sleep(1)
    data = data_fetch.stock.get_stock_info_from_csv('all')
    db_manager.sql_dml_query("TRUNCATE TABLE stock_info;")
    db_manager.insert_stock_info(data)


if __name__ == '__main__':

    # # test update_month_revenue
    # dates = [
    #     '201901'
    # ]
    # update_month_revenue(dates)

    # # test update_stock_price_by_a_day
    # dates = [
    #     '2019-11-04',
    #     '2019-11-05'
    # ]
    # update_stock_price_by_a_day(dates)

    # test stock_info_update
    # stock_info_update()

    pass
