# -*- coding: utf-8 -*-
"""
Created on 2017/9/18 09:59

@author: demonickrace
"""
import time
import requests
import random
import csv
import datetime
import data_fetch.config
from bs4 import BeautifulSoup
from database import mysql_manager

manager = mysql_manager.MysqlManager()

income_statement_dict_s1 = None
income_statement_dict_s2 = None
income_statement_dict_s3 = None

max_retry_seconds = 20
min_retry_seconds = 15

max_wait_seconds = 20
min_wait_seconds = 10

retry_count = 0


def income_statement_fetch_a_season(co_id=2330, year=106, season=1):
    global retry_count
    global income_statement_dict_s1
    global income_statement_dict_s2
    global income_statement_dict_s3

    if year > 1911:
        year -= 1911

    get_a_year = False

    if season == 5:
        get_a_year = True
        season = 4

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb04"
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
        'co_id': co_id,
        'year': year,
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
        'queryName': 'co_id',
        'inpuType': 'co_id',
        'TYPEK': 'all',
        'isnew': 'false',
        'co_id': 2330,
        'year': 105,
        'season': 02
    """
    """
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

    header = {
       'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
       'Accept-Encoding': 'utf-8'
    }

    soup = None
    table = None
    try:
        html = requests.post(url, data=form_data, headers=header, timeout=20)
        soup = BeautifulSoup(html.content.decode("utf8"), "html.parser")
        table = soup.find("table", "hasBorder")
    except Exception as e:
        print(e.args)

    if soup is None:
        print("page not fail... try to read again...")
        time.sleep(random.randint(min_retry_seconds, max_retry_seconds))
        return income_statement_fetch_a_season(co_id, year, season)

    data = []

    all_row = None

    try:
        all_row = table.find_all("tr")
    except Exception as e:
        print(e.args)

    if all_row is None:
        #        print(soup.find("h3").text)
        #        print(table)
        msg = None
        try:
            if soup.find("h3").text is not None:
                return None
            msg = soup.find("h4").find("font").text
        except Exception as e:
            print(e.args)
            return None

        if msg == u"查無所需資料！":
            print("stock_no = {}, year = {}, season = {}, website find no data for the season!".format(co_id, year, season))
            return None
        else:
            print("stock_no = {}, year = {}, season = {}, website is busy and find no data!".format(co_id, year, season))

        retry_count += 1

        if retry_count > 5:
            retry_count = 0
            print("retry_count > 5 , wait for few seconds...")
            time.sleep(max_retry_seconds)

        time.sleep(random.randint(min_retry_seconds, max_retry_seconds))
        return income_statement_fetch_a_season(co_id, year, season)

    retry_count = 0

    for i, tr in enumerate(all_row, 1):
        if i > 4:
            row = []
            for j, td in enumerate(tr.find_all("td"), 1):
                if j > 3:
                    break
                col = td.text.strip().encode("utf8").replace(",", "")
                row.append(full_to_half(col))
            data.append(row)

    dict_format = {
        "營業收入合計": "OperatingRevenue",
        "營業成本合計": "OperatingCosts",
        "營業毛利(毛損)": "GrossProfitLossFromOperations",
        "未實現銷貨(損)益": "UnrealizedProfitLossFromSales",
        "已實現銷貨(損)益": "RealizedProfitLossOnFromSales",
        "營業毛利(毛損)淨額": "GrossProfitLossFromOperationsNet",
        #營業費用
        "推銷費用": "SellingExpenses",
        "管理費用": "AdministrativeExpense",
        "研究發展費用": "ResearchAndDevelopmentExpenses",
        "營業費用合計": "OperatingExpenses",
        #其他收益及費損淨額
        "其他收益及費損淨額": "NetOtherIncomeExpenses",
        "營業利益(損失)": "NetOperatingIncomeLoss",
        #營業外收入及支出
        "其他收入": "OtherIncomeOthers",
        "其他利益及損失淨額": "OtherGainsLosses",
        "財務成本淨額": "FinanceCosts",
        "採用權益法認列之關聯企業及合資損益之份額淨額": "Y1",
        "營業外收入及支出合計": "NonoperatingIncomeAndExpenses",
        "稅前淨利(淨損)": "ProfitLossBeforeTax",
        "所得稅費用(利益)合計": "IncomeTaxExpenseContinuingOperations",
        "繼續營業單位本期淨利(淨損)": "ProfitLossFromContinuingOperations",
        "本期淨利(淨損)": "ProfitLoss",
        #後續可能重分類至損益之項目
        "國外營運機構財務報表換算之兌換差額": "Y3",
        "備供出售金融資產未實現評價損益": "Y4",
        "採用權益法認列關聯企業及合資之其他綜合損益之份額-可能重分類至損益之項目": "Y2",
        "與可能重分類之項目相關之所得稅": "IncomeTaxRelatingToComponentsOfOtherComprehensiveIncome",
        "其他綜合損益(淨額)": "OtherComprehensiveIncome",
        "本期綜合損益總額": "ComprehensiveIncome",
        "母公司業主(淨利/損)": "ProfitLossAttributableToOwnersOfParent",
        "非控制權益(淨利∕損)": "ProfitLossAttributableToNoncontrollingInterests",
        "母公司業主(綜合損益)": "ComprehensiveIncomeAttributableToOwnersOfParent",
        "非控制權益(綜合損益)": "ComprehensiveIncomeAttributableToNoncontrollingInterests",
        #基本每股盈餘
        "基本每股盈餘": "BasicEarningsLossPerShare",
        #稀釋每股盈餘
        "稀釋每股盈餘": "DilutedEarningsLossPerShare"
    }

    dict_data = {}

    for row in data:
        row[0] = row[0].encode('utf8', 'ignore')
        row[1] = row[1].encode('utf8', 'ignore')
        row[2] = row[2].encode('utf8', 'ignore')
