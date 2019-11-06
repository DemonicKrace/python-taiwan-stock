# -*- coding: utf-8 -*-
"""
Created on 2019/11/4 16:36

@author: demonickrace
"""
import os
import requests
import zipfile
import xlrd
import data_fetch.config
import data_fetch.log
import database.mysql_manager


def download_twse(date='201909'):
    zip_file = data_fetch.config.MONTH_REVENUE_SAVE_PATH + '/{}_twse.zip'.format(date)
    try:
        url = data_fetch.config.TWSE_MONTH_REVENUE_URL.format(date + '_C04003.zip')
        response = requests.get(url)

        # create zip
        with open(zip_file, "wb") as temp_zip_file:
            temp_zip_file.write(response.content)

        # extract zip and rename xls file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(data_fetch.config.MONTH_REVENUE_SAVE_PATH)
            temp_file = data_fetch.config.MONTH_REVENUE_SAVE_PATH + '/{}'.format(zip_ref.namelist()[0])
            new_file = data_fetch.config.MONTH_REVENUE_SAVE_PATH + '/{}_twse.xls'.format(date)
            if os.path.exists(temp_file):
                os.rename(temp_file, new_file)
            print('{} was download.'.format(new_file))
    except Exception as e:
        msg = 'download_twse error, msg = '.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)
    finally:
        # remove zip
        if os.path.exists(zip_file):
            os.remove(zip_file)


def download_otc(date='201909'):
    xls_file = data_fetch.config.MONTH_REVENUE_SAVE_PATH + '/{}_otc.xls'.format(date)
    try:
        url = data_fetch.config.OTC_MONTH_REVENUE_URL.format('O_' + date + '.xls')
        response = requests.get(url)
        with open(xls_file, "wb") as temp_xls_file:
            temp_xls_file.write(response.content)
            print('{} was download.'.format(xls_file))
    except Exception as e:
        msg = 'download_otc error, msg = '.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)


def get_twse_month_revenue(date='201909'):
    twes_xls_file = data_fetch.config.MONTH_REVENUE_SAVE_PATH + '/{}_twse.xls'.format(date)
    try:
        if not os.path.exists(twes_xls_file):
            download_twse(date)
        workbook = xlrd.open_workbook(twes_xls_file)
        sheet = workbook.sheet_by_index(0)
        end_row = sheet.nrows
        # start row
        i = 10
        date = date[:4] + '-' + date[4:] + '-01'
        twse_data = []
        while i < end_row:
            row = sheet.row_values(i)
            i += 1
            if 'total' in row[0].lower():
                break
            stock_no = row[0].split(' ')[0]
            if stock_no and len(stock_no) == 4:
                net_sales = row[2] * 1000
                pre_year_net_sales = row[4] * 1000
                increased_amount = net_sales - pre_year_net_sales
                increased_amount_percent = -1.0
                if pre_year_net_sales != 0:
                    increased_amount_percent = increased_amount / pre_year_net_sales
                accumulated_amount = row[3] * 1000
                pre_year_accumulated_amount = row[5] * 1000
                accumulated_increased_amount = accumulated_amount - pre_year_accumulated_amount
                accumulated_increased_amount_percent = -1.0
                if pre_year_accumulated_amount != 0:
                    accumulated_increased_amount_percent = accumulated_increased_amount / pre_year_accumulated_amount
                temp = [
                    stock_no,
                    date,
                    net_sales,
                    pre_year_net_sales,
                    increased_amount,
                    increased_amount_percent,
                    accumulated_amount,
                    pre_year_accumulated_amount,
                    accumulated_increased_amount,
                    accumulated_increased_amount_percent,
                    ''
                ]
                twse_data.append(temp)
        return twse_data
    except Exception as e:
        msg = 'get_twse_month_revenue error, msg = '.format(e.args)
        print(msg)
    return None


def get_otc_month_revenue(date='201909'):
    otc_xls_file = data_fetch.config.MONTH_REVENUE_SAVE_PATH + '/{}_otc.xls'.format(date)
    try:
        if not os.path.exists(otc_xls_file):
            download_otc(date)
        workbook = xlrd.open_workbook(otc_xls_file)
        # otc has two sheets
        sheets = [
            workbook.sheet_by_index(0),
            workbook.sheet_by_index(1)
        ]
        otc_data = []
        date = date[:4] + '-' + date[4:] + '-01'
        for sheet in sheets:
            end_row = sheet.nrows
            # start row
            i = 10
            while i < end_row:
                row = sheet.row_values(i)
                i += 1
                if 'total' in row[0].lower():
                    break
                stock_no = row[0].split(' ')[0]
                if stock_no and len(stock_no) == 4:
                    net_sales = row[3] * 1000
                    pre_year_net_sales = row[5] * 1000
                    increased_amount = net_sales - pre_year_net_sales
                    increased_amount_percent = -1.0
                    if pre_year_net_sales != 0:
                        increased_amount_percent = increased_amount / pre_year_net_sales
                    accumulated_amount = row[4] * 1000
                    pre_year_accumulated_amount = row[6] * 1000
                    accumulated_increased_amount = accumulated_amount - pre_year_accumulated_amount
                    accumulated_increased_amount_percent = -1.0
                    if pre_year_accumulated_amount != 0:
                        accumulated_increased_amount_percent = accumulated_increased_amount / pre_year_accumulated_amount
                    temp = [
                        stock_no,
                        date,
                        net_sales,
                        pre_year_net_sales,
                        increased_amount,
                        increased_amount_percent,
                        accumulated_amount,
                        pre_year_accumulated_amount,
                        accumulated_increased_amount,
                        accumulated_increased_amount_percent,
                        ''
                    ]
                    otc_data.append(temp)
        return otc_data
    except Exception as e:
        msg = 'get_otc_month_revenue error, msg = '.format(e.args)
        print(msg)
    return None


def get_all_month_revenue(date='201909'):
    return get_twse_month_revenue(date) + get_otc_month_revenue(date)


def update_month_revenue_to_db(dates=None):
    if dates is None:
        dates = []
    db_manager = database.mysql_manager.MysqlManager()
    for date in dates:
        print('start update month_revenue, date={}'.format(date))
        data = get_all_month_revenue(date)
        db_manager.insert_month_revenue_to_db(date, data)


def get_month_revenue_by_stockno_date(stock_no='2330', date='201909'):
    date = date[:4] + '-' + date[4:] + '-01'
    sql = "SELECT * FROM month_revenue WHERE stock_no = '{}' AND date = '{}';".format(stock_no, date)
    db_manager = database.mysql_manager.MysqlManager()
    result = db_manager.select_query(sql, True)
    return result[0]


if __name__ == '__main__':
    # download_twse()
    # download_otc()

    # all_twse = get_twse_month_revenue()
    # print(len(all_twse))
    # for row in all_twse:
    #     print(row)

    # all_otc = get_otc_month_revenue()
    # print(len(all_otc))
    # for row in all_otc:
    #     print(row)

    # all = get_all_month_revenue()
    # print(len(all))
    # for r in all:
    #     print(r)

    # # db insert test
    # dates = [
    #     '201901',
    #     '201909'
    # ]
    # update_month_revenue_to_db(dates)

    # import pprint
    # d = get_month_revenue_by_stockno_date()
    # pprint.pprint(d)

    pass
