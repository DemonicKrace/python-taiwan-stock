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
        print('start update month_revenue, date={}'.format(date))
        data = data_fetch.month_revenue.get_all_month_revenue(date)
        db_manager.insert_month_revenue_to_db(date, data)
        time.sleep(random.randint(data_fetch.config.MIN_WAIT_SECONDS, data_fetch.config.MAX_WAIT_SECONDS))


# 更新股價資料到資料庫
def update_stock_price_by_a_day(date='2000-01-01'):
    data = data_fetch.stock.get_all_stock_price_by_a_day(date)
    db_manager.insert_all_stock_price_by_a_day(date, data)


if __name__ == '__main__':

    # update_month_revenue test
    # dates = [
    #     '201901'
    # ]
    # update_month_revenue(dates)

    pass
