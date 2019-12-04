# -*- coding: utf-8 -*-
"""
Created on 2019/11/6 15:14

@author: demonickrace
"""
import lib.tool
import data_fetch.config
import data_fetch.month_revenue
import data_fetch.statement_of_comprehensive_income as income_statement
import data_fetch.balance_sheet
import data_fetch.stock
import database.mysql_manager

db_manager = database.mysql_manager.MysqlManager()

except_business_type = [
    '金融保險業',
    '建材營造業'
]


# 更新上市櫃公司之資訊到資料庫
def update_stock_info():
    print('update_stock_info start...')
    all_rows = data_fetch.stock.update_latest_all_stock_info_to_db_and_temp()
    print('all updated stock info = {}'.format(all_rows))
    print('update_stock_info finish...\n')
    print('\n')


def update_function(func_ref=None, update_dates=None):
    print('{} start...\n'.format(func_ref.__name__))
    if not update_dates:
        update_dates = []
    for date in update_dates:
        print('{} start..., date = {}'.format(func_ref.__name__, date))
        all_rows = func_ref(date)
        print('all inserted row = {}'.format(all_rows))
        print('{} finish..., date = {}'.format(func_ref.__name__, date))
        print('\n')
    print('{} finish...\n'.format(func_ref.__name__))


# 更新股價資料到資料庫
def update_stock_price_by_dates(update_dates=None):
    update_function(data_fetch.stock.update_all_stock_price_a_day_to_db, update_dates)


# 更新上市櫃月營收資訊到資料庫
def update_month_revenue(update_months=None):
    update_function(data_fetch.month_revenue.update_all_month_revenue_to_db, update_months)


# 更新上市櫃綜合損益財報
def update_income_statement_by_a_season(stock_no=None, year=None, season=None):
    result = income_statement.update_income_statement_of_a_season_to_db(stock_no, year, season)
    print('update_income_statement_by_a_season, stock_no = {}, year = {}, season = {}'.format(stock_no, year, season))
    print('inserted row = {}'.format(result))


# 更新上市櫃綜合損益財報
def update_balance_sheet_by_a_season(stock_no=None, year=None, season=None):
    result = data_fetch.balance_sheet.update_balance_sheet_of_a_season_to_db(stock_no, year, season)
    print('update_balance_sheet_by_a_season, stock_no = {}, year = {}, season = {}'.format(stock_no, year, season))
    print('inserted row = {}'.format(result))


# 更新全部上市櫃財報
def update_all_fs_by_seasons(dates=None):
    print('update_all_fs_by_seasons start...\n')
    if not dates:
        dates = []
    if dates:
        all_company_info = data_fetch.stock.get_all_stock_info()
        all_company_count = len(all_company_info)
        for date in dates:
            year = date[0]
            season = date[1]
            print('update_all_fs_by_seasons start, year = {}, season = {}\n'.format(year, season))
            i = 0
            for stock_info in all_company_info:
                i += 1
                stock_no = stock_info[0]
                stock_name = stock_info[1]
                business_type = stock_info[3]
                print('now={}/{}, ({}/{})'.format(year, season, i, all_company_count))
                print('stock_no = {} ({}, {})'.format(stock_no, stock_name, business_type))
                if business_type in except_business_type:
                    print('this business type would not process...')
                    continue
                # balance not contain season 5 (year)
                if 5 != season:
                    # update balance sheet
                    update_balance_sheet_by_a_season(stock_no, year, season)
                # update income statement
                update_income_statement_by_a_season(stock_no, year, season)
                print('\n')
            print('update_all_fs_by_seasons finish, year = {}, season = {}\n'.format(year, season))
    print('update_all_fs_by_seasons finish...\n')


if __name__ == '__main__':
    import pprint as pp

    # # test update_stock_price_by_dates
    # dates = [
    #     '2019-11-04',
    #     '2019-11-05'
    # ]
    # update_stock_price_by_dates(dates)

    # # test update_stock_info
    # update_stock_info()

    # # test update_month_revenue
    # months = [
    #     '201901',
    #     '201902',
    #     '201903',
    # ]
    # update_month_revenue(months)

    # test update_all_fs_by_seasons
    seasons = [
        [2018, 1],
        [2018, 2],
        [2018, 3],
        [2018, 4],
        [2018, 5],
        [2019, 1],
        [2019, 2]
    ]
    update_all_fs_by_seasons(seasons)

    pass