#        print row[0], row[0] in dict_format
#        print row[0], row[1], row[2]
        if row[0] in dict_format and row[1] != "":
#            key = unicode(row[0], "utf8", errors="ignore")
#            key = row[0]
            key = dict_format.get(row[0], None)
            key_p = key + "_p"
            if row[1] != "" and key is not None:
                dict_data[key] = row[1]
#                print("{} = {}".format(key, dict_data[key]))
            if row[2] != "" and key_p is not None:
                dict_data[key_p] = float(row[2]) / 100.0
#                print("{} = {}".format(key_p, dict_data[key_p]))
#            print row[0], row[1], row[2]

    if get_a_year:
        season = 5
    elif season == 1:
        income_statement_dict_s1 = dict_data
    elif season == 2:
        income_statement_dict_s2 = dict_data
    elif season == 3:
        income_statement_dict_s3 = dict_data
    elif season == 4:
        if income_statement_dict_s1 is None:
            time.sleep(2)
            income_statement_dict_s1 = income_statement_fetch_a_season(co_id, year, 1)
        if income_statement_dict_s2 is None:
            time.sleep(2)
            income_statement_dict_s2 = income_statement_fetch_a_season(co_id, year, 2)
        if income_statement_dict_s3 is None:
            time.sleep(2)
            income_statement_dict_s3 = income_statement_fetch_a_season(co_id, year, 3)

        dict_data = process_income_statement_season_4(dict_data)
        # reset s1~s2
        income_statement_dict_s1 = None
        income_statement_dict_s2 = None
        income_statement_dict_s3 = None

    if year < 1911:
        year += 1911

    info = {'stock_no': co_id, 'year': year, 'season': season}

    if dict_data is not None:
        dict_data.update(info)

    return dict_data


def process_income_statement_season_4(dict_data):

    global income_statement_dict_s1
    global income_statement_dict_s2
    global income_statement_dict_s3

    # check s1~s3 are not none
    if income_statement_dict_s1 is None or income_statement_dict_s2 is None or income_statement_dict_s3 is None or dict_data is None:
        print("error: income_statement_dict_s1, income_statement_dict_s2, income_statement_dict_s3, dict_data can not be none!")
        return None

    dict_year = dict_data
    dict_s4 = {}

    # 營業收入合計
    y_OperatingRevenue = dict_year.get('OperatingRevenue', None)
    s1_OperatingRevenue = income_statement_dict_s1.get('OperatingRevenue', None)
    s2_OperatingRevenue = income_statement_dict_s2.get('OperatingRevenue', None)
    s3_OperatingRevenue = income_statement_dict_s3.get('OperatingRevenue', None)

    s4_operating_revenue = 0

    if y_OperatingRevenue and s1_OperatingRevenue and s2_OperatingRevenue and s3_OperatingRevenue:
            dict_s4['OperatingRevenue'] = float(y_OperatingRevenue) - float(s1_OperatingRevenue) - \
                                          float(s2_OperatingRevenue) - float(s3_OperatingRevenue)
            s4_operating_revenue = dict_s4['OperatingRevenue']
            dict_s4['OperatingRevenue_p'] = 1.0

    # no compute
    except_cols = ["OperatingRevenue"]

    # iterate cols
    for key, value in dict_year.items():
        if key not in except_cols and "_p" not in key:
            temp = compute_income_statement_season_4(key, dict_year, s4_operating_revenue)
            dict_s4.update(temp)

    return dict_s4


