# -*- coding: utf-8 -*-
"""
Created on 2019/11/14 17:28

@author: demonickrace
"""
import json
import requests
import data_fetch.config
import data_fetch.log
import lib.tool
from bs4 import BeautifulSoup

dict_format = {
    # 流動資產
    "現金及約當現金": "cash_and_cash_equivalents",
    "現金及約當現金合計": "cash_and_cash_equivalents",
    "透過損益按公允價值衡量之金融資產-流動": "current_financial_assets_at_fair_value_through_profit_or_loss",
    "備供出售金融資產-流動淨額": "current_available_for_sale_financial_assets",
    "持有至到期日金融資產-流動淨額": "current_held_to_maturity_financial_assets",
    "應收帳款淨額": "accounts_receivable_net",
    "存貨": "inventories",
    "其他流動資產": "other_current_assets",
    "流動資產合計": "current_assets",
    # 非流動資產
    "採用權益法之投資": "investment_accounted_for_using_equity_method",
    "採用權益法之投資淨額": "investment_accounted_for_using_equity_method",
    "不動產、廠房及設備": "property_plant_and_equipment",
    "不動產、廠房及設備合計": "property_plant_and_equipment",
    "無形資產": "intangible_assets",
    "遞延所得稅資產": "deferred_tax_assets",
    "其他非流動資產": "other_noncurrent_assets",
    "非流動資產合計": "noncurrent_assets",
    ""
    "資產總額": "assets",
    # 流動負債
    "短期借款": "shortterm_borrowings",
    "短期借款合計": "shortterm_borrowings",
    "透過損益按公允價值衡量之金融負債-流動": "current_liabilities_c2",
    "透過損益按公允價值衡量之金融負債-流動合計": "current_liabilities_c2",
    "避險之衍生金融負債-流動": "current_derivative_financial_liabilities_for_hedging",
    "應付帳款": "accounts_payable",
    "其他應付款": "other_payables",
    "其他應付款合計": "other_payables",
    "本期所得稅負債": "current_tax_liabilities",
    "當期所得稅負債": "current_tax_liabilities",
    "負債準備-流動": "current_provisions",
    "負債準備-流動合計": "current_provisions",
    "其他流動負債": "other_current_liabilities",
    "其他流動負債合計": "other_current_liabilities",
    "流動負債合計": "current_liabilities",
    # 非流動負債
    "應付公司債": "bonds_payable",
    "應付公司債合計": "bonds_payable",
    "長期借款": "longterm_borrowings",
    "長期借款合計": "longterm_borrowings",
    "其他非流動負債": "other_noncurrent_liabilities",
    "其他非流動負債合計": "other_noncurrent_liabilities",
    "非流動負債合計": "noncurrent_liabilities",
    "負債總計": "liabilities",
    "負債總額": "liabilities",
    # # 歸屬於母公司業主之權益
    # 股本
    "普通股股本": "ordinary_share",
    "股本合計": "capital_stock",
    # 資本公積
    "資本公積-發行溢價": "capital_surplus_additional_paid_in_capital",
    "資本公積-認列對子公司所有權權益變動數": "capital_surplus_c2",
    "資本公積-受贈資產": "capital_surplus_donated_assets_received",
    "資本公積-採用權益法認列關聯企業及合資股權淨值之變動數": "capital_surplus_c4",
    "資本公積-合併溢額": "capital_surplus_net_assets_from_merger",
    "資本公積合計": "capital_surplus",
    # 保留盈餘
    "法定盈餘公積": "legal_reserve",
    "未分配盈餘(或待彌補虧損)": "retained_earnings_c2",
    "保留盈餘合計": "retained_earnings",
    # 其他權益
    "其他權益合計": "other_equity_interest",
    "歸屬於母公司業主之權益合計": "equity_attributable_to_owners_of_parent",
    "非控制權益": "noncontrolling_interests",
    "權益總計": "equity",
    "權益總額": "equity",
    "預收股款(權益項下)之約當發行股數(單位:股)": "balance_sheet_other_column_1",
    "母公司暨子公司所持有之母公司庫藏股股數(單位:股)": "balance_sheet_other_column_2",
}


