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
            msg = " select_query failed! ,error = {}\n".format(e.message)
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

    def select_all_warrant_no(self, twse=False, otc=False):
        if twse and otc:
            print("twse 和 otc 不可同時為 True")

        if not twse and not otc:
            print("twse 和 otc 不可同時為 False")

        if twse:
            type = "twse"
        elif otc:
            type = "otc"

        # 若資料量過大，可分批處理
        # count = 10000 start_no = 0 sql_select = "SELECT distinct warrant_no FROM warrant where {} = '1' limit {},
        # {};".format(type, start_no, count)

        sql_select = "SELECT distinct warrant_no FROM warrant where {} = '1';".format(type)

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
            msg = " select_all_warrant_no failed! ,error = {}\n".format(e.message)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
            return None
        finally:
            con.close()

    def insert_warrant_info(self, rows, table="warrant_info"):

        if len(rows) == 0:
            print("{} , insert_warrant_info, there is no data!".format(datetime.datetime.now()))
            return

        sql_insert = """INSERT INTO {}
                        (`warrant_no`,
                        `type`,
                        `company_name`,
                        `company_abbr`,
                        `en_abbr`,
                        `open_date`,
                        `final_date`,
                        `finish_date`,
                        `exercise_open_date`,
                        `exercise_finish_date`,
                        `circulation`,
                        `add_circulation`,
                        `target_no`,
                        `target_name`,
                        `twse`,
                        `otc`)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""".format(table)
        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            cursor = con.cursor()
            cursor.execute("SET NAMES utf8")
            affected_count = cursor.executemany(sql_insert, rows)
            con.commit()
            print("warrant_info inserted {} rows".format(affected_count))
            print("\n")
        # except pymysql.IntegrityError as e:
        except Exception as e:
            msg = " warrant info insert failed! ,error = {}\n".format(e.message)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
        finally:
            con.close()

    def insert_warrant(self, date, rows, table="warrant"):

        if len(rows) == 0:
            print("{} , date:{} is no data!".format(datetime.datetime.now(), date))
            return

        sql_insert = """INSERT INTO {}
                                    (`warrant_no`,
                                    `date`,
                                    `shares`,
                                    `turnover`,
                                    `open`,
                                    `high`,
                                    `low`,
                                    `close`,
                                    `bid_ask_spread`,
                                    `deal`,
                                    `twse`,
                                    `otc`)
                                    VALUES
                                    ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""".format(table)
        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            cursor = con.cursor()
            affected_count = cursor.executemany(sql_insert, rows)
            con.commit()
            print("date:{} warrant inserted {} rows".format(date, affected_count))
        # except pymysql.IntegrityError as e:
        except Exception as e:
            msg = " date:{} warrant insert failed! ,error = {}\n".format(date, e.message)
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

    def insert_income_statement_to_db(self, stock_no, year, season, data, table="statement_of_comprehensive_income"):
        if data is None:
            err_msg = "insert_income_statement_to_db error:  stock_no = {}, year = {}, season = {}, input data is None!"\
                .format(stock_no, year, season)
            print(err_msg)
            self.write_error_log(err_msg)
            return
        if data.get('stock_no', None) is None or data.get('year', None) is None or data.get('season', None) is None:
            print("insert_income_statement_to_db error: 'stock_no or year or season is None!'")
            err_msg = "insert_income_statement_to_db error:  stock_no = {}, year = {}, season = {}, " \
                      "stock_no or year or season is None!".format(stock_no, year, season)
            print(err_msg)
            self.write_error_log(err_msg)
            return

        # cols names
        cols = [
                'stock_no',
                'year',
                'season',
                'OperatingRevenue',
                'OperatingRevenue_p',
                'OperatingCosts',
                'OperatingCosts_p',
                'GrossProfitLossFromOperations',
                'GrossProfitLossFromOperations_p',
                'UnrealizedProfitLossFromSales',
                'UnrealizedProfitLossFromSales_p',
                'RealizedProfitLossOnFromSales',
                'RealizedProfitLossOnFromSales_p',
                'GrossProfitLossFromOperationsNet',
                'GrossProfitLossFromOperationsNet_p',
                'SellingExpenses',
                'SellingExpenses_p',
                'AdministrativeExpense',
                'AdministrativeExpense_p',
                'ResearchAndDevelopmentExpenses',
                'ResearchAndDevelopmentExpenses_p',
                'OperatingExpenses',
                'OperatingExpenses_p',
                'NetOtherIncomeExpenses',
                'NetOtherIncomeExpenses_p',
                'NetOperatingIncomeLoss',
                'NetOperatingIncomeLoss_p',
                'OtherIncomeOthers',
                'OtherIncomeOthers_p',
                'OtherRevenue',
                'OtherRevenue_p',
                'ForeignExchangeGains',
                'ForeignExchangeGains_p',
                'OtherGainsLosses',
                'OtherGainsLosses_p',
                'FinanceCosts',
                'FinanceCosts_p',
                'Y1',
                'Y1_p',
                'NonoperatingIncomeAndExpenses',
                'NonoperatingIncomeAndExpenses_p',
                'ProfitLossBeforeTax',
                'ProfitLossBeforeTax_p',
                'IncomeTaxExpenseContinuingOperations',
                'IncomeTaxExpenseContinuingOperations_p',
                'ProfitLossFromContinuingOperations',
                'ProfitLossFromContinuingOperations_p',
                'ProfitLoss',
                'ProfitLoss_p',
                'Y3',
                'Y3_p',
                'Y4',
                'Y4_p',
                'Y2',
                'Y2_p',
                'IncomeTaxRelatingToComponentsOfOtherComprehensiveIncome',
                'IncomeTaxRelatingToComponentsOfOtherComprehensiveIncome_p',
                'OtherComprehensiveIncome',
                'OtherComprehensiveIncome_p',
                'ComprehensiveIncome',
                'ComprehensiveIncome_p',
                'ProfitLossAttributableToOwnersOfParent',
                'ProfitLossAttributableToOwnersOfParent_p',
                'ProfitLossAttributableToNoncontrollingInterests',
                'ProfitLossAttributableToNoncontrollingInterests_p',
                'ComprehensiveIncomeAttributableToOwnersOfParent',
                'ComprehensiveIncomeAttributableToOwnersOfParent_p',
                'ComprehensiveIncomeAttributableToNoncontrollingInterests',
                'ComprehensiveIncomeAttributableToNoncontrollingInterests_p',
                'BasicEarningsLossPerShare',
                'DilutedEarningsLossPerShare']

        col_list = []
        value_list = []
        for col in cols:
            v = data.get(col, None)
            if(v is not None):
                col_list.append(col)
                value_list.append(str(v))
