# -*- coding: utf-8 -*-
"""
Created on 2018/4/26 13:38

此版本只計算當天最新發佈的財報
@author: demonickrace
"""
import requests
import time
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from database import mysql_manager
from data_fetch import finanical_statement_fetch
from data_fetch import stock_fetch

manager = mysql_manager.MysqlManager()

# 顯示訊息
SHOW_MSG = True

# 爬資料delay時間
wait_seconds = 15

# 目標日期
target_date = datetime.today().strftime('%Y-%m-%d')
# target_date = "2018-08-17"

# 過濾之產業
ban_list = ["金融保險業", "建材營造業"]

# 預計算之季別時間
target_year = 2019
target_season = 2

# 欄位名稱
data_row = [
    ['股票代號', '公司名稱',
     '{}收盤價'.format(target_date),
     '近四季eps',
     '近四季本益比',
     "{}年第{}季eps".format(target_year, target_season),
     "{}年第{}季eps".format(target_year - 1, target_season),
     '{}年第{}季-{}年第{}季之eps成長率'.format(target_year, target_season, target_year - 1, target_season),
     '修正後近四季本益比',
     '{}年第{}季營業利益 (損失)(千元)'.format(target_year, target_season),
     '{}年第{}季營業利益 (損失)(千元)'.format(target_year - 1, target_season),
     '{}年第{}季-{}年第{}季營業利益 (損失)成長率'.format(target_year, target_season, target_year - 1, target_season),
     '每股現金淨值',
     '判斷訊息']]
"""
[company_no, company_name,
today_market_price,
recent_4_season_eps_sum,
recent_4_season_per,
this_season_eps,
pre_season_eps,
this_season_to_pre_season_eps_grow_rate,
amended_recent_4_season_per,
this_season_net_income,
pre_season_net_income,
this_season_to_pre_season_net_income_grow_rate,
net_cash_of_per_share,
msg]
"""

# 對應資料夾名稱
temp_dir = "temp"
report_dir = "report"


# it will create_temp
def get_now_company_report_info():
    url = "https://mops.twse.com.tw/mops/web/t51sb10?Stp=R1"

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept-Encoding': 'utf-8'
    }

    match_company_set = set()
    try:
        html = requests.get(url, headers=header, timeout=20)
        soup = BeautifulSoup(html.content, "html.parser")
        buttons = soup.findAll("button")
        save_text = ""
        for b in buttons:
            msg = b.find("u").text
            print(msg)
            save_text += msg.encode('utf8') + "\n"
            match_company_no = match_process(msg.encode('utf8'))
            if match_company_no:
                match_company_set.add(match_company_no)
        #        print(match_company_set)
        create_temp(save_text, target_date)

    except Exception as e:
        print("get_report_info error... ")
        print(e.args)

    return list(match_company_set)


def match_process(msg_str):
    match_str = ["上櫃公司", "上市公司"]
    left_count = 0
    right_count = 0

    left_start_1 = 0
    right_end_1 = 0

    left_start_2 = 0
    right_end_2 = 0

    for i, c in enumerate(msg_str, 0):
        if c is '(' and left_count == 0:
            left_start_1 = i + 1
            left_count += 1
        elif c is ")" and right_count == 0:
            right_end_1 = i
            right_count += 1
        elif c is "(" and left_count > 0:
            left_start_2 = i + 1
        elif c is ")" and right_count > 0:
            right_end_2 = i
            break

    title = msg_str[left_start_1: right_end_1]
    company_no = msg_str[left_start_2: right_end_2]
    #    print(left_start_1, right_end_1)
    #    print(left_start_2, right_end_2)
    #    print("{}, {}\n".format(title, company_no))

    match_word = "IFRSs"
    if match_word in msg_str:
        for tmp in match_str:
            if title == tmp:
                return company_no

    return None


# 篩選條件
"""

1. 近四季eps找不到，無條件通過

2. 0 < 近四季本益比 <= 10

3. 最近一季eps 與 去年同季esp 之成長率(%) >=  近四季本益比

4. 最近一季[營業利益 (損失)] 與 去年同季[營業利益 (損失)] 之成長率(%) >= 近四季本益比

5. 最近一季每股現金淨值 >= 市價

6. 0 < 修正後近四季本益比 <= 10

7. 皆無條件符合，[不合格]

由1~7依序判斷，當前條件符合則做對應判斷

"""