def save_balance_sheet_of_a_season_to_temp(data=None):
    try:
        if not data:
            raise Exception('save_balance_sheet_of_a_season_to_temp fail, input data is None!')

        date = '{}-{}'.format(data['year'], data['season'])
        key = '{}-{}'.format(data['stock_no'], date)
        target_file = data_fetch.config.FS_BALANCE_SHEET_PATH + '/{}.json'.format(date)

        lib.tool.init_json_file_if_not_exist(target_file)
        json_obj = lib.tool.get_json_obj_from_temp_file(target_file)

        # check data exist
        with open(target_file, 'w') as temp_file:
            json_obj[key] = data
            save_data = json.dumps(json_obj, indent=4, sort_keys=True)
            temp_file.write(save_data)
        return True
    except Exception as e:
        msg = 'save_balance_sheet_of_a_season_to_temp error, msg = {}'.format(e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)
        return False


def get_balance_sheet_of_a_season_from_temp(stock_no='2330', year=2019, season=1):
    try:
        date = '{}-{}'.format(year, season)
        key = '{}-{}'.format(stock_no, date)
        target_file = data_fetch.config.FS_BALANCE_SHEET_PATH + '/{}.json'.format(date)

        lib.tool.init_json_file_if_not_exist(target_file)
        json_obj = lib.tool.get_json_obj_from_temp_file(target_file)
        result = json_obj.get(key, None)
        return result
    except Exception as e:
        msg = 'get_balance_sheet_of_a_season_from_temp error, file = {}.json, msg = {}'.format(key, e.args)
        print(msg)
        log = data_fetch.log.Log()
        log.write_fetch_err_log(msg)
        return None


def get_balance_sheet_of_a_season_from_url(stock_no='2330', year=2019, season=1):
    global dict_format
    year_season = "{}-{}".format(year, season)
    try:
        query_year = year
        if 1911 < query_year:
            query_year -= 1911

        header = data_fetch.config.HEADER
        url = data_fetch.config.MOPS_BALANCE_SHEET_URL
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
            'queryName': 'co_id',
            'inpuType': 'co_id',
            'TYPEK': 'all',
            'isnew': 'false',
            'co_id': stock_no,
            'year': query_year,
            'season': season
        }
        """
        # 一般產業股
        encodeURIComponent: 1,
        step: 1,
        firstin: 1,
        off: 1,
        keyword4: '',
        code1: '',
        TYPEK2: '',
        checkbtn: '',
        queryName: 'co_id',
        inpuType: 'co_id',
        TYPEK: 'all',
        isnew: 'false',
        co_id: 2330,
        year: 108,
        season': 01
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
        msg = 'get_balance_sheet_of_a_season_from_url error, year_season = {}, msg = {}'.format(year_season, e.args)
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
    except_columns = []
    for row in data:
        row[0] = row[0].encode('utf8', 'ignore')
        row[1] = row[1].encode('utf8', 'ignore')
        row[2] = row[2].encode('utf8', 'ignore')
        if row[0] in dict_format and '' != row[1]:
            key = dict_format.get(row[0], None)
            key_p = key + "_p"
            if '' != row[1]and key:
                dict_data[key] = int(row[1]) * 1000
            if '' != row[2] and key_p:
                dict_data[key_p] = float(row[2]) / 100.0

    info = {'stock_no': stock_no, 'year': year, 'season': season}
    if dict_data:
        dict_data.update(info)
        dict_data = lib.tool.fill_default_value_if_column_not_exist(dict_format, dict_data, except_columns)
        # 儲存至temp
        save_balance_sheet_of_a_season_to_temp(dict_data)

    return dict_data


def get_balance_sheet_of_a_season(stock_no='2330', year=2019, season=1):
    result = get_balance_sheet_of_a_season_from_temp(stock_no, year, season)
    if not result:
        result = get_balance_sheet_of_a_season_from_url(stock_no, year, season)
    return result


if __name__ == '__main__':
    import pprint as pp

    # # test get_balance_sheet_of_a_season_from_url
    # r = get_balance_sheet_of_a_season_from_url()
    # pp.pprint(r)

    # # test get_balance_sheet_of_a_season_from_temp
    # r = get_balance_sheet_of_a_season_from_temp()
    # pp.pprint(r)

    # # test get_balance_sheet_of_a_season
    # r = get_balance_sheet_of_a_season()
    # pp.pprint(r)

    pass
