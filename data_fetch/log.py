# -*- coding: utf-8 -*-
"""
Created on 2017/3/23 12:45

@author: demonickrace
"""
import os
import datetime


class Log:
    def __init__(self, path="/../"):
        # 專案根目錄
        self.path = os.path.dirname(os.path.abspath(__file__)) + path

    def write_db_err_log(self, msg, filename="/database/db_err_log.txt"):
        self.write_log(msg, filename)

    def write_fetch_err_log(self, msg, filename="/data_fetch/fetch_err_log.txt"):
        self.write_log(msg, filename)

    def write_report_log(self, msg, report_name):
        filename = "/analysis_report/{}_log.txt".format(report_name)
        self.write_log(msg, filename)

    def write_log(self, msg, filename):
        path = self.path + filename
        d = datetime.datetime.now()
        with open(path, "a") as f:
            f.write("{}, {}\n".format(d, msg))