#                print(col, v)

        col_str = ""
        value_str = ""
        for i in range(0, len(col_list)):
#            print(col_list[i], value_list[i])
            if i < len(col_list) - 1:
                col_str += "`" + col_list[i] + "`, "
                value_str += "'" + value_list[i] + "', "
            else:
                col_str += "`" + col_list[i] + "`"
                value_str += "'" + value_list[i] + "'"

        col_str = "(" + col_str + ")"
        value_str = "(" + value_str + ")"

 #       print(col_str)
 #       print(value_str)

        sql_insert = "INSERT INTO {} {} VALUES {};".format(table, col_str, value_str)
        # print(sql_insert)

        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            cursor = con.cursor()
            affected_count = cursor.execute(sql_insert)
            con.commit()
            print("statement_of_comprehensive_income, stock_no:{}, year:{}, season:{} inserted {} row"
                  .format(data['stock_no'], data['year'], data['season'], affected_count))
        # except pymysql.IntegrityError as e:
        except Exception as e:
            msg = "statement_of_comprehensive_income, stock_no:{}, year:{}, season:{} ,insert failed! ,error = {}\n"\
                .format(data['stock_no'], data['year'], data['season'], e.args)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
        finally:
            con.close()

    def insert_balance_sheet_to_db(self, stock_no, year, season, data, table="balance_sheet"):
        if data is None:
            err_msg = "insert_balance_sheet_to_db error:  stock_no = {}, year = {}, season = {}, input data is None!"\
                .format(stock_no, year, season)
            print(err_msg)
            self.write_error_log(err_msg)
            return
        if data.get('stock_no', None) is None or data.get('year', None) is None or data.get('season', None) is None:
            print("insert_balance_sheet_to_db error: 'stock_no or year or season is None!'")
            err_msg = "insert_balance_sheet_to_db error:  stock_no = {}, year = {}, season = {}, " \
                      "stock_no or year or season is None!".format(stock_no, year, season)
            print(err_msg)
            self.write_error_log(err_msg)
            return

        # cols names
        cols = [
              'stock_no',
              'year',
              'season',
              'CashAndCashEquivalents',
              'CashAndCashEquivalents_p',
              'CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss',
              'CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss_p',
              'CurrentAvailableForSaleFinancialAssets',
              'CurrentAvailableForSaleFinancialAssets_p',
              'CurrentHeldToMaturityFinancialAssets',
              'CurrentHeldToMaturityFinancialAssets_p',
              'AccountsReceivableNet',
              'AccountsReceivableNet_p',
              'AccountsReceivableDuefromRelatedPartiesNet',
              'AccountsReceivableDuefromRelatedPartiesNet_p',
              'OtherReceivablesDueFromRelatedParties',
              'OtherReceivablesDueFromRelatedParties_p',
            #  'InventoriesManufacturingBusiness',
            #  'InventoriesManufacturingBusiness_p',
              'Inventories',
              'Inventories_p',
            #  'OtherCurrentFinancialAssets',
            #  'OtherCurrentFinancialAssets_p',
            #  'OtherCurrentAssetsOthers',
            #  'OtherCurrentAssetsOthers_p',
              'OtherCurrentAssets',
              'OtherCurrentAssets_p',
              'CurrentAssets',
              'CurrentAssets_p',
            #  'NoncurrentAvailableForSaleFinancialAssets',
            #  'NoncurrentAvailableForSaleFinancialAssets_p',
            #  'NoncurrentFinancialAssetsAtCost',
            #  'NoncurrentFinancialAssetsAtCost_p',
              'InvestmentAccountedForUsingEquityMethod',
              'InvestmentAccountedForUsingEquityMethod_p',
              'PropertyPlantAndEquipment',
              'PropertyPlantAndEquipment_p',
              'IntangibleAssets',
              'IntangibleAssets_p',
              'DeferredTaxAssets',
              'DeferredTaxAssets_p',
            #  'GuaranteeDepositsPaid',
            #  'GuaranteeDepositsPaid_p',
            #  'OtherNoncurrentAssetsOthers',
            #  'OtherNoncurrentAssetsOthers_p',
              'OtherNoncurrentAssets',
              'OtherNoncurrentAssets_p',
              'NoncurrentAssets',
              'NoncurrentAssets_p',
            #  'Assets',
            #  'Assets_p',
              'ShorttermBorrowings',
              'ShorttermBorrowings_p',
              'CurrentFinancialLiabilitiesAtFairValueThroughProfitOrLoss',
              'CurrentFinancialLiabilitiesAtFairValueThroughProfitOrLoss_p',
              'CurrentDerivativeFinancialLiabilitiesForHedging',
              'CurrentDerivativeFinancialLiabilitiesForHedging_p',
              'AccountsPayable',
              'AccountsPayable_p',
              'AccountsPayableToRelatedParties',
              'AccountsPayableToRelatedParties_p',
            #  'WagesAndSalariesPayable',
            #  'WagesAndSalariesPayable_p',
            #  'EmployeeBonusPayable',
            #  'EmployeeBonusPayable_p',
            #  'CompensationDueToDirectorsAndSupervisors',
            #  'CompensationDueToDirectorsAndSupervisors_p',
            #  'PayableOnMachineryAndEquipment',
            #  'PayableOnMachineryAndEquipment_p',
              'OtherPayables',
              'OtherPayables_p',
              'CurrentTaxLiabilities',
              'CurrentTaxLiabilities_p',
              'CurrentProvisions',
              'CurrentProvisions_p',
            #  'OtherCurrentLiabilitiesOthers',
            #  'OtherCurrentLiabilitiesOthers_p',
              'OtherCurrentLiabilities',
              'OtherCurrentLiabilities_p',
              'CurrentLiabilities',
              'CurrentLiabilities_p',
            #  'NoncurrentDerivativeFinancialLiabilitiesForHedging',
            #  'NoncurrentDerivativeFinancialLiabilitiesForHedging_p',
              'BondsPayable',
              'BondsPayable_p',
            #  'LongtermBankLoans',
            #  'LongtermBankLoans_p',
              'LongtermBorrowings',
              'LongtermBorrowings_p',
            #  'NoncurrentLeaseObligationsPayable',
            #  'NoncurrentLeaseObligationsPayable_p',
            #  'LongtermNotesAndAccountsPayable',
            #  'LongtermNotesAndAccountsPayable_p',
            #  'AccruedPensionLiabilities',
            #  'AccruedPensionLiabilities_p',
            #  'OtherNoncurrentLiabilitiesOthers',
            #  'OtherNoncurrentLiabilitiesOthers_p',
              'OtherNoncurrentLiabilities',
              'OtherNoncurrentLiabilities_p',
              'NoncurrentLiabilities',
              'NoncurrentLiabilities_p',
              'Liabilities',
              'Liabilities_p',
              'OrdinaryShare',
              'OrdinaryShare_p',
              'CapitalStock',
              'CapitalStock_p',
            #  'CapitalSurplusAdditionalPaidInCapitalArisingFromOrdinaryShare',
            #  'CapitalSurplusAdditionalPaidInCapitalArisingFromOrdinaryShare_p',
            #  'CapitalSurplusAdditionalPaidInCapitalArisingFromBondConversion',
            #  'CapitalSurplusAdditionalPaidInCapitalArisingFromBondConversion_p',
              'CapitalSurplusAdditionalPaidInCapital',
              'CapitalSurplusAdditionalPaidInCapital_p',
            #  'X1',
            #  'X1_p',
              'CapitalSurplusChangesInOwnershipInterestsInSubsidiaries',
              'CapitalSurplusChangesInOwnershipInterestsInSubsidiaries_p',
            # 'CapitalSurplusOtherDonatedAssetsReceived',
            #  'CapitalSurplusOtherDonatedAssetsReceived_p',
              'CapitalSurplusDonatedAssetsReceived',
              'CapitalSurplusDonatedAssetsReceived_p',
              'X2',
              'X2_p',
              'CapitalSurplusNetAssetsFromMerger',
              'CapitalSurplusNetAssetsFromMerger_p',
              'CapitalSurplus',
              'CapitalSurplus_p',
              'LegalReserve',
              'LegalReserve_p',
            #  'SpecialReserve',
            #  'SpecialReserve_p',
              'UnappropriatedRetainedEarningsAaccumulatedDeficit',
              'UnappropriatedRetainedEarningsAaccumulatedDeficit_p',
              'RetainedEarnings',
              'RetainedEarnings_p',
              'OtherEquityInterest',
              'OtherEquityInterest_p',
              'EquityAttributableToOwnersOfParent',
              'EquityAttributableToOwnersOfParent_p',
              'NoncontrollingInterests',
              'NoncontrollingInterests_p',
              'Equity',
              'Equity_p',
            #  'NumberOfShareCapitalAwaitingRetirement',
            #  'NumberOfShareCapitalAwaitingRetirement_p',
              'EquivalentIssueSharesOfAdvanceReceiptsForOrdinaryShare',
            #  'EquivalentIssueSharesOfAdvanceReceiptsForOrdinaryShare_p',
              'NumberOfSharesInEntityHeldByEntityAndByItsSubsidiaries',
            #  'NumberOfSharesInEntityHeldByEntityAndByItsSubsidiaries_p',
                ]

        col_list = []
        value_list = []
        for col in cols:
            v = data.get(col, None)
            if (v is not None):
                col_list.append(col)
                value_list.append(str(v))