def cal_qualification(stock_no, year, season,
                      today_market_price,
                      this_season_eps, pre_season_eps,
                      this_season_net_income, pre_season_net_income,
                      net_cash_of_per_share):
    if SHOW_MSG:
        print("company_no = {}, year = {}, season = {}, "
              "today_market_price = {}, "
              "this_season_eps = {}, pre_season_eps = {}, "
              "this_season_net_income = {}, pre_season_net_income = {}, "
              "net_cash_of_per_share = {}".format(stock_no, year, season,
                                                  today_market_price,
                                                  this_season_eps, pre_season_eps,
                                                  this_season_net_income, pre_season_net_income,
                                                  net_cash_of_per_share))

    # 必要資訊缺少，無條件不通過
    if stock_no is None or year is None or season is None or today_market_price is None:
        print("stock_no, year, season, today_market_price, this_year_eps someone is None")
        return [False, "必要資訊缺少，無條件不通過"]

    # 近四季eps
    recent_4_season_eps_sum = get_recent_4_season_eps_sum(stock_no, year, season)

    # 1. 近四季eps找不到，無條件通過
    if recent_4_season_eps_sum is None:
        msg = "1. 近四季eps找不到，無條件通過"
        print(msg)
        return [True, msg]

    if today_market_price is not None and float(recent_4_season_eps_sum) > 0:
        # 近四季本益比
        recent_4_season_per = float(today_market_price) / float(recent_4_season_eps_sum)

        # 2. 0 < 近四季本益比 <= 10
        if 0 < recent_4_season_per <= 10:
            msg = "2. 0 < 近四季本益比({}) <= 10".format(recent_4_season_per)
            print(msg)
            return [True, msg]

        # 3. 最近一季eps 與 去年同季esp 之成長率 >=  近四季本益比
        if this_season_eps is not None and pre_season_eps is not None and float(recent_4_season_per) > 0 \
                and float(pre_season_eps) > 0:
            # 最近一季eps 與 去年同季esp 之成長率
            this_season_to_pre_season_eps_grow_rate = \
                (float(this_season_eps) - float(pre_season_eps)) / float(pre_season_eps)
            if this_season_to_pre_season_eps_grow_rate * 100 >= recent_4_season_per:
                msg = "3. 最近一季eps 與 去年同季esp 之成長率({}%) >=  近四季本益比({})" \
                    .format(this_season_to_pre_season_eps_grow_rate * 100, recent_4_season_per)
                print(msg)
                return [True, msg]

        # 4. 最近一季[營業利益 (損失)] 與 去年同季[營業利益 (損失)] 之成長率(%) >= 近四季本益比
        if this_season_net_income is not None and pre_season_net_income is not None \
                and float(pre_season_net_income) > 0 and float(recent_4_season_per) > 0:
            # 最近一季[營業利益 (損失)] 與 去年同季[營業利益 (損失)] 之成長率
            this_season_to_pre_season_net_income_grow_rate = \
                (float(this_season_net_income) - float(pre_season_net_income)) / float(pre_season_net_income)
            if this_season_to_pre_season_net_income_grow_rate * 100 >= recent_4_season_per:
                msg = "4. 最近一季[營業利益 (損失)] 與 去年同季[營業利益 (損失)] 之成長率({}%) >= 近四季本益比({})" \
                    .format(this_season_to_pre_season_net_income_grow_rate * 100, recent_4_season_per)
                print(msg)
                return [True, msg]

    # 5. 最近一季每股現金淨值 >= 市價
    if net_cash_of_per_share is not None and today_market_price is not None:
        if float(net_cash_of_per_share) >= float(today_market_price):
            msg = "5. 最近一季每股現金淨值({}) >= 市價({})".format(net_cash_of_per_share, today_market_price)
            print(msg)
            return [True, msg]

    # 6. 0 < 修正後近四季本益比 <= 10
    if today_market_price is not None and net_cash_of_per_share is not None and float(net_cash_of_per_share) >= 0 \
            and recent_4_season_eps_sum is not None and float(recent_4_season_eps_sum) > 0:
        # 修正後近四季本益比
        amended_recent_4_season_per = (float(today_market_price) - float(net_cash_of_per_share)) \
                                      / float(recent_4_season_eps_sum)
        if 0 < amended_recent_4_season_per <= 10:
            msg = "6. 0 < 修正後近四季本益比({}) <= 10".format(amended_recent_4_season_per)
            print(msg)
            return [True, msg]

    # 上述條件皆不符合
    # 7. 皆無條件符合，[不合格]
    msg = "7. 皆無條件符合，[不合格]"
    print(msg)
    return [False, msg]


