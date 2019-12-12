# -*- coding: utf-8 -*-
"""
Created on 2019/11/12 16:25

@author: demonickrace
"""
import json
import requests
import data_fetch.config
import data_fetch.log
import lib.tool
import database.config
from bs4 import BeautifulSoup
import database.mysql_manager

db_manager = database.mysql_manager.MysqlManager()

# 綜合損益 statement_of_comprehensive_income
# 爬取的欄位
dict_format = {
    ##
    "營業收入合計": "operating_revenue",
    "收入合計": "operating_revenue",
    ##
    "營業成本合計": "operating_costs",
    "支出合計": "operating_costs",
    "營業毛利(毛損)": "gross_profit_loss_from_operations",
    "未實現銷貨(損)益": "unrealized_profit_loss_from_sales",
    "已實現銷貨(損)益": "realized_profit_loss_on_from_sales",
    "營業毛利(毛損)淨額": "gross_profit_loss_from_operations_net",
    # 營業費用
    "推銷費用": "selling_expenses",
    "管理費用": "administrative_expense",
    "研究發展費用": "research_and_development_expenses",
    "營業費用合計": "operating_expenses",
    # 其他收益及費損淨額
    "其他收益及費損淨額": "net_other_income_expenses",
    "營業利益(損失)": "net_operating_income_loss",
    # 營業外收入及支出
    "其他收入": "other_income_others",
    "其他利益及損失淨額": "other_gains_losses",
    "財務成本淨額": "finance_costs",
    "採用權益法認列之關聯企業及合資損益之份額淨額": "other_income_c4",
    "營業外收入及支出合計": "nonoperating_income_and_expenses",
    "稅前淨利(淨損)": "profit_loss_before_tax",
    "所得稅費用(利益)合計": "income_tax_expense_continuing_operations",
    "繼續營業單位本期淨利(淨損)": "profit_loss_from_continuing_operations",
    "本期淨利(淨損)": "profit_loss",
    # 後續可能重分類至損益之項目
    "其他綜合損益(淨額)": "other_comprehensive_income",
    "本期綜合損益總額": "comprehensive_income",
    "母公司業主(淨利∕損)": "profit_loss_attributable_to_owners_of_parent",
    "非控制權益(淨利∕損)": "profit_loss_attributable_to_noncontrolling_interests",
    "母公司業主(綜合損益)": "comprehensive_income_attributable_to_owners_of_parent",
    "非控制權益(綜合損益)": "comprehensive_income_attributable_to_noncontrolling_interests",
    # 基本每股盈餘
    "基本每股盈餘": "basic_earnings_loss_per_share",
    # 稀釋每股盈餘
    "稀釋每股盈餘": "diluted_earnings_loss_per_share"
}

except_percent_columns = [
    "basic_earnings_loss_per_share",
    "diluted_earnings_loss_per_share"
]


def is_income_statement_exist_in_db(stock_no='2330', year=2019, season=1):
    table = database.config.INCOME_STATEMENT_TABLE
    sql = "select * from {} where stock_no='{}' and year='{}' and season='{}'".format(table, stock_no, year, season)
    result = db_manager.select_query(sql)
    if result:
        return True
    return False


def update_income_statement_of_a_season_to_db(stock_no='2330', year=2019, season=1):
    inserted_rows = 0
    if is_income_statement_exist_in_db(stock_no, year, season):
        print('income statement is already exist, stock_no = {}, year= {}, season = {}'.format(stock_no, year, season))
    else:
        return_data = get_income_statement_of_a_season_from_url(stock_no, year, season)
        if return_data:
            inserted_rows = save_income_statement_of_a_season_to_db(return_data)
        lib.tool.delay_short_seconds()
    return inserted_rows


def save_income_statement_of_a_season_to_db(data=None):
    inserted_rows = 0
    stock_no = data.get('stock_no', None)
    year = data.get('year', None)
    season = data.get('season', None)

    if data and stock_no and year and season:
        table_columns = []
        values = []
        for key, value in data.items():
            if '' != value:
                table_columns.append(key)
                values.append(value)
        if not is_income_statement_exist_in_db(stock_no, year, season) and values:
            print('stock_no = {}, year = {}, season = {}, try to inserting...'.format(stock_no, year, season))
            rows = [values]
            table_name = database.config.INCOME_STATEMENT_TABLE
            inserted_rows = db_manager.insert_rows(table_columns, rows, table_name)
    return inserted_rows