#                print(col, v)

        col_str = ""
        value_str = ""
        for i in range(0, len(col_list)):
            #            print(col_list[i], value_list[i])
            if i < len(col_list) - 1:
                col_str += "`" + col_list[i] + "`, "
                value_str += "'" + value_list[i] + "', "
            else:
                col_str += "`" + col_list[i] + "`"
                value_str += "'" + value_list[i] + "'"

        col_str = "(" + col_str + ")"
        value_str = "(" + value_str + ")"

        #       print(col_str)
        #       print(value_str)

        sql_insert = "INSERT INTO {} {} VALUES {};".format(table, col_str, value_str)
        # print(sql_insert)

        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            cursor = con.cursor()
            affected_count = cursor.execute(sql_insert)
            con.commit()
            print("balance_sheet, stock_no:{}, year:{}, season:{} inserted {} row"
                  .format(data['stock_no'], data['year'], data['season'], affected_count))
        # except pymysql.IntegrityError as e:
        except Exception as e:
            msg = "balance_sheet, stock_no:{}, year:{}, season:{} ,insert failed! ,error = {}\n" \
                .format(data['stock_no'], data['year'], data['season'], e.args)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
        finally:
            con.close()

    def insert_month_revenue_to_db(self, date, data=None, table="month_revenue"):
        if data is None:
            data = []
        sql_insert = """INSERT INTO {}
                                (stock_no,
                                 date,
                                 net_sales,
                                 pre_year_net_sales,
                                 increased_amount,
                                 increased_amount_percent,
                                 accumulated_amount,
                                 pre_year_accumulated_amount,
                                 accumulated_increased_amount,
                                 accumulated_increased_amount_percent,
                                 note)
                                 VALUES
                                 ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""".format(table)
        try:
            con = pymysql.connect(self.host, self.user, self.pw, self.db)
        except Exception as e:
            print("database connect fail, error={}".format(e.message))
            return None
        try:
            cursor = con.cursor()
            affected_count = cursor.executemany(sql_insert, data)
            con.commit()
            print("target date:{}, month_revenue inserted {} rows".format(date, affected_count))
        except Exception as e:
            msg = "target date:{}, month_revenue insert failed! ,error = {}\n".format(date, e.args)
            print(msg)
            self.write_error_log(msg)
            con.rollback()
        finally:
            con.close()

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