# 每股現金淨值(float)
def get_net_cash_of_per_share(stock_no, year, season):
    sql = "select CashAndCashEquivalents, " \
          "CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss, " \
          "CurrentAvailableForSaleFinancialAssets, " \
          "CurrentHeldToMaturityFinancialAssets, " \
          "NoncurrentLiabilities, " \
          "OrdinaryShare " \
          "from balance_sheet " \
          "where stock_no = '{}' and year = {} and season = {};".format(stock_no, year, season)
    result = manager.select_query(sql)

    if len(result) == 0:
        # 嘗試再爬取一次
        print("get_net_cash_of_per_share, stock_no:{}, year:{}, season:{} is no data, try to get data again,".
              format(stock_no, year, season))
        data = finanical_statement_fetch.balance_sheet_fetch_a_season(stock_no, year, season)
        manager.insert_balance_sheet_to_db(stock_no, year, season, data)
        result = manager.select_query(sql)
        if len(result) == 0:
            print("get_net_cash_of_per_share again failed...")
            return None

    CashAndCashEquivalents = result[0][0]
    CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss = result[0][1]
    CurrentAvailableForSaleFinancialAssets = result[0][2]
    CurrentHeldToMaturityFinancialAssets = result[0][3]
    NoncurrentLiabilities = result[0][4]
    OrdinaryShare = result[0][5]

    if SHOW_MSG:
        print("現金及約當現金(+) = {}, "
              "透過損益按公允價值衡量之金融資產-流動(+) = {}, "
              "備供出售金融資產-流動(+) = {}, "
              "持有至到期日金融資產-流動(+) = {}, "
              "非流動負債合計(-) = {}, "
              "普通股數 = {}".format(CashAndCashEquivalents,
                                 CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss,
                                 CurrentAvailableForSaleFinancialAssets,
                                 CurrentHeldToMaturityFinancialAssets,
                                 NoncurrentLiabilities,
                                 OrdinaryShare))

    if CashAndCashEquivalents is None:
        CashAndCashEquivalents = 0

    if CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss is None:
        CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss = 0

    if CurrentAvailableForSaleFinancialAssets is None:
        CurrentAvailableForSaleFinancialAssets = 0

    if CurrentHeldToMaturityFinancialAssets is None:
        CurrentHeldToMaturityFinancialAssets = 0

    if NoncurrentLiabilities is None:
        NoncurrentLiabilities = 0

    if OrdinaryShare is None:
        return None

    """
    print(CashAndCashEquivalents)
    print(CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss)
    print(CurrentAvailableForSaleFinancialAssets)
    print(CurrentHeldToMaturityFinancialAssets)
    print(NoncurrentLiabilities)
    print(OrdinaryShare)
    """
    try:
        net_cash = (int(CashAndCashEquivalents) +
                    int(CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss) +
                    int(CurrentAvailableForSaleFinancialAssets) +
                    int(CurrentHeldToMaturityFinancialAssets) -
                    int(NoncurrentLiabilities))

        net_cash_of_per_share = float(net_cash) / float(OrdinaryShare) * 10
        #    print(net_cash)
        print("每股現金淨值 = {}".format(net_cash_of_per_share))
        return net_cash_of_per_share
    except ValueError:
        print("get_net_cash_of_per_shares error...")
        return None


# 近四季eps和
def get_recent_4_season_eps_sum(stock_no, year, season):
    s4 = [year, season]
    s3 = 0
    s2 = 0
    s1 = 0
    eps_sum = 0

    if season == 3:
        s3 = [year, 2]
        s2 = [year, 1]
        s1 = [year - 1, 4]

    elif season == 2:
        s3 = [year, 1]
        s2 = [year - 1, 4]
        s1 = [year - 1, 3]

    elif season == 1:
        s3 = [year - 1, 4]
        s2 = [year - 1, 3]
        s1 = [year - 1, 2]

    if 1 <= season <= 3:
        s4_eps = get_a_season_eps(stock_no, s4[0], s4[1])
        s3_eps = get_a_season_eps(stock_no, s3[0], s3[1])
        s2_eps = get_a_season_eps(stock_no, s2[0], s2[1])
        s1_eps = get_a_season_eps(stock_no, s1[0], s1[1])
        if s4_eps is None or s3_eps is None or s2_eps is None or s1_eps is None:
            return None
        eps_sum = s4_eps + s3_eps + s2_eps + s1_eps
    elif season == 4:
        eps_sum = get_a_season_eps(stock_no, year, 5)
        if eps_sum is None:
            return None
    return float(eps_sum)