def compute_income_statement_season_4(col_name, dict_year, s4_operating_revenue):
    global income_statement_dict_s1
    global income_statement_dict_s2
    global income_statement_dict_s3

    except_percent = ["BasicEarningsLossPerShare", "DilutedEarningsLossPerShare"]
    dict_s4_temp = {}

    y = dict_year.get(col_name, None)
    s1 = income_statement_dict_s1.get(col_name, None)
    s2 = income_statement_dict_s2.get(col_name, None)
    s3 = income_statement_dict_s3.get(col_name, None)

    if y and s1 and s2 and s3 and float(s4_operating_revenue) != 0:
        dict_s4_temp[col_name] = float(y) - float(s1) - float(s2) - float(s3)
        if col_name not in except_percent and "_p" not in col_name:
            col_p = col_name + "_p"
            dict_s4_temp[col_p] = round(float(dict_s4_temp[col_name]) / float(s4_operating_revenue), 4)
#            print(col_name, dict_s4_temp[col_name], s4_operating_revenue, dict_s4_temp[col_p])
#    print("col_name = " + col_name, dict_s4_temp)
    return dict_s4_temp


def balance_sheet_fetch_a_season(co_id=2330, year=106, season=1):
    global retry_count

    if year > 1911:
        year -= 1911

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb03"
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
        'co_id': co_id,
        'year': year,
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
        'queryName': 'co_id',
        'inpuType': 'co_id',
        'TYPEK': 'all',
        'isnew': 'false',
        'co_id': 2330,
        'year': 105,
        'season': 02
    """
    """
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

    header = {
       'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
       'Accept-Encoding': 'utf-8'
    }

    soup = None
    table = None
    try:
        html = requests.post(url, data=form_data, headers=header, timeout=20)
        soup = BeautifulSoup(html.content.decode("utf8"), "html.parser")
        table = soup.find("table", "hasBorder")
    except Exception as e:
        print(e.args)

    if soup is None:
        print("page not fail... try to read again...")
        time.sleep(random.randint(min_retry_seconds, max_retry_seconds))
        return balance_sheet_fetch_a_season(co_id, year, season)

    data = []

    all_row = None

    try:
        all_row = table.find_all("tr")
    except Exception as e:
        print(e.args)

    if all_row is None:
        msg = None
        try:
            if soup.find("h3").text is not None:
                return None
            msg = soup.find("h4").find("font").text
        except Exception as e:
            print(e.args)
            return None

        if msg == u"查無所需資料！":
            print("stock_no = {}, year = {}, season = {} ,website find no data for the season!".format(co_id, year, season))
            return None
        else:
            print("stock_no = {}, year = {}, season = {} ,website is busy and find no data!".format(co_id, year, season))

        retry_count += 1

        if retry_count > 5:
            retry_count = 0
            #            print(soup)
            print("retry_count > 5 , wait for few seconds...")
            time.sleep(max_retry_seconds)

        time.sleep(random.randint(min_retry_seconds, max_retry_seconds))
        return balance_sheet_fetch_a_season(co_id, year, season)

    retry_count = 0

    for i, tr in enumerate(all_row, 1):
        if i > 4:
            row = []
            for j, td in enumerate(tr.find_all("td"), 1):
                if j > 3:
                    break
                col = td.text.strip().encode("utf8").replace(",", "")
                row.append(full_to_half(col))