def save_income_statement_of_a_season_to_temp(data=None):
    try:
        if not data:
            raise Exception('save_income_statement_of_a_season_to_temp fail, input data is None!')

        date = '{}-{}'.format(data['year'], data['season'])
        key = '{}-{}'.format(data['stock_no'], date)
        target_file = data_fetch.config.FS_STATEMENT_OF_COMPREHENSIVE_INCOME_PATH + '/{}.json'.format(date)

        lib.tool.init_json_file_if_not_exist(target_file)
        json_obj = lib.tool.get_json_obj_from_temp_file(target_file)

        # check data exist
        with open(target_file, 'w') as temp_file:
            json_obj[key] = data
            save_data = json.dumps(json_obj, indent=4, sort_keys=True)
            temp_file.write(save_data)
        return True
    except Exception as e:
        msg = 'save_income_statement_of_a_season_to_temp error, msg = {}'.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)
        return False


def get_income_statement_of_a_season_from_temp(stock_no='2330', year=2019, season=1):
    try:
        date = '{}-{}'.format(year, season)
        key = '{}-{}'.format(stock_no, date)
        target_file = data_fetch.config.FS_STATEMENT_OF_COMPREHENSIVE_INCOME_PATH + '/{}.json'.format(date)

        lib.tool.init_json_file_if_not_exist(target_file)
        json_obj = lib.tool.get_json_obj_from_temp_file(target_file)
        result = json_obj.get(key, None)
        return result
    except Exception as e:
        msg = 'get_income_statement_of_a_season_from_temp error, file = {}.json, msg = {}'.format(key, e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)
        return None


def get_income_statement_from_url(stock_no='2330', year=2019, season=1):
    stockno_year_season = "{}-{}-{}".format(stock_no, year, season)
    try:
        query_year = year
        if 1911 < query_year:
            query_year -= 1911
                            
        header = data_fetch.config.HEADER
        url = data_fetch.config.MOPS_STATEMENT_OF_COMPREHENSIVE_INCOME_URL
        # 查詢資料
        form_data = {
            'encodeURIComponent': '1',
            'step': '1',
            'firstin': '1',
            'off': '1',
            'keyword4': '',
            'code1': '',
            'TYPEK2': '',
            'checkbtn': '',
            'queryName': 'stock_no',
            'inpuType': 'stock_no',
            'TYPEK': 'all',
            'isnew': 'false',
            'co_id': stock_no,
            'year': query_year,
            'season': season
        }
        """
        # 一般產業股
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'keyword4': '',
        'code1': '',
        'TYPEK2': '',
        'checkbtn': '',
        'queryName': 'stock_no',
        'inpuType': 'stock_no',
        'TYPEK': 'all',
        'isnew': 'false',
        'co_id': 2330,
        'year': 105,
        'season': 02

        # 金融保險業
        encodeURIComponent:1
        id:
        key:
        TYPEK:sii
        step:2
        year:106
        season:2
        co_id:2884
        firstin:1
        """
        html = requests.post(url, data=form_data, headers=header, timeout=data_fetch.config.TIMEOUT_SECONDS)
        soup = BeautifulSoup(html.content.decode("utf8"), "html.parser")

        if soup.find("h3"):
            msg = "website is busy!"
            print(msg)
            raise Exception(msg)

        h4 = soup.find("h4").find("font").text
        if u"查無所需資料！" == h4:
            msg = "website find no data for the season!"
            print(msg)
            raise Exception(msg)

        table = soup.find("table", "hasBorder")
        all_row = table.find_all("tr")
    except Exception as e:
        msg = 'get_income_statement_from_url error, stockno_year_season = {}, msg = {}'.format(stockno_year_season, e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)
        return None

    data = []
    for i, tr in enumerate(all_row, 1):
        if i > 4:
            row = []
            for j, td in enumerate(tr.find_all("td"), 1):
                if j > 3:
                    break
                col = td.text.strip().encode("utf8").replace(",", "")
                row.append(lib.tool.full_to_half(col))
            data.append(row)

    dict_data = {}
    for row in data:
        row[0] = row[0].encode('utf8', 'ignore')
        row[1] = row[1].encode('utf8', 'ignore')
        row[2] = row[2].encode('utf8', 'ignore')
        if row[0] in dict_format and '' != row[1]:
            key = dict_format.get(row[0], None)
            key_p = key + "_p"
            if '' != row[1] and key:
                if key in except_percent_columns:
                    dict_data[key] = float(row[1])
                else:
                    dict_data[key] = int(row[1]) * 1000
            if '' != row[2] and key_p:
                dict_data[key_p] = float(row[2]) / 100.0
    
    # 公開觀測站只有第一二三季報表,第四季為年度報表
    if 4 == season:
        season = 5
    info = {'stock_no': stock_no, 'year': year, 'season': season}
    if dict_data:
        dict_data.update(info)
        dict_data = lib.tool.fill_default_value_if_column_not_exist(dict_format, dict_data, except_percent_columns)
    return dict_data


