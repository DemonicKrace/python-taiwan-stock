# -*- coding: utf-8 -*-
"""
Created on 2019/10/29 14:57

@author: demonickrace
"""
import os

MAX_RETRY_SECONDS = 12
MIN_RETRY_SECONDS = 8

MAX_WAIT_SECONDS = 20
MIN_WAIT_SECONDS = 15

TIMEOUT_SECONDS = 20

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
    'Accept-Encoding': 'utf-8'
}

"""
directory path
"""
# 公開觀測站最新公開財報公司代號的暫存檔路徑
NEWEST_REPORT_INFO_SAVE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/../financial_statement_report/temp'

# 上市櫃月營收檔案暫存路徑
MONTH_REVENUE_SAVE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/month_revenue'


"""
url
"""
# 全部上市類證卷的收盤價
# https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=20191029&type=ALLBUT0999
TWSE_STOCK_BY_A_DAY_URL = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={}&type=ALLBUT0999'

# 全部上櫃類證卷的收盤價
# https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d=108/10/29&se=EW&_=1572338329081
OTC_STOCK_BY_A_DAY_URL = 'https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d={}&se=EW'

# 公開觀測站當天當下最新已公佈財報的公司列表資訊
NEWEST_REPORT_INFO_URL = 'https://mops.twse.com.tw/mops/web/t51sb10?Stp=R1'

# 上市公司月營收
# https://www.twse.com.tw/staticFiles/inspection/inspection/04/003/201909_C04003.zip
TWSE_MONTH_REVENUE_URL = 'https://www.twse.com.tw/staticFiles/inspection/inspection/04/003/{}'

# 上櫃公司月營收
# https://www.tpex.org.tw/storage/statistic/sales_revenue/O_201909.xls
OTC_MONTH_REVENUE_URL = 'https://www.tpex.org.tw/storage/statistic/sales_revenue/{}'