#            print(row[0], row[1], row[2])
            data.append(row)

    dict_format = {
        #流動資產
            "現金及約當現金": "CashAndCashEquivalents",
            "透過損益按公允價值衡量之金融資產-流動": "CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss",
            "備供出售金融資產-流動淨額": "CurrentAvailableForSaleFinancialAssets",
            "持有至到期日金融資產-流動淨額": "CurrentHeldToMaturityFinancialAssets",
           #避險之衍生金融資產-流動
            "應收帳款淨額": "AccountsReceivableNet",
            "應收帳款-關係人淨額": "AccountsReceivableDuefromRelatedPartiesNet",
            "其他應收款-關係人淨額": "OtherReceivablesDueFromRelatedParties",
            "存貨": "Inventories",
            "其他流動資產": "OtherCurrentAssets",
           "流動資產合計": "CurrentAssets",
        #非流動資產
            #持有至到期日金融資產-非流動淨額
            #以成本衡量之金融資產-非流動淨額
            "採用權益法之投資淨額": "InvestmentAccountedForUsingEquityMethod",
            "不動產、廠房及設備": "PropertyPlantAndEquipment",
            "無形資產": "IntangibleAssets",
           "遞延所得稅資產": "DeferredTaxAssets",
            "其他非流動資產": "OtherNoncurrentAssets",
            "非流動資產合計": "NoncurrentAssets",
        #資產總計
        #流動負債
            "短期借款": "ShorttermBorrowings",
            "透過損益按公允價值衡量之金融負債-流動": "CurrentFinancialLiabilitiesAtFairValueThroughProfitOrLoss",
            "避險之衍生金融負債-流動": "CurrentDerivativeFinancialLiabilitiesForHedging",
            "應付帳款": "AccountsPayable",
            "應付帳款-關係人": "AccountsPayableToRelatedParties",
            "其他應付款": "OtherPayables",
           "本期所得稅負債": "CurrentTaxLiabilities",
            "負債準備-流動": "CurrentProvisions",
            "其他流動負債": "OtherCurrentLiabilities",
            "流動負債合計": "CurrentLiabilities",
        #非流動負債
            "應付公司債": "BondsPayable",
            "長期借款": "LongtermBorrowings",
            #遞延所得稅負債
            "其他非流動負債": "OtherNoncurrentLiabilities",
           "非流動負債合計": "NoncurrentLiabilities",
        "負債總計": "Liabilities",
        #歸屬於母公司業主之權益
           #股本
            "普通股股本": "OrdinaryShare",
           "股本合計": "CapitalStock",
        #資本公積
            "資本公積-發行溢價": "CapitalSurplusAdditionalPaidInCapital",
            "資本公積-認列對子公司所有權權益變動數": "CapitalSurplusChangesInOwnershipInterestsInSubsidiaries",
            "資本公積-受贈資產": "CapitalSurplusDonatedAssetsReceived",
           "資本公積-採用權益法認列關聯企業及合資股權淨值之變動數": "X2",
            "資本公積-合併溢額": "CapitalSurplusNetAssetsFromMerger",
           "資本公積合計": "CapitalSurplus",
        #保留盈餘
            "法定盈餘公積": "LegalReserve",
            "未分配盈餘(或待彌補虧損)": "UnappropriatedRetainedEarningsAaccumulatedDeficit",
           "保留盈餘合計": "RetainedEarnings",
        #其他權益
            "其他權益合計": "OtherEquityInterest",
        "歸屬於母公司業主之權益合計": "EquityAttributableToOwnersOfParent",
        "非控制權益": "NoncontrollingInterests",
        "權益總計": "Equity",
        #負債及權益總計
        "預收股款(權益項下)之約當發行股數(單位:股)": "EquivalentIssueSharesOfAdvanceReceiptsForOrdinaryShare",
        "母公司暨子公司所持有之母公司庫藏股股數(單位:股)": "NumberOfSharesInEntityHeldByEntityAndByItsSubsidiaries"
    }

    dict_data = {}

    for row in data:
        row[0] = row[0].encode('utf8', 'ignore')
        row[1] = row[1].encode('utf8', 'ignore')
        row[2] = row[2].encode('utf8', 'ignore')
        #        print row[0], row[0] in dict_format
        #        print row[0], row[1], row[2]
        if row[0] in dict_format and row[1] != "":
            #            key = unicode(row[0], "utf8", errors="ignore")
            #            key = row[0]
            key = dict_format.get(row[0], None)
            key_p = key + "_p"
            if row[1] != "" and key is not None:
                dict_data[key] = row[1]
            #                print("{} = {}".format(key, dict_data[key]))
            if row[2] != "" and key_p is not None:
                dict_data[key_p] = float(row[2]) / 100.0