def get_income_statement_of_a_season4(stock_no='2330', year=2018):
    s1_data = get_income_statement_of_a_season_from_temp(stock_no, year, 1)
    s2_data = get_income_statement_of_a_season_from_temp(stock_no, year, 2)
    s3_data = get_income_statement_of_a_season_from_temp(stock_no, year, 3)
    s4_data = None
    year_data = get_income_statement_of_a_season_from_temp(stock_no, year, 5)

    if not s1_data:
        s1_data = get_income_statement_from_url(stock_no, year, 1)
        if s1_data:
            if data_fetch.config.AUTO_SAVE_TO_DB:
                save_income_statement_of_a_season_to_db(s1_data)
            if data_fetch.config.AUTO_SAVE_TO_TEMP:
                save_income_statement_of_a_season_to_temp(s1_data)
        lib.tool.delay_short_seconds()

    if not s2_data:
        s2_data = get_income_statement_from_url(stock_no, year, 2)
        if s2_data:
            if data_fetch.config.AUTO_SAVE_TO_DB:
                save_income_statement_of_a_season_to_db(s2_data)
            if data_fetch.config.AUTO_SAVE_TO_TEMP:
                save_income_statement_of_a_season_to_temp(s2_data)
        lib.tool.delay_short_seconds()

    if not s3_data:
        s3_data = get_income_statement_from_url(stock_no, year, 3)
        if s3_data:
            if data_fetch.config.AUTO_SAVE_TO_DB:
                save_income_statement_of_a_season_to_db(s3_data)
            if data_fetch.config.AUTO_SAVE_TO_TEMP:
                save_income_statement_of_a_season_to_temp(s3_data)
        lib.tool.delay_short_seconds()

    if not year_data:
        year_data = get_income_statement_from_url(stock_no, year, 4)
        if year_data:
            if data_fetch.config.AUTO_SAVE_TO_DB:
                save_income_statement_of_a_season_to_db(year_data)
            if data_fetch.config.AUTO_SAVE_TO_TEMP:
                save_income_statement_of_a_season_to_temp(year_data)
        lib.tool.delay_short_seconds()

    if s1_data and s2_data and s3_data and year_data:
        s4_data = {
            'stock_no': stock_no,
            'year': year,
            'season': 4
        }
        for key, value in year_data.items():
            # no include percent column
            if '_p' == key[len(key)-2:] or key in ['stock_no', 'year', 'season']:
                continue
            s1_value = s1_data[key]
            s2_value = s2_data[key]
            s3_value = s3_data[key]
            year_value = year_data[key]

            if '' == s1_value:
                s1_value = 0
            if '' == s2_value:
                s2_value = 0
            if '' == s3_value:
                s3_value = 0

            if '' == year_value:
                s4_data[key] = ''
            else:
                s4_data[key] = year_value - s1_value - s2_value - s3_value

        s4_operating_revenue = s4_data['operating_revenue']
        if 0 == float(s4_operating_revenue):
            s4_data['operating_revenue_p'] = 0.0
        else:
            s4_data['operating_revenue_p'] = 1.0
        # calculate percent
        for key, value in s4_data.items():
            # columns with not need percent
            if key in [
                'operating_revenue',
                'operating_revenue_p',
                'stock_no',
                'year',
                'season'
            ] + except_percent_columns:
                continue
            percent_key = key + '_p'
            if '' == value:
                s4_data[percent_key] = ''
            else:
                if 0 == float(s4_operating_revenue):
                    s4_data[percent_key] = 0.0
                else:
                    s4_data[percent_key] = round(float(value) / float(s4_operating_revenue), 4)
        s4_data = lib.tool.fill_default_value_if_column_not_exist(dict_format, s4_data, except_percent_columns)
    return s4_data


