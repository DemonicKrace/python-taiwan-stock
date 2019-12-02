# -*- coding: utf-8 -*-
"""
Created on 2017/3/14 19:25

@author: demonickrace
"""
import pymysql
import datetime
import config


class MysqlManager:
    def __init__(self, host="localhost", user="root", pw="root", db="stock"):
        self.host = config.DB_HOST
        self.user = config.DB_USER
        self.pw = config.DB_PWD
        self.db = config.DB_DEFAULT

    def sql_dml_query(self, sql_str):
        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            cursor = con.cursor()
            cursor.execute(sql_str)
            con.commit()
            print("sql '" + sql_str + "' run succeed")
        except Exception as e:
            msg = " sql_dml_query failed! ,error = {}\n".format(e.message)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
            return None
        finally:
            con.close()

    def select_query(self, sql_select, return_dict=False):
        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            if return_dict:
                cursor = con.cursor(pymysql.cursors.DictCursor)
            else:
                cursor = con.cursor()
            cursor.execute(sql_select)
            data = cursor.fetchall()
            con.commit()
            return data
        except Exception as e:
            msg = "select_query failed! ,error = {}\n".format(e.message)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
        finally:
            con.close()
        return None

    def select_market_open_date(self, start_dt="", end_dt="", table="market_open_date"):
        if start_dt == "":
            start_dt = "1992/01/01"
        if end_dt == "":
            end_dt = datetime.datetime.now().date()

        sql_select = "SELECT date FROM {} WHERE date >= '{}' AND date <= '{}';".format(table, start_dt, end_dt)

        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            cursor = con.cursor()
            cursor.execute(sql_select)
            data = cursor.fetchall()
            con.commit()
            return data
        except Exception as e:
            msg = " select_market_open_date failed! ,error = {}\n".format(e.message)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
            return None
        finally:
            con.close()

    def insert_stock_info(self, data=None, table="stock_info"):
        if data is None:
            data = []
        sql_insert = """INSERT INTO {}
                        (`stock_no`,
                        `company_name`,
                        `date`,
                        `business_type`,
                        `market_type`)
                        VALUES
                        (%s ,%s ,%s ,%s ,%s);""".format(table)
        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            cursor = con.cursor()
            cursor.execute("SET NAMES utf8")
            affected_count = cursor.executemany(sql_insert, data)
            con.commit()
            print("stock_info inserted {} rows".format(affected_count))
        except Exception as e:
            msg = " stock_info insert failed! ,error = {}\n".format(e.message)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
        finally:
            con.close()

    def insert_stock(self, stock_no, rows, table="stock"):

        data = []

        if len(rows) == 0:
            return

        last_row = []
        try:
            for i, row in enumerate(rows, 1):

                # 確保日期格式正確，ex:"100/01/01 * " => "100/01/01"
                # row[0] = row[0][0:9]

                date = row[0].split("/")
                if int(date[0]) < 1900 and len(date) == 3:
                    # 將民國轉成西元
                    row[0] = "{}/{}/{}".format(str(int(date[0]) + 1911), date[1], date[2])

                temp_row = []

                # 處理數字的逗號與正號，"+1,000.01" => "1000.01"
                row_format = []
                for r in row:
                    r = r.replace(",", "").replace("+", "").replace("＊", "")
                    row_format.append(r)

                row = row_format

                # 檢查成交量是否為0，若為0，則此筆資料全部轉為0
                if int(row[1]) == 0:
                    temp_row.extend([stock_no, row[0], 0, 0, 0, 0, 0, 0, 0, 0])
                else:
                    temp_row.append(stock_no)
                    temp_row.extend([r for r in row if r])
                data.append(temp_row)
                last_row = row
        except Exception as e:
            print("last_row = {}".format(last_row))
            print("error row = {}".format(row))
            msg = " stock_no:{} , last_row = {} ,format error = '{}'\n\n".format(stock_no, last_row, e.message)
            print(msg)
            self.write_error_log(msg)

        # self.show_data(data)
        #        return
        #        self.show_data(data)

        sql_insert = """INSERT INTO {}
                                (stock_no,
                                 date,
                                 shares,
                                 turnover,
                                 open,
                                 high,
                                 low,
                                 close,
                                 bid_ask_spread,
                                 deal)
                                 VALUES
                                 ( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s );""".format(table)
        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            cursor = con.cursor()
            affected_count = cursor.executemany(sql_insert, data)
            con.commit()
            print("stock_no:{} inserted {} rows".format(stock_no, affected_count))
        # except pymysql.IntegrityError as e:
        except Exception as e:
            msg = " stock_no:{} insert failed! ,error = {}\n".format(stock_no, e.args)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
        finally:
            con.close()

    def insert_all_stock_price_by_a_day(self, date, rows, table="stock"):
        sql_insert = """INSERT INTO {}
                        (stock_no,
                         date,
                         shares,
                         turnover,
                         open,
                         high,
                         low,
                         close,
                         bid_ask_spread,
                         deal)
                         VALUES
                         ( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s );""".format(table)
        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            cursor = con.cursor()
            affected_count = cursor.executemany(sql_insert, rows)
            con.commit()
            print("target date:{} inserted {} rows".format(date, affected_count))
        except Exception as e:
            msg = "target date:{} insert failed! ,error = {}\n".format(date, e.args)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
        finally:
            con.close()

    def insert_rows(self, columns=None, rows=None, table=None):
        affected_count = 0
        con = self.get_connection_obj()
        if not con:
            return affected_count
        try:
            columns_str = ', '.join(columns)
            values_str = ', '.join(['%s' for i in columns])
            sql_insert = "INSERT INTO {} ({}) VALUES ({});".format(table, columns_str, values_str)
            cursor = con.cursor()
            affected_count = cursor.executemany(sql_insert, rows)
            con.commit()
            print("table:{} inserted {} rows".format(table, affected_count))
        except Exception as e:
            msg = "table:{} insert failed! ,error = {}\n".format(table, e.args)
            print(msg)
            self.write_error_log(msg)
        finally:
            con.close()
        return affected_count

    def get_connection_obj(self):
        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
            return con
        except Exception as e:
            print("database connect fail..., msg={}".format(e.args))
            return None

    @staticmethod
    def write_error_log(msg):
        from data_fetch.log import Log
        log = Log()
        log.write_db_err_log(msg)

    # 檢查與測試資料
    @staticmethod
    def show_data(data):
        if data is None:
            print ("data is empty!")
            return
        print("----------")
        for i, row in enumerate(data, 1):
            print(i, row)
        print("----------")


if __name__ == '__main__':

    pass