#                print("{} = {}".format(key_p, dict_data[key_p]))
#            print row[0], row[1], row[2]

    if year < 1911:
        year += 1911

    info = {'stock_no': co_id, 'year': year, 'season': season}

    if dict_data is not None:
        dict_data.update(info)

    return dict_data


#   （Ａ）=> (A)
def full_to_half(s):
    n = []
    s = s.decode('utf-8')
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        num = unichr(num)
        n.append(num)
    return ''.join(n)


def insert_all():

    data = []

    twse_file = "twse_info_list.csv"
    with open(twse_file) as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, 1):
            if i == 1:
                continue
            data.append([row[0], row[1], row[2], row[3]])
    #            print (row[0], row[1], row[2], row[3])

    otc_file = "otc_info_list.csv"
    with open(otc_file) as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, 1):
            if i == 1:
                continue
            data.append([row[0], row[1], row[2], row[3]])
    #            print (row[0], row[1], row[2], row[3])

#    today = time.strftime("%Y/%m/%d")

    #    this_year = 2016
    #    this_month = 7

    this_year = datetime.datetime.now().year
    this_month = datetime.datetime.now().month

    this_season = 1

    target_year = this_year

    if 12 == this_month or (1 <= this_month <= 3) :
        this_season = 4
        target_year -= 1
    elif 4 <= this_month <= 7:
        this_season = 2
    elif 8 <= this_month <= 11:
        this_season = 3

    target_season = this_season

    if target_season == 4:
        target_season = 5

    ifrs_date = time.strptime("2013/01/01", "%Y/%m/%d")

    # [股票代號, 公司名稱, 上櫃/市日期,    產業別]
    for row in data:
        if "金融" not in row[3]:
            print("{}, {}, {}, {}".format(row[0], row[1], row[2], row[3]))
            stock_listing_date = time.strptime(row[2], "%Y/%m/%d")

            start_year = 102 + 1911

            start_season = 1

            if stock_listing_date > ifrs_date:
                start_year = int(row[2].split("/")[0])
                start_month = int(row[2].split("/")[1])
                if 1 <= start_month <= 3:
                    start_season = 1
                elif 4 <= start_month <= 7:
                    start_season = 2
                elif 8 <= start_month <= 11:
                    start_season = 3
                else:
                    start_season = 4
#                print(start_year, start_season)

            year_season = [[y, s] for y in range(start_year, start_year + 1) for s in range(start_season, 6)]
            year_season.extend([[y, s] for y in range(start_year + 1, target_year) for s in range(1, 6)])
            year_season.extend([[target_year, s] for s in range(1, target_season + 1)])

            stock_id = row[0]
            for r in year_season:
                year = r[0]
                season = r[1]
#                print(year, season)
                time.sleep(random.randint(min_wait_seconds, max_wait_seconds))
                d = income_statement_fetch_a_season(stock_id, year, season)
                # print(d)
                if d is None:
                    break
                manager.insert_income_statement_to_db(stock_id, year, season, d)
#                print("{}/{}".format(r[0], r[1]))

            if target_season == 5:
                target_season = 4

            year_season = [[y, s] for y in range(start_year, start_year + 1) for s in range(start_season, 5)]
            year_season.extend([[y, s] for y in range(start_year + 1, target_year) for s in range(1, 5)])
            year_season.extend([[target_year, s] for s in range(1, target_season + 1)])

            stock_id = row[0]
            for r in year_season:
                year = r[0]
                season = r[1]
#                print(year, season)
                time.sleep(random.randint(min_wait_seconds, max_wait_seconds))
                d = balance_sheet_fetch_a_season(stock_id, year, season)
                # print(d)
                manager.insert_balance_sheet_to_db(stock_id, year, season, d)


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


