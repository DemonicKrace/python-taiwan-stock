# -*- coding: utf-8 -*-
"""
Created on 2017/3/14 19:25

@author: demonickrace
"""
import pymysql
import datetime
import database.config


class MysqlManager:
    def __init__(self):
        self.host = database.config.DB_HOST
        self.user = database.config.DB_USER
        self.pw = database.config.DB_PWD
        self.db = database.config.DB_DEFAULT
        self.port = database.config.DB_PORT

    def sql_dml_query(self, sql_str):
        result = False
        con = self.get_connection_obj()
        if con:
            try:
                cursor = con.cursor()
                cursor.execute(sql_str)
                con.commit()
                print("sql '" + sql_str + "' run succeed")
                result = True
            except Exception as e:
                msg = " sql_dml_query failed! ,error = {}\n".format(e.message)
                print(msg)
                self.write_error_log(msg)
            finally:
                con.close()
        return result

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
            print("table:'{}' inserted {} rows".format(table, affected_count))
        except Exception as e:
            msg = "table:'{}' insert failed! ,error = {}\n".format(table, e.args)
            print(msg)
            self.write_error_log(msg)
        finally:
            con.close()
        return affected_count

    def get_connection_obj(self):
        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db, self.port)
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
