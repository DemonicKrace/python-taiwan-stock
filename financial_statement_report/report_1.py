# -*- coding: utf-8 -*-
"""
Created on 2018/3/15 13:29

@author: demonickrace

# 第一版
"""

import csv
import time
import os
from os import listdir
from database import mysql_manager
manager = mysql_manager.MysqlManager()
from data_fetch import stock
from datetime import datetime
from data_fetch import log
log = log.Log()

wait_seconds = 5

report_dir = os.path.dirname(os.path.realpath(__file__)) + "/" + "report"

target_date = "2018-03-31"

pass_old_data = False


def get_price(stock_no, date):
    sql_query = "SELECT stock.close FROM stock.stock where stock_no = '{}' and date = '{}';".format(stock_no, date)
    result = manager.select_query(sql_query)
    if len(result) == 1:
        return result[0][0]
    return None


def get_last_deal_date_price(stock_no):
    sql_query = "select close from stock where stock_no = '{}' order by date desc;".format(stock_no)
    result = manager.select_query(sql_query)
    for price in result:
        if float(price[0]) > 0:
            return float(price[0])
    return None


def insert_stock_data(stock_no, date):
    info_result = manager.select_query("SELECT twse, otc FROM stock.stock_info where stock_no = '{}';"
                                       .format(stock_no), True)
    twse = int(info_result[0]['twse'])
    otc = int(info_result[0]['otc'])

    year = datetime.strptime(date, '%Y-%m-%d').year
    mon = datetime.strptime(date, '%Y-%m-%d').month

    # print(year, mon)

    data = None
    if twse == 1:
        data = stock.twse_fetch_a_month(stock_no, year, mon)
    elif otc == 1:
        data = stock.otc_fetch_a_month(stock_no, year, mon)

    if data is not None:
        month = date.split("-")[0] + "-" + date.split("-")[1]
        manager.sql_dml_query("delete from stock where stock_no = '{}' and date like '{}%';"
                              .format(stock_no, month))
        manager.insert_stock(stock_no, data)

    time.sleep(wait_seconds)

    if data is not None:
        # fetch success
        return True
    # fetch fail
    return False

#    stock_fetch.twse_fetch_a_month()
#    stock_fetch.otc_fetch_a_month()