# 一季之eps
def get_a_season_eps(stock_no, year, season):
    sql_query = "select BasicEarningsLossPerShare from statement_of_comprehensive_income " \
                "where stock_no = '{}' and year = '{}' and season = '{}'".format(stock_no, year, season)

    result = manager.select_query(sql_query)

    #    print(result[0][0])
    try:
        # 缺資料則再爬取一次
        if len(result) == 0:
            data = finanical_statement_fetch.income_statement_fetch_a_season(stock_no, year, season)
            manager.insert_income_statement_to_db(stock_no, year, season, data)
            result = manager.select_query(sql_query)
            if len(result) > 0:
                val = float(result[0][0])
                return val
        else:
            if result[0][0] is None:
                return None
            else:
                return float(result[0][0])
        print("get_a_season_eps is None...")
    except ValueError:
        print("get_a_season_eps error...")
    return None


# 判斷所需之前置資料,
# NetOperatingIncomeLoss = 營業淨收
def get_company_data(company_no, year, season):
    sql_query = "SELECT NetOperatingIncomeLoss " \
                "FROM stock.statement_of_comprehensive_income " \
                "where stock_no = '{}' and year = '{}' and season = '{}';".format(company_no, year, season)
    ci_result = manager.select_query(sql_query, True)
    if len(ci_result) > 0:
        return ci_result
    else:
        # 嘗試再爬取一次
        print("get_company_data, stock_no:{}, year:{}, season:{} is no data, try to get data again,".
              format(company_no, year, season))
        data = finanical_statement_fetch.income_statement_fetch_a_season(company_no, year, season)
        manager.insert_income_statement_to_db(company_no, year, season, data)
        ci_result = manager.select_query(sql_query, True)
        if len(ci_result) > 0:
            return ci_result
        else:
            print("get_company_data again failed...")
            return None


# 確認此公司之綜合損益報表是否已存在
def is_income_statement_report_exist(company_no, year, season):
    sql_query = "select stock_no from statement_of_comprehensive_income " \
                "where stock_no = '{}' and year = '{}' and season = '{}';".format(company_no, year, season)
    result = manager.select_query(sql_query)
    if len(result) == 1:
        return True
    return False


# 確認此公司之資產負債報表是否已存在
def is_balance_sheet_report_exist(company_no, year, season):
    sql_query = "select stock_no from balance_sheet " \
                "where stock_no = '{}' and year = '{}' and season = '{}';".format(company_no, year, season)
    result = manager.select_query(sql_query)
    if len(result) == 1:
        return True
    return False


# 股價(float)
def get_price(stock_no, date):
    sql_query = "SELECT stock.close FROM stock.stock where stock_no = '{}' and date = '{}';".format(stock_no, date)
    result = manager.select_query(sql_query)
    # 若當天無成交價，則傳回最後成交之收盤價
    if len(result) == 1:
        return float(result[0][0])
    else:
        #
        insert_stock_data(stock_no, date)
        return get_last_deal_date_price(stock_no)


# 最後成交之收盤價
def get_last_deal_date_price(stock_no):
    sql_query = "select close from stock where stock_no = '{}' order by date desc;".format(stock_no)
    result = manager.select_query(sql_query)
    for price in result:
        if float(price[0]) > 0:
            return float(price[0])
    return None


# 插入某月股票價格資料
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
        data = stock_fetch.twse_fetch_a_month(stock_no, year, mon)
    elif otc == 1:
        data = stock_fetch.otc_fetch_a_month(stock_no, year, mon)

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


