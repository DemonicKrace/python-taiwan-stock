# -*- coding: utf-8 -*-
"""
Created on 2017/3/13 00:25

@author: demonickrace
"""
import csv


def test():
    twse_file = "twse_info_list.csv"

    with open(twse_file) as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            print (row[0], row[1])

    otc_file = "otc_info_list.csv"

    with open(otc_file) as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            print (row[0],row[1])


# 創建csv
def create_csv(data, file_name):
    with open(file_name, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows([row for row in data if row])