def get_stock_no_need_update_data(year, season):
    sql_1 = "SELECT distinct stock_no FROM stock.statement_of_comprehensive_income;"

    sql_2 = "SELECT distinct stock_no FROM stock.statement_of_comprehensive_income where year = '{}' and season = '{}';"\
        .format(year, season)

    sql_3 = "SELECT distinct stock_no FROM stock.balance_sheet;"

    sql_4 = "SELECT distinct stock_no FROM stock.balance_sheet where year = '{}' and season = '{}';"\
        .format(year, season)

    data_1 = manager.select_query(sql_1)
    data_2 = manager.select_query(sql_2)
    data_3 = manager.select_query(sql_3)
    data_4 = manager.select_query(sql_4)

    s1 = set()
    s2 = set()
    s3 = set()
    s4 = set()

    for row in data_1:
        s1.add(row[0])

    for row in data_2:
        s2.add(row[0])

    for row in data_3:
        s3.add(row[0])

    for row in data_4:
        s4.add(row[0])

    s1.update(s3)

    need_remove_data = s2.intersection(s4)

    need_update_data = list(s1.difference(need_remove_data))

#    print(need_update_data)

    data = []

    twse_file = "twse_info_list.csv"
    with open(twse_file) as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, 1):
            if i == 1:
                continue
            if row[0] in need_update_data:
                data.append([row[0], row[1], row[2], row[3]])
    #            print (row[0], row[1], row[2], row[3])

    otc_file = "otc_info_list.csv"
    with open(otc_file) as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, 1):
            if i == 1:
                continue
            if row[0] in need_update_data:
                data.append([row[0], row[1], row[2], row[3]])

    return data


# 更新全部上市櫃資產負債和綜合損益財報
def update_all(year, season):
    need_update_data = get_stock_no_need_update_data(year, season)
    i = 0
    all_data = len(need_update_data)
    print("all_data = {}...".format(all_data))
    for row in need_update_data:
        i += 1
        print("{}/{}...".format(i, all_data))
        if "金融" not in row[3]:
            print("{}, {}, {}, {}".format(row[0], row[1], row[2], row[3]))
            stock_id = row[0]

            is_exist = is_income_statement_report_exist(stock_id, year, season)
            bs_exist = is_balance_sheet_report_exist(stock_id, year, season)

            if is_exist and bs_exist:
                print("pass...\n")
                continue

            # statement_of_comprehensive_income
            if not is_exist:
                d = income_statement_fetch_a_season(stock_id, year, season)
                manager.insert_income_statement_to_db(stock_id, year, season, d)

            if not bs_exist:
                d = balance_sheet_fetch_a_season(stock_id, year, season)
                manager.insert_balance_sheet_to_db(stock_id, year, season, d)

            time.sleep(random.randint(min_wait_seconds, max_wait_seconds))

            if season == 4 and not is_exist:
                d = income_statement_fetch_a_season(stock_id, year, 5)
                manager.insert_income_statement_to_db(stock_id, year, 5, d)
                time.sleep(random.randint(min_wait_seconds, max_wait_seconds))

        print("\n")


# 取得公開觀測站當天最新公布財報的公司代號
def get_newest_company_report_info():
    url = data_fetch.config.NEWEST_REPORT_INFO_URL
    header = data_fetch.config.HEADER
    match_company_set = set()
    try:
        html = requests.get(url, headers=header, timeout=data_fetch.config.TIMEOUT_SECONDS)
        soup = BeautifulSoup(html.content, "html.parser")
        buttons = soup.findAll("button")
        save_text = ""
        print('get data from {}'.format(url))
        print('data start...')
        for b in buttons:
            msg = b.find("u").text
            print(msg)
            save_text += msg.encode('utf8') + "\n"
            match_company_no = match_process(msg.encode('utf8'))
            if match_company_no:
                match_company_set.add(match_company_no)
        print('data end...')
        create_newest_company_report_info_temp(save_text, datetime.datetime.today().strftime('%Y-%m-%d'))

    except Exception as e:
        print("get_report_info error... ")
        print(e.args)

    return list(match_company_set)


# 將公開觀測站當天最新公布財報的公司代號存入temp
def create_newest_company_report_info_temp(data, file_name):
    target = "{}/{}.txt".format(data_fetch.config.NEWEST_REPORT_INFO_SAVE_PATH, file_name)
    with open(target, 'w') as the_file:
        the_file.write(data)
    print("{}.txt was built...".format(target))


