# -*- coding: utf-8 -*-
"""
Created on 2019/11/6 15:14

@author: demonickrace
"""
import random
import time
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
        wait_seconds()


# 更新股價資料到資料庫
def update_stock_price_by_a_day(dates=None):
    if dates is None:
        dates = []
    for date in dates:
        print('start update stock price, date={}'.format(date))
        data = data_fetch.stock.get_all_stock_price_by_a_day(date)
        db_manager.insert_all_stock_price_by_a_day(date, data)
        wait_seconds()


def stock_info_update():
    data = data_fetch.stock.get_stock_info_from_csv('all')
    db_manager.sql_dml_query("TRUNCATE TABLE stock_info;")
    db_manager.insert_stock_info(data)


def wait_seconds():
    seconds = random.randint(data_fetch.config.MIN_WAIT_SECONDS, data_fetch.config.MAX_WAIT_SECONDS)
    print('wait {} seconds...\n'.format(seconds))
    time.sleep(seconds)


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

    # # test stock_info_update
    # stock_info_update()

    pass