def get_income_statement_of_a_season_from_url(stock_no='2330', year=2019, season=1):    
    result = None
    if season in [1, 2, 3]:
        result = get_income_statement_from_url(stock_no, year, season)
    elif 4 == season:
        result = get_income_statement_of_a_season4(stock_no, year)
    elif 5 == season:
        result = get_income_statement_from_url(stock_no, year, 4)
    return result


def get_income_statement_of_a_season_from_db(stock_no='2330', year=2019, season=1):
    table = database.config.INCOME_STATEMENT_TABLE
    sql = "SELECT * FROM {} WHERE stock_no='{}' and year='{}' and season='{}';".format(table, stock_no, year, season)
    result = db_manager.select_query(sql, return_dict=True)
    if result:
        return lib.tool.byteify(result[0])
    return None


def get_income_statement_of_a_season(stock_no='2330', year=2019, season=1):
    result = get_income_statement_of_a_season_from_temp(stock_no, year, season)
    if not result:
        result = get_income_statement_of_a_season_from_db(stock_no, year, season)
        if not result:
            result = get_income_statement_of_a_season_from_url(stock_no, year, season)
            if result and data_fetch.config.AUTO_SAVE_TO_DB:
                save_income_statement_of_a_season_to_db(result)
            lib.tool.delay_short_seconds()
        if result and data_fetch.config.AUTO_SAVE_TO_TEMP:
            save_income_statement_of_a_season_to_temp(result)
    return result


if __name__ == "__main__":
    import pprint as pp

    # # test get_income_statement_of_a_season_from_url
    # d = get_income_statement_of_a_season_from_url()
    # pp.pprint(d)

    # # test get_income_statement_of_a_season_from_temp
    # r = get_income_statement_of_a_season_from_temp()
    # pp.pprint(r)

    # # test get_income_statement_of_a_season_from_url
    # s = get_income_statement_of_a_season_from_url('2330', 2018, 4)
    # pp.pprint(s)

    # # test get_income_statement_of_a_season_from_db
    # s = get_income_statement_of_a_season_from_db('2330', 2018, 4)
    # pp.pprint(s)

    # # test get_income_statement_of_a_season
    # r = get_income_statement_of_a_season('2330', 2018, 4)
    # pp.pprint(r)

    # test get_income_statement_of_a_season
    # date = [
    #     [2017, 1],
    #     [2017, 2],
    #     [2017, 3],
    #     [2017, 4],
    #     [2018, 1],
    #     [2018, 2],
    #     [2018, 3],
    #     [2018, 4]
    # ]
    # for d in date:
    #     y = d[0]
    #     s = d[1]
    #     r = get_income_statement_of_a_season('2330', y, s)
    #     pp.pprint(r)
    #     lib.tool.delay_short_seconds()
    # r = get_income_statement_from_url('2330', 2018, 4)
    # pp.pprint(r)

    # # test update_income_statement_of_a_season_to_db
    # r = update_income_statement_of_a_season_to_db('2330', 2018, 4)
    # pp.pprint(r)

    # # test bank
    # r = get_income_statement_of_a_season_from_url('2891', 2019, 1)
    # pp.pprint(r)

    # # test 2207 with "收入合計" column
    # r = get_income_statement_of_a_season_from_url('2207', 2018, 4)
    # pp.pprint(r)

    # # test 6541 with "收入合計" column
    # r = get_income_statement_of_a_season_from_url('6541', 2018, 4)
    # pp.pprint(r)

    pass