# 字串處理，過濾字串
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
    match_word = "IFRSs"
    if match_word in msg_str:
        for tmp in match_str:
            if title == tmp:
                return company_no
    return None


if __name__ == "__main__":

    # print(get_newest_company_report_info())

    # update_all(2019, 2)
    # print(income_statement_fetch_a_season(2330, 2019, 2))
    # d = income_statement_fetch_a_season("2392", 2019, 3)
    # print(d)
    # manager.insert_income_statement_to_db("5225", 2017, 5, d)
    #
    # insert_all()

    # (1201, 2013, 4) error
    # 多次request 有機率被拒絕訪問一段時間(至少超過數十秒，若無等候此時間，則會不斷被拒絕訪問)
    # d = income_statement_fetch_a_season(1201, 2013, 4)
    # from database import mysql_manager
    # manager = mysql_manager.MysqlManager()
    # manager.insert_income_statement_to_db(1201, 2013, 4, d)

    # is_data = income_statement_fetch_a_season(2330, 106, 1)
    # manager.insert_income_statement_to_db(2330, 106, 1, is_data)
    #
    # bs_data = balance_sheet_fetch_a_season(1436, 107, 1)
    # manager.insert_balance_sheet_to_db(1436, 107, 1, bs_data)
    #
    # print(len(bs_data))
    # for k, v in bs_data.items():
    #     print(k, v)
    #
    # manager.insert_balance_sheet_to_db()

    pass

# 綜合損益 statement_of_comprehensive_income
"""
營業收入合計 OperatingRevenue
營業成本合計 OperatingCosts
營業毛利（毛損） GrossProfitLossFromOperations
未實現銷貨（損）益 UnrealizedProfitLossFromSales
已實現銷貨（損）益 RealizedProfitLossOnFromSales
營業毛利（毛損）淨額 GrossProfitLossFromOperationsNet
營業費用
　　推銷費用 SellingExpenses
　　管理費用 AdministrativeExpense
　　研究發展費用 ResearchAndDevelopmentExpenses
　營業費用合計 OperatingExpenses
其他收益及費損淨額
　其他收益及費損淨額 NetOtherIncomeExpenses
營業利益（損失）NetOperatingIncomeLoss
營業外收入及支出
　　其他收入 OtherIncomeOthers
　　其他利益及損失淨額 OtherGainsLosses
　　財務成本淨額 FinanceCosts
　　採用權益法認列之關聯企業及合資損益之份額淨額 ShareOfProfitLossOfAssociatesAndJointVenturesAccountedForUsingEquityMethod => Y1
　營業外收入及支出合計 NonoperatingIncomeAndExpenses
稅前淨利（淨損）ProfitLossBeforeTax
所得稅費用（利益）合計 IncomeTaxExpenseContinuingOperations
繼續營業單位本期淨利（淨損）ProfitLossFromContinuingOperations
本期淨利（淨損）ProfitLoss
後續可能重分類至損益之項目：
　　國外營運機構財務報表換算之兌換差額 OtherComprehensiveIncomeBeforeTaxExchangeDifferencesOnTranslation => Y3
　　備供出售金融資產未實現評價損益 OtherComprehensiveIncomeBeforeTaxAvailableforsaleFinancialAssets => Y4
　　採用權益法認列關聯企業及合資之其他綜合損益之份額-可能重分類至損益之項目(*採用權益法認列之關聯企業及合資之其他綜合損益之份額合計) ShareOfOtherComprehensiveIncomeOfAssociatesAndJointVenturesAccountedForUsingEquityMethod => Y2
　　與可能重分類之項目相關之所得稅(*與其他綜合損益組成部分相關之所得稅) IncomeTaxRelatingToComponentsOfOtherComprehensiveIncome
　其他綜合損益（淨額）OtherComprehensiveIncome
本期綜合損益總額 ComprehensiveIncome
　母公司業主（淨利／損）ProfitLossAttributableToOwnersOfParent
　非控制權益（淨利／損）ProfitLossAttributableToNoncontrollingInterests
　母公司業主（綜合損益）ComprehensiveIncomeAttributableToOwnersOfParent
　非控制權益（綜合損益）ComprehensiveIncomeAttributableToNoncontrollingInterests
基本每股盈餘
　基本每股盈餘(*eps) BasicEarningsLossPerShare
稀釋每股盈餘
　稀釋每股盈餘(*diluted_eps) DilutedEarningsLossPerShare
"""

