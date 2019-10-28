# -*- coding: utf-8 -*-
"""
Created on 2017/3/21 20:29

@author: demonickrace
"""

import datetime


def fetch_all_warrant_to_db(twse=False, otc=False):
    from database import mysql_manager
    from data_fetch.warrant_fetch import twse_warrant_fetch
    from data_fetch.warrant_fetch import otc_warrant_fetch

    mysql_manager = mysql_manager.MysqlManager()

    start_dt = datetime.datetime.now()
    # otc自民國96年7月起開始提供
    # twse自民國93年2月11日起提供
    # 從民國97年1月1號開始收集 = 西元2008/01/01
    start_date = datetime.date(2008, 1, 1)
    end_date = datetime.date.today()
    day = datetime.timedelta(days=1)

    while start_date <= end_date:
        date = start_date.strftime('%Y/%m/%d')
        data = None

        # 擷取當日otc全部權證資料
        if twse:
            print("twse warrant , date:{} start loading".format(date))
            data = twse_warrant_fetch(date)
        elif otc:
            print("otc warrant , date:{} start loading".format(date))
            data = otc_warrant_fetch(date)

        if data is not None:
            # 匯入至資料庫
            mysql_manager.insert_warrant(date, data)

        start_date = start_date + day

    end_dt = datetime.datetime.now()

    dif = end_dt - start_dt

    print ("started at ", start_dt)
    print ("finished at ", end_dt)
    print ("all time = ", dif)


if __name__ == "__main__":
    # fetch_all_warrant_to_db(twse=True)
    # fetch_all_warrant_to_db(otc=True)

    print("finish!")

