# -*- coding: utf-8 -*-
"""
Created on 2019/11/4 16:36

@author: demonickrace
"""
import os
import requests
import zipfile
import xlrd
import lib.tool
import data_fetch.config
import data_fetch.log
import database.config
import database.mysql_manager

db_manager = database.mysql_manager.MysqlManager()

table_columns = [
    "stock_no",
    "date",
    "net_sales",
    "pre_year_net_sales",
    "increased_amount",
    "increased_amount_percent",
    "accumulated_amount",
    "pre_year_accumulated_amount",
    "accumulated_increased_amount",
    "accumulated_increased_amount_percent",
    "note"
]


def is_month_revenue_exist_in_db(date='201909'):
    date = date[:4] + '-' + date[4:] + '-01'
    table = database.config.MONTH_REVENUE_TABLE
    sql = "select * from {} where date='{}'".format(table, date)
    result = db_manager.select_query(sql)
    if result:
        return True
    return False


def update_all_month_revenue_to_db(date='201909'):
    global table_columns
    inserted_rows = 0
    if is_month_revenue_exist_in_db(date):
        print('month revenue is already exist, month = {}'.format(date))
    else:
        rows = get_all_month_revenue_from_temp(date, return_dict=False)
        if rows:
            table_name = database.config.MONTH_REVENUE_TABLE
            inserted_rows = db_manager.insert_rows(table_columns, rows, table_name)
    return inserted_rows


def download_twse_month_revenue(date='201909'):
    zip_file = data_fetch.config.FS_MONTH_REVENUE_PATH + '/{}_twse.zip'.format(date)
    try:
        url = data_fetch.config.TWSE_MONTH_REVENUE_URL.format(date + '_C04003.zip')
        response = requests.get(url)

        # create zip
        with open(zip_file, "wb") as temp_zip_file:
            temp_zip_file.write(response.content)

        # extract zip and rename xls file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(data_fetch.config.FS_MONTH_REVENUE_PATH)
            temp_file = data_fetch.config.FS_MONTH_REVENUE_PATH + '/{}'.format(zip_ref.namelist()[0])
            new_file = data_fetch.config.FS_MONTH_REVENUE_PATH + '/{}_twse.xls'.format(date)
            if os.path.exists(temp_file):
                os.rename(temp_file, new_file)
            print('{} was download.'.format(new_file))
    except Exception as e:
        msg = 'download_twse_month_revenue error, date = {}, msg = {}'.format(date, e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)
    finally:
        # remove zip
        if os.path.exists(zip_file):
            os.remove(zip_file)


def download_otc_month_revenue(date='201909'):
    xls_file = data_fetch.config.FS_MONTH_REVENUE_PATH + '/{}_otc.xls'.format(date)
    try:
        url = data_fetch.config.OTC_MONTH_REVENUE_URL.format('O_' + date + '.xls')
        response = requests.get(url)
        file_type = response.headers['Content-Type']
        if 'text/html' == file_type:
            raise Exception('File is not xls type')
        with open(xls_file, "wb") as temp_xls_file:
            temp_xls_file.write(response.content)
            print('{} was download.'.format(xls_file))
    except Exception as e:
        msg = 'download_otc_month_revenue error, date = {}, msg = {}'.format(date, e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)


def get_twse_month_revenue_from_temp(date='201909'):
    twes_xls_file = data_fetch.config.FS_MONTH_REVENUE_PATH + '/{}_twse.xls'.format(date)
    try:
        if not os.path.exists(twes_xls_file) and data_fetch.config.AUTO_SAVE_TO_TEMP:
            download_twse_month_revenue(date)
            lib.tool.delay_short_seconds()
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
        return lib.tool.byteify(twse_data)
    except Exception as e:
        msg = 'get_twse_month_revenue_from_temp error, msg = {}'.format(e.args)
        print(msg)
    return None