# 資產負債 balance_sheet
"""
流動資產
    現金及約當現金 (現金及約當現金合計) CashAndCashEquivalents
    透過損益按公允價值衡量之金融資產-流動 CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss
    備供出售金融資產-流動淨額 CurrentAvailableForSaleFinancialAssets
    持有至到期日金融資產-流動淨額 CurrentHeldToMaturityFinancialAssets
   避險之衍生金融資產-流動
    應收帳款淨額 AccountsReceivableNet
    應收帳款-關係人淨額 AccountsReceivableDuefromRelatedPartiesNet
    其他應收款-關係人淨額 OtherReceivablesDueFromRelatedParties
    存貨 Inventories
    其他流動資產 OtherCurrentAssets
   流動資產合計 CurrentAssets
非流動資產
    持有至到期日金融資產-非流動淨額
    以成本衡量之金融資產-非流動淨額
    採用權益法之投資淨額 InvestmentAccountedForUsingEquityMethod
    不動產、廠房及設備 (不動產、廠房及設備合計) PropertyPlantAndEquipment
    無形資產 IntangibleAssets
   遞延所得稅資產 DeferredTaxAssets
    其他非流動資產 OtherNoncurrentAssets
    非流動資產合計 (非流動資產合計) NoncurrentAssets
資產總計 Assets
流動負債
    短期借款 (短期借款合計) ShorttermBorrowings
    透過損益按公允價值衡量之金融負債-流動 (透過損益按公允價值衡量之金融負債－流動合計) CurrentFinancialLiabilitiesAtFairValueThroughProfitOrLoss
    避險之衍生金融負債-流動 CurrentDerivativeFinancialLiabilitiesForHedging
    應付帳款 AccountsPayable
    應付帳款-關係人 (應付帳款－關係人合計) AccountsPayableToRelatedParties
    其他應付款 (其他應付款合計) OtherPayables
   本期所得稅負債 (當期所得稅負債) CurrentTaxLiabilities
    負債準備-流動 (負債準備－流動合計) CurrentProvisions
    其他流動負債 (其他流動負債合計) OtherCurrentLiabilities
    流動負債合計 CurrentLiabilities
非流動負債
    應付公司債 (應付公司債合計) BondsPayable
    長期借款 (長期借款合計) LongtermBorrowings
    遞延所得稅負債
    其他非流動負債 (其他非流動負債合計) OtherNoncurrentLiabilities
   非流動負債合計 NoncurrentLiabilities
負債總計 Liabilities
歸屬於母公司業主之權益
   股本
    普通股股本 OrdinaryShare
   股本合計 CapitalStock
資本公積
    資本公積-發行溢價 CapitalSurplusAdditionalPaidInCapital
    資本公積-認列對子公司所有權權益變動數 CapitalSurplusChangesInOwnershipInterestsInSubsidiaries
    資本公積-受贈資產 CapitalSurplusDonatedAssetsReceived
   資本公積-採用權益法認列關聯企業及合資股權淨值之變動數 CapitalSurplusChangesInEquityOfAssociatesAndJointVenturesAccountedForUsingEquityMethod => X2
    資本公積-合併溢額 CapitalSurplusNetAssetsFromMerger
   資本公積合計 CapitalSurplus
保留盈餘
    法定盈餘公積 LegalReserve
    未分配盈餘(或待彌補虧損) UnappropriatedRetainedEarningsAaccumulatedDeficit
   保留盈餘合計 RetainedEarnings
其他權益
    其他權益合計 OtherEquityInterest
歸屬於母公司業主之權益合計 EquityAttributableToOwnersOfParent
非控制權益 NoncontrollingInterests
權益總計 (權益總額	) Equity
負債及權益總計 
預收股款(權益項下)之約當發行股數(單位:股) EquivalentIssueSharesOfAdvanceReceiptsForOrdinaryShare
母公司暨子公司所持有之母公司庫藏股股數(單位:股) NumberOfSharesInEntityHeldByEntityAndByItsSubsidiaries
"""