# 創建csv
def create_csv(data, file_name):
    with open(file_name, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows([row for row in data if row])


def get_old_stockNo(file_name):
    with open(file_name) as f:
        csv_reader = csv.reader(f)
        first = True
        old_stockNo = []
        for row in csv_reader:
            if not first:
                old_stockNo.append(row[0])
            else:
                first = False
        return old_stockNo


if __name__ == "__main__":

#    r = get_price(2330, '2018-03-13')
#    print(r)

#    insert_stock_data(2330, '2018-03-13')

    # 綜合損益
    # 營業利益（損失）= NetOperatingIncomeLoss
    # eps = BasicEarningsLossPerShare
    sql_query = "SELECT stock_no, NetOperatingIncomeLoss, NetOperatingIncomeLoss_p, BasicEarningsLossPerShare " \
                "FROM stock.statement_of_comprehensive_income where year = '2017' and season = '5';"
    ci_result = manager.select_query(sql_query, True)

    #
    # target_date = "2018-03-29"

    eps_title = "2017_year_eps"
    eps_pre_year_title = "2016_year_eps"

    eps_compare_title = "2017_2016_eps_compare_eps成長率"

    NetOperatingIncomeLoss_year_title = "2017_year_NetOperatingIncomeLoss_營業淨收(千元)"
    NetOperatingIncomeLoss_p_year_title = "2017_year_NetOperatingIncomeLoss_p_營業淨收佔總營收之百分比(%)"

    NetOperatingIncomeLoss_pre_year_title = "2016_year_NetOperatingIncomeLoss_營業淨收(千元)"
    NetOperatingIncomeLoss_p_pre_year_title = "2016_year_NetOperatingIncomeLoss_p_營業淨收佔總營收之百分比(%)"

    NetOperatingIncomeLoss_compare_title = "2017_2016_NetOperatingIncomeLoss_compare_營業淨收成長率(%)"
    NetOperatingIncomeLoss_p_compare_title = "2017_2016_NetOperatingIncomeLoss_p_compare_營業淨收佔總營收之百分比之成長率(%)"

    # 欄位
    data_row = [['stock_no_股票代號', 'company_name_公司名稱', target_date + '_closed_price_收盤價', eps_title, 'price_earnings_ratio_本益比',
                eps_pre_year_title,
                eps_compare_title,
                NetOperatingIncomeLoss_year_title, NetOperatingIncomeLoss_p_year_title,
                NetOperatingIncomeLoss_pre_year_title, NetOperatingIncomeLoss_p_pre_year_title,
                NetOperatingIncomeLoss_compare_title, NetOperatingIncomeLoss_p_compare_title]]

    # 舊資料
    old_stockNo = []
    if pass_old_data:
        report_files = [f for f in listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]
        for report_file in report_files:
            if report_file.endswith('.csv'):
                f = report_dir + "/" + report_file
                old_data = get_old_stockNo(f)
                old_stockNo.extend(old_data)

    # 公司資訊
    all_stock_info = stock.get_all_stock_info_from_csv()
    all_stock_info_company_name = {}
    for row in all_stock_info:
        all_stock_info_company_name[row[0]] = row[1]

    i = 0
    all_count = len(ci_result)
    for company in ci_result:
        stock_no = company['stock_no']

        i += 1
        print("stock_no:{}, {}/{}...".format(stock_no, i, all_count))
        # print(company)

        # 略過分析過的
        if stock_no in old_stockNo:
            print("stock_no:{} ,old data pass...\n".format(stock_no))
            continue

        net_income = company['NetOperatingIncomeLoss']
        net_income_p = company['NetOperatingIncomeLoss_p']
        eps = company['BasicEarningsLossPerShare']
        if net_income is None or net_income_p is None or eps is None:
            print("some value is None, net_income = {}, net_income_p = {}, eps = {}, pass..."
                  .format(net_income, net_income_p, eps))
            continue

        if float(eps) <= 0:
            print("eps <= 0, pass...")

        market_price = get_price(stock_no, target_date)

        if market_price is None:
            print("stock_no:{} ,date:{} ,market_price is None, try to loading again... ".format(stock_no, target_date))
            fetch_state = insert_stock_data(stock_no, target_date)
            market_price = get_price(stock_no, target_date)
            print(fetch_state)
            if fetch_state and market_price is None:
                msg = "stock_no:{} ,date:{} , market_price is no deal , try to get last date closed price".format(stock_no, target_date)
                market_price = get_last_deal_date_price(stock_no)
                if market_price is None:
                    msg = "stock_no:{} ,date:{} , get last price error...\n".format(stock_no)
                    print(msg)
                    log.write_fetch_err_log(msg)
                    continue
            if fetch_state is False:
                market_price = get_last_deal_date_price(stock_no)

        if float(market_price) == 0:
            market_price = get_last_deal_date_price(stock_no)

        if eps is None:
            msg = "stock_no:{} ,year:2017 ,season:5 ,eps is None\n".format(stock_no)
            print(msg)
            log.write_fetch_err_log(msg)
            continue

        try:
#            print("eps = {}, market_price = {}".format(eps, market_price))
            if eps > 0:
                per = float(market_price) / float(eps)

            # print("eps = {}, market_price = {}, per = {}".format(eps, market_price, per))

            query = "SELECT NetOperatingIncomeLoss, NetOperatingIncomeLoss_p, " \
                    "BasicEarningsLossPerShare FROM stock.statement_of_comprehensive_income " \
                    "where year = '2016' and season = '5' and stock_no = '{}';".format(stock_no)
            result = manager.select_query(query, True)
#            print("query = " + query)

            net_income_2016 = None
            net_income_p_2016 = None
            eps_2016 = None

            for row in result:
                net_income_2016 = row['NetOperatingIncomeLoss']
                net_income_p_2016 = row['NetOperatingIncomeLoss_p']
                eps_2016 = row['BasicEarningsLossPerShare']

            if net_income_2016 is None or net_income_p_2016 is None or eps_2016 is None:
                print("some value is None, net_income_2016 = {}, net_income_p_2016 = {}, eps_2016 = {}, pass..."
                      .format(net_income_2016, net_income_p_2016, eps_2016))
                continue

            if float(eps) <= 0:
                continue

            if float(eps_2016) <= 0:
                eps_compare = "+{}up".format(float(eps) - float(eps_2016))
                eps_compare_number = float(eps) - float(eps_2016)
            else:
                eps_compare = (float(eps) - float(eps_2016)) / float(eps_2016)
                eps_compare_number = (float(eps) - float(eps_2016)) / float(eps_2016)

#            if float(net_income_2016) < 0:
            net_income_compare = (float(net_income) - float(net_income_2016)) / float(net_income_2016)
#            else:
#                net_income_compare = (float(net_income) - float(net_income_2016))

            net_income_p_compare = float(net_income_p) - float(net_income_p_2016)

#            print("compare = {}, {}, {}".format(eps_compare, net_income_compare, net_income_p_compare))

            # 篩選條件
            qualification = False
            if 0 <= per <= 10:
                qualification = True
            if 0 <= per <= (eps_compare_number * 100):
                qualification = True
            if 0 <= per <= (net_income_p_compare * 100):
                qualification = True

#            print("per = {}, eps_compare = {}, net_income_p_compare = {}"
#                  .format(per, eps_compare_number * 100, net_income_p_compare * 100))

            if qualification is False:
                print("per = {}, eps_compare_number = {}, net_income_p_compare = {}"
                      .format(per, eps_compare_number, net_income_p_compare))
                print("stock_no:{} pass...\n".format(stock_no))
                continue

            company_name = all_stock_info_company_name.get(stock_no, None)
            if company_name is None:
                company_name = "find no name"

            data = [stock_no, company_name, market_price, eps, per,
                    eps_2016,
                    eps_compare,
                    net_income, net_income_p,
                    net_income_2016, net_income_p_2016,
                    net_income_compare, net_income_p_compare
                    ]
            print(data)
            data_row.append(data)
        except Exception as e:
            print("stock_no:{} process fail...".format(stock_no))
            print(e.args)
            continue
        print("\n")

#    file_name = report_dir + "/" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ".csv"
    file_name = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ".csv"
    create_csv(data_row, file_name)