def get_otc_month_revenue_from_temp(date='201909'):
    otc_xls_file = data_fetch.config.FS_MONTH_REVENUE_PATH + '/{}_otc.xls'.format(date)
    try:
        if not os.path.exists(otc_xls_file) and data_fetch.config.AUTO_SAVE_TO_TEMP:
            download_otc_month_revenue(date)
            lib.tool.delay_short_seconds()
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
        return lib.tool.byteify(otc_data)
    except Exception as e:
        msg = 'get_otc_month_revenue_from_temp error, msg = {}'.format(e.args)
        print(msg)
    return None


def get_all_month_revenue_from_db(date='201909', return_dict=False):
    global table_columns
    select_columns = table_columns
    select_columns[1] = 'CAST(date AS CHAR) AS date'
    columns_str = ', '.join(select_columns)
    date = date[:4] + '-' + date[4:] + '-01'
    table_name = database.config.MONTH_REVENUE_TABLE
    sql = "SELECT {} FROM {} WHERE date='{}';".format(columns_str, table_name, date)
    result = db_manager.select_query(sql, return_dict)
    if result:
        if return_dict:
            return lib.tool.byteify(result)
        else:
            return [list(row) for row in result]
    return None


def get_all_month_revenue_from_temp(date='201909', return_dict=False):
    global table_columns
    twse_data = get_twse_month_revenue_from_temp(date)
    otc_data = get_otc_month_revenue_from_temp(date)

    all_data = []
    if twse_data and otc_data:
        all_data = twse_data + otc_data

    if not return_dict:
        return all_data

    return_data = []
    for row in all_data:
        dict_data = {}
        for index, key in enumerate(table_columns, 0):
            dict_data[key] = row[index]
        return_data.append(dict_data)
    return return_data


def get_all_month_revenue(date='201909', return_dict=False):
    result = get_all_month_revenue_from_db(date, return_dict)
    if not result:
        result = get_all_month_revenue_from_temp(date, return_dict)
        if data_fetch.config.AUTO_SAVE_TO_DB and result:
            update_all_month_revenue_to_db(date)
    return result


# from db
def get_month_revenue_by_stockno_date(stock_no='2330', date='201909', return_dict=False):
    global table_columns
    select_columns = table_columns
    select_columns[1] = 'CAST(date AS CHAR) AS date'
    columns_str = ', '.join(select_columns)
    date = date[:4] + '-' + date[4:] + '-01'
    table_name = database.config.MONTH_REVENUE_TABLE
    sql = "SELECT {} FROM {} WHERE stock_no = '{}' AND date = '{}';".format(columns_str, table_name, stock_no, date)
    result = db_manager.select_query(sql, return_dict)
    if result:
        if return_dict:
            return lib.tool.byteify(result[0])
        else:
            return list(result[0])
    return None


if __name__ == '__main__':
    import pprint as pp

    # # test download_twse_month_revenue
    # download_twse_month_revenue('201912')

    # # test get_twse_month_revenue_from_temp
    # r_twse = get_twse_month_revenue_from_temp('201912')
    # pp.pprint(r_twse)

    # # test download_otc_month_revenue
    # download_otc_month_revenue('201912')

    # # test get_otc_month_revenue_from_temp
    # r_otc = get_otc_month_revenue_from_temp('201912')
    # pp.pprint(r_otc)

    # # test get_all_month_revenue_from_temp
    # r = get_all_month_revenue_from_temp('201912', True)
    # pp.pprint(r)
    # print(len(r))

    # # get_month_revenue_by_stockno_date
    # r = get_month_revenue_by_stockno_date('2330', '201909', True)
    # pp.pprint(r)

    # # test get_all_month_revenue_from_db
    # r = get_all_month_revenue_from_db('201909')
    # pp.pprint(r)
    # print(len(r))

    # # test is_month_revenue_exist_in_db
    # r = is_month_revenue_exist_in_db('201901')
    # pp.pprint(r)

    # # test update_all_month_revenue_to_db
    # inserted_count = update_all_month_revenue_to_db('201901')
    # print(inserted_count)

    # # test get_all_month_revenue
    # r = get_all_month_revenue('201908', return_dict=False)
    # pp.pprint(r)

    pass