# 創建csv
def create_csv(data, file_name):
    target = r"{}/{}.csv".format(report_dir, file_name)

    with open(target, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows([row for row in data if row])
    print("{}.csv was built...".format(file_name))


# 創建temp
def create_temp(data, file_name):
    target = "{}/{}.txt".format(temp_dir, file_name)
    with open(target, 'w') as the_file:
        the_file.write(data)
    print("{}.txt was built...".format(file_name))


# 暫存檔
def get_data_from_temp(filename):
    with open(filename) as f:
        content = f.readlines()
    #        print(content)
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    match_company_set = set()
    for row in content:
        print(row)
        match_company_no = match_process(row)
        if match_company_no:
            match_company_set.add(match_company_no)
    data = list(match_company_set)
    print(data)
    return data


# 從資料庫之財報取得此年與去年同季之公司代號
def get_company_report_info_from_db(year, season):
    sql_list = [
        "select distinct stock_no from balance_sheet where year = '{}' and season = '{}';".format(year - 1, season),
        "select distinct stock_no from balance_sheet where year = '{}' and season = '{}';".format(year, season),
        "select distinct stock_no from statement_of_comprehensive_income where year = '{}' and season = '{}';"
            .format(year - 1, season),
        "select distinct stock_no from statement_of_comprehensive_income where year = '{}' and season = '{}';"
            .format(year, season)]

    company_no_set = set()

    for query in sql_list:
        try:
            result = manager.select_query(query)
            for row in result:
                company_no_set.add(row[0])
        #                print(row[0])
        except Exception as e:
            print(e.message)
    # print(len(company_no_set))
    return list(company_no_set)


# 主程式
def main():
    # 抓取此時刻最新公布之報表
    # all_company_no = get_now_company_report_info()

    # 使用暫存檔
    # all_company_no = get_data_from_temp(temp_dir + "/2018-08-13.txt")

    # 從資料庫抓取已儲存的資料
    all_company_no = get_company_report_info_from_db(target_year, target_season)

    file_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # 公司名稱資訊
    all_stock_info = stock_fetch.get_all_stock_info_from_csv()
    all_stock_info_company_name = {}
    for row in all_stock_info:
        # [代號] = [公司名稱, 產業類別]
        all_stock_info_company_name[row[0]] = [row[1], row[3]]

    year = target_year
    season = target_season

    for i, company_no in enumerate(all_company_no, 1):
        msg = "company_no:{}, year:{}, season:{}".format(company_no, year, season)
        print("\n{} is processing... {}/{}".format(msg, i, len(all_company_no)))
        # 公司資訊
        company_info = all_stock_info_company_name.get(company_no, None)

        if company_info is None:
            print("company info is None...")
            continue

        print("{}:{}".format(company_info[0], company_info[1]))

        ban = False
        # 過濾特定產業
        for ban_industry in ban_list:
            company_type = company_info[1]
            if ban_industry in company_type:
                print("{} is banned...".format(company_type))
                ban = True
                break

        if ban:
            continue

        # 確認新一季資料是否已存在
        if not is_income_statement_report_exist(company_no, year, season):
            data = finanical_statement_fetch.income_statement_fetch_a_season(company_no, year, season)
            manager.insert_income_statement_to_db(company_no, year, season, data)
        if not is_balance_sheet_report_exist(company_no, year, season):
            data = finanical_statement_fetch.balance_sheet_fetch_a_season(company_no, year, season)
            manager.insert_balance_sheet_to_db(company_no, year, season, data)

        today_market_price = get_price(company_no, target_date)

        # 取得今年前年之當季損益報表
        this_season_data = get_company_data(company_no, year, season)
        pre_season_data = get_company_data(company_no, year - 1, season)

        # 若今年這一季或前年這一季的資料為空
        if this_season_data is None or pre_season_data is None:
            print("{}, this_season_data or pre_season_data is None...".format(msg))
            continue

        this_season_net_income = None
        for this_season in this_season_data:
            this_season_net_income = this_season['NetOperatingIncomeLoss']

        pre_season_net_income = None
        for pre_season in pre_season_data:
            pre_season_net_income = pre_season['NetOperatingIncomeLoss']

        this_season_eps = get_a_season_eps(company_no, year, season)
        pre_season_eps = get_a_season_eps(company_no, year - 1, season)

        net_cash_of_per_share = get_net_cash_of_per_share(company_no, year, season)

        qualification = cal_qualification(company_no, year, season,
                                          today_market_price,
                                          this_season_eps, pre_season_eps,
                                          this_season_net_income, pre_season_net_income,
                                          net_cash_of_per_share)
        print("qualification = {}, msg = {}".format(qualification[0], qualification[1]))

        if qualification[0]:
            # 近四季本益比
            # recent_4_season_per = None
            # 近四季eps
            recent_4_season_eps_sum = get_recent_4_season_eps_sum(company_no, year, season)

            if recent_4_season_eps_sum is None or float(recent_4_season_eps_sum) == 0:
                recent_4_season_per = None
            else:
                recent_4_season_per = float(today_market_price) / float(recent_4_season_eps_sum)

            # 修正後近四季本益比
            # amended_recent_4_season_per = None
            if recent_4_season_eps_sum is None or float(recent_4_season_eps_sum) == 0 \
                    or net_cash_of_per_share is None or float(net_cash_of_per_share) == 0:
                amended_recent_4_season_per = None
            else:

                amended_recent_4_season_per = (float(today_market_price) - float(net_cash_of_per_share)) / float(
                    recent_4_season_eps_sum)

            # 公司名稱
            company_name = company_info[0]
            if company_name is None:
                company_name = "find no name"

            this_season_to_pre_season_eps_grow_rate = None
            if this_season_eps is not None and pre_season_eps is not None and float(pre_season_eps) > 0:
                # 最近一季eps 與 去年同季esp 之成長率
                this_season_to_pre_season_eps_grow_rate = \
                    (float(this_season_eps) - float(pre_season_eps)) / float(pre_season_eps)

            this_season_to_pre_season_net_income_grow_rate = None
            if this_season_net_income is not None and pre_season_net_income is not None \
                    and float(pre_season_net_income) > 0:
                # 最近一季[營業利益 (損失)] 與 去年同季[營業利益 (損失)] 之成長率
                this_season_to_pre_season_net_income_grow_rate = \
                    (float(this_season_net_income) - float(pre_season_net_income)) / float(pre_season_net_income)

            msg = qualification[1]

            row = [company_no, company_name,
                   today_market_price,
                   recent_4_season_eps_sum,
                   recent_4_season_per,
                   this_season_eps,
                   pre_season_eps,
                   this_season_to_pre_season_eps_grow_rate,
                   amended_recent_4_season_per,
                   this_season_net_income,
                   pre_season_net_income,
                   this_season_to_pre_season_net_income_grow_rate,
                   net_cash_of_per_share,
                   msg]

            data_row.append(row)
        else:
            print("{} is unqualified".format(msg))
            continue

    print("\nall data processed finish...\n")
    create_csv(data_row, file_name)


if __name__ == '__main__':
    #    string_process("10:27(公開發行公司)可取(4981)-10604-IFRSs會計師查核(核閱)報告")

    #    n = get_net_cash_of_per_share(3259, 2018, 1)
    #    print(n)
    #    get_a_season_eps(2330, 2017, 3)

    #    get_recent_4_season_eps_sum(2330, 2017, 3)
    #    d = get_company_data(2330, 2017, 3)
    #    print(d['BasicEarningsLossPerShare'])

    #    print(is_balance_sheet_report_exist(2330, 2018, 1))
    #    print(is_income_statement_report_exist(2330, 2018, 1))

    #    create_temp("test\ntest\n", "123.txt")

    # get_company_report_info_from_db(2018, 1)

    main()

    pass

"""
現金淨值=
現金及約當現金 + //CashAndCashEquivalents
透過損益按公允價值衡量之金融資產-流動 + //CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss
備供出售金融資產-流動 + //CurrentAvailableForSaleFinancialAssets
持有至到期日金融資產-流動 + //CurrentHeldToMaturityFinancialAssets
避險之衍生金融資產-流動 - // 略過
非流動負債合計 // NoncurrentLiabilities


普通股股本 //OrdinaryShare

每股現金淨值=
現金淨值 /  (普通股股本/10) 

select CashAndCashEquivalents, 
CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss, 
CurrentAvailableForSaleFinancialAssets,
CurrentHeldToMaturityFinancialAssets,
NoncurrentLiabilities
from balance_sheet

===============
選股方式

(成長法)
1.本益比<10
2.營業利益成長>0(數字增長不是比例增長)
3.  0 < 本益比 < EPS成長比 


(資產法)
挑選項目1.
每股現金淨值>股價

挑選項目2.

修正後本益比=
(股價 - 每股現金淨值 ) / 近4季EPS

0  < 修正後本益比 < 10

"""
