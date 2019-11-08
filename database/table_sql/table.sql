-- stock
CREATE TABLE `stock` (
  `stock_no` char(10) NOT NULL COMMENT '公司股票代號',
  `date` date NOT NULL COMMENT '日期',
  `shares` bigint(20) NOT NULL COMMENT '成交股數',
  `turnover` bigint(20) NOT NULL COMMENT '成交金額',
  `open` float NOT NULL COMMENT '開盤價',
  `high` float NOT NULL COMMENT '最高價',
  `low` float NOT NULL COMMENT '最低價',
  `close` float NOT NULL COMMENT '收盤價',
  `bid_ask_spread` varchar(10) NOT NULL COMMENT 'Ex-dividend date (價差)',
  `deal` int(11) NOT NULL COMMENT '成交筆數',
  PRIMARY KEY (`stock_no`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='股價表';



-- stock_info
CREATE TABLE `stock_info` (
  `stock_no` char(10) NOT NULL COMMENT '公司股票代號',
  `company_name` varchar(30) NOT NULL COMMENT '公司名稱',
  `date` date NOT NULL COMMENT '上市櫃日期',
  `business_type` varchar(20) NOT NULL COMMENT '主業類型',
  `market_type` varchar(20) DEFAULT NULL COMMENT '上市櫃類型',
  PRIMARY KEY (`stock_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='證卷之公司資訊';


-- warrant
CREATE TABLE `warrant` (
  `warrant_no` char(10) NOT NULL,
  `date` date NOT NULL,
  `shares` int(11) NOT NULL,
  `turnover` int(11) NOT NULL,
  `open` float NOT NULL,
  `high` float NOT NULL,
  `low` float NOT NULL,
  `close` float NOT NULL,
  `bid_ask_spread` float NOT NULL,
  `deal` int(11) NOT NULL,
  `twse` int(11) NOT NULL DEFAULT '0',
  `otc` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`warrant_no`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- warrant_info
CREATE TABLE `warrant_info` (
  `warrant_no` char(10) NOT NULL,
  `type` char(5) NOT NULL,
  `company_name` varchar(30) NOT NULL,
  `company_abbr` varchar(30) NOT NULL,
  `en_abbr` char(30) NOT NULL,
  `open_date` date NOT NULL,
  `final_date` date NOT NULL,
  `finish_date` date NOT NULL,
  `exercise_open_date` date NOT NULL,
  `exercise_finish_date` date NOT NULL,
  `circulation` int(11) NOT NULL,
  `add_circulation` int(11) NOT NULL,
  `target_no` char(30) NOT NULL,
  `target_name` varchar(30) NOT NULL,
  `twse` int(11) NOT NULL DEFAULT '0',
  `otc` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`warrant_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Balance Sheet
CREATE TABLE `balance_sheet` (
  `stock_no` char(10) NOT NULL,
  `year` int(11) NOT NULL,
  `season` int(11) NOT NULL,
  `CashAndCashEquivalents` int(11) DEFAULT NULL,
  `CashAndCashEquivalents_p` float DEFAULT NULL,
  `CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss` int(11) DEFAULT NULL,
  `CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss_p` float DEFAULT NULL,
  `CurrentAvailableForSaleFinancialAssets` int(11) DEFAULT NULL,
  `CurrentAvailableForSaleFinancialAssets_p` float DEFAULT NULL,
  `CurrentHeldToMaturityFinancialAssets` int(11) DEFAULT NULL,
  `CurrentHeldToMaturityFinancialAssets_p` float DEFAULT NULL,
  `AccountsReceivableNet` int(11) DEFAULT NULL,
  `AccountsReceivableNet_p` float DEFAULT NULL,
  `AccountsReceivableDuefromRelatedPartiesNet` int(11) DEFAULT NULL,
  `AccountsReceivableDuefromRelatedPartiesNet_p` float DEFAULT NULL,
  `OtherReceivablesDueFromRelatedParties` int(11) DEFAULT NULL,
  `OtherReceivablesDueFromRelatedParties_p` float DEFAULT NULL,
  `InventoriesManufacturingBusiness` int(11) DEFAULT NULL,
  `InventoriesManufacturingBusiness_p` float DEFAULT NULL,
  `Inventories` int(11) DEFAULT NULL,
  `Inventories_p` float DEFAULT NULL,
  `OtherCurrentFinancialAssets` int(11) DEFAULT NULL,
  `OtherCurrentFinancialAssets_p` float DEFAULT NULL,
  `OtherCurrentAssetsOthers` int(11) DEFAULT NULL,
  `OtherCurrentAssetsOthers_p` float DEFAULT NULL,
  `OtherCurrentAssets` int(11) DEFAULT NULL,
  `OtherCurrentAssets_p` float DEFAULT NULL,
  `CurrentAssets` int(11) DEFAULT NULL,
  `CurrentAssets_p` float DEFAULT NULL,
  `NoncurrentAvailableForSaleFinancialAssets` int(11) DEFAULT NULL,
  `NoncurrentAvailableForSaleFinancialAssets_p` float DEFAULT NULL,
  `NoncurrentFinancialAssetsAtCost` int(11) DEFAULT NULL,
  `NoncurrentFinancialAssetsAtCost_p` float DEFAULT NULL,
  `InvestmentAccountedForUsingEquityMethod` int(11) DEFAULT NULL,
  `InvestmentAccountedForUsingEquityMethod_p` float DEFAULT NULL,
  `PropertyPlantAndEquipment` int(11) DEFAULT NULL,
  `PropertyPlantAndEquipment_p` float DEFAULT NULL,
  `IntangibleAssets` int(11) DEFAULT NULL,
  `IntangibleAssets_p` float DEFAULT NULL,
  `DeferredTaxAssets` int(11) DEFAULT NULL,
  `DeferredTaxAssets_p` float DEFAULT NULL,
  `GuaranteeDepositsPaid` int(11) DEFAULT NULL,
  `GuaranteeDepositsPaid_p` float DEFAULT NULL,
  `OtherNoncurrentAssetsOthers` int(11) DEFAULT NULL,
  `OtherNoncurrentAssetsOthers_p` float DEFAULT NULL,
  `OtherNoncurrentAssets` int(11) DEFAULT NULL,
  `OtherNoncurrentAssets_p` float DEFAULT NULL,
  `NoncurrentAssets` int(11) DEFAULT NULL,
  `NoncurrentAssets_p` float DEFAULT NULL,
  `Assets` int(11) DEFAULT NULL,
  `Assets_p` float DEFAULT NULL,
  `ShorttermBorrowings` int(11) DEFAULT NULL,
  `ShorttermBorrowings_p` float DEFAULT NULL,
  `CurrentFinancialLiabilitiesAtFairValueThroughProfitOrLoss` int(11) DEFAULT NULL,
  `CurrentFinancialLiabilitiesAtFairValueThroughProfitOrLoss_p` float DEFAULT NULL,
  `CurrentDerivativeFinancialLiabilitiesForHedging` int(11) DEFAULT NULL,
  `CurrentDerivativeFinancialLiabilitiesForHedging_p` float DEFAULT NULL,
  `AccountsPayable` int(11) DEFAULT NULL,
  `AccountsPayable_p` float DEFAULT NULL,
  `AccountsPayableToRelatedParties` int(11) DEFAULT NULL,
  `AccountsPayableToRelatedParties_p` float DEFAULT NULL,
  `WagesAndSalariesPayable` int(11) DEFAULT NULL,
  `WagesAndSalariesPayable_p` float DEFAULT NULL,
  `EmployeeBonusPayable` int(11) DEFAULT NULL,
  `EmployeeBonusPayable_p` float DEFAULT NULL,
  `CompensationDueToDirectorsAndSupervisors` int(11) DEFAULT NULL,
  `CompensationDueToDirectorsAndSupervisors_p` float DEFAULT NULL,
  `PayableOnMachineryAndEquipment` int(11) DEFAULT NULL,
  `PayableOnMachineryAndEquipment_p` float DEFAULT NULL,
  `OtherPayables` int(11) DEFAULT NULL,
  `OtherPayables_p` float DEFAULT NULL,
  `CurrentTaxLiabilities` int(11) DEFAULT NULL,
  `CurrentTaxLiabilities_p` float DEFAULT NULL,
  `CurrentProvisions` int(11) DEFAULT NULL,
  `CurrentProvisions_p` float DEFAULT NULL,
  `OtherCurrentLiabilitiesOthers` int(11) DEFAULT NULL,
  `OtherCurrentLiabilitiesOthers_p` float DEFAULT NULL,
  `OtherCurrentLiabilities` int(11) DEFAULT NULL,
  `OtherCurrentLiabilities_p` float DEFAULT NULL,
  `CurrentLiabilities` int(11) DEFAULT NULL,
  `CurrentLiabilities_p` float DEFAULT NULL,
  `NoncurrentDerivativeFinancialLiabilitiesForHedging` int(11) DEFAULT NULL,
  `NoncurrentDerivativeFinancialLiabilitiesForHedging_p` float DEFAULT NULL,
  `BondsPayable` int(11) DEFAULT NULL,
  `BondsPayable_p` float DEFAULT NULL,
  `LongtermBankLoans` int(11) DEFAULT NULL,
  `LongtermBankLoans_p` float DEFAULT NULL,
  `LongtermBorrowings` int(11) DEFAULT NULL,
  `LongtermBorrowings_p` float DEFAULT NULL,
  `NoncurrentLeaseObligationsPayable` int(11) DEFAULT NULL,
  `NoncurrentLeaseObligationsPayable_p` float DEFAULT NULL,
  `LongtermNotesAndAccountsPayable` int(11) DEFAULT NULL,
  `LongtermNotesAndAccountsPayable_p` float DEFAULT NULL,
  `AccruedPensionLiabilities` int(11) DEFAULT NULL,
  `AccruedPensionLiabilities_p` float DEFAULT NULL,
  `OtherNoncurrentLiabilitiesOthers` int(11) DEFAULT NULL,
  `OtherNoncurrentLiabilitiesOthers_p` float DEFAULT NULL,
  `OtherNoncurrentLiabilities` int(11) DEFAULT NULL,
  `OtherNoncurrentLiabilities_p` float DEFAULT NULL,
  `NoncurrentLiabilities` int(11) DEFAULT NULL,
  `NoncurrentLiabilities_p` float DEFAULT NULL,
  `Liabilities` int(11) DEFAULT NULL,
  `Liabilities_p` float DEFAULT NULL,
  `OrdinaryShare` int(11) DEFAULT NULL,
  `OrdinaryShare_p` float DEFAULT NULL,
  `CapitalStock` int(11) DEFAULT NULL,
  `CapitalStock_p` float DEFAULT NULL,
  `CapitalSurplusAdditionalPaidInCapitalArisingFromOrdinaryShare` int(11) DEFAULT NULL,
  `CapitalSurplusAdditionalPaidInCapitalArisingFromOrdinaryShare_p` float DEFAULT NULL,
  `CapitalSurplusAdditionalPaidInCapitalArisingFromBondConversion` int(11) DEFAULT NULL,
  `CapitalSurplusAdditionalPaidInCapitalArisingFromBondConversion_p` float DEFAULT NULL,
  `CapitalSurplusAdditionalPaidInCapital` int(11) DEFAULT NULL,
  `CapitalSurplusAdditionalPaidInCapital_p` float DEFAULT NULL,
  `X1` int(11) DEFAULT NULL,
  `X1_p` float DEFAULT NULL,
  `CapitalSurplusChangesInOwnershipInterestsInSubsidiaries` int(11) DEFAULT NULL,
  `CapitalSurplusChangesInOwnershipInterestsInSubsidiaries_p` float DEFAULT NULL,
  `CapitalSurplusOtherDonatedAssetsReceived` int(11) DEFAULT NULL,
  `CapitalSurplusOtherDonatedAssetsReceived_p` float DEFAULT NULL,
  `CapitalSurplusDonatedAssetsReceived` int(11) DEFAULT NULL,
  `CapitalSurplusDonatedAssetsReceived_p` float DEFAULT NULL,
  `X2` int(11) DEFAULT NULL,
  `X2_p` float DEFAULT NULL,
  `CapitalSurplusNetAssetsFromMerger` int(11) DEFAULT NULL,
  `CapitalSurplusNetAssetsFromMerger_p` float DEFAULT NULL,
  `CapitalSurplus` int(11) DEFAULT NULL,
  `CapitalSurplus_p` float DEFAULT NULL,
  `LegalReserve` int(11) DEFAULT NULL,
  `LegalReserve_p` float DEFAULT NULL,
  `SpecialReserve` int(11) DEFAULT NULL,
  `SpecialReserve_p` float DEFAULT NULL,
  `UnappropriatedRetainedEarningsAaccumulatedDeficit` int(11) DEFAULT NULL,
  `UnappropriatedRetainedEarningsAaccumulatedDeficit_p` float DEFAULT NULL,
  `RetainedEarnings` int(11) DEFAULT NULL,
  `RetainedEarnings_p` float DEFAULT NULL,
  `OtherEquityInterest` int(11) DEFAULT NULL,
  `OtherEquityInterest_p` float DEFAULT NULL,
  `EquityAttributableToOwnersOfParent` int(11) DEFAULT NULL,
  `EquityAttributableToOwnersOfParent_p` float DEFAULT NULL,
  `NoncontrollingInterests` int(11) DEFAULT NULL,
  `NoncontrollingInterests_p` float DEFAULT NULL,
  `Equity` int(11) DEFAULT NULL,
  `Equity_p` float DEFAULT NULL,
  `NumberOfShareCapitalAwaitingRetirement` int(11) DEFAULT NULL,
  `NumberOfShareCapitalAwaitingRetirement_p` float DEFAULT NULL,
  `EquivalentIssueSharesOfAdvanceReceiptsForOrdinaryShare` int(11) DEFAULT NULL,
  `NumberOfSharesInEntityHeldByEntityAndByItsSubsidiaries` int(11) DEFAULT NULL,
  PRIMARY KEY (`stock_no`,`year`,`season`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Income Statement
CREATE TABLE `statement_of_comprehensive_income` (
  `stock_no` char(10) NOT NULL,
  `year` int(11) NOT NULL,
  `season` int(11) NOT NULL,
  `OperatingRevenue` int(11) DEFAULT NULL,
  `OperatingRevenue_p` float DEFAULT NULL,
  `OperatingCosts` int(11) DEFAULT NULL,
  `OperatingCosts_p` float DEFAULT NULL,
  `GrossProfitLossFromOperations` int(11) DEFAULT NULL,
  `GrossProfitLossFromOperations_p` float DEFAULT NULL,
  `UnrealizedProfitLossFromSales` int(11) DEFAULT NULL,
  `UnrealizedProfitLossFromSales_p` float DEFAULT NULL,
  `RealizedProfitLossOnFromSales` int(11) DEFAULT NULL,
  `RealizedProfitLossOnFromSales_p` float DEFAULT NULL,
  `GrossProfitLossFromOperationsNet` int(11) DEFAULT NULL,
  `GrossProfitLossFromOperationsNet_p` float DEFAULT NULL,
  `SellingExpenses` int(11) DEFAULT NULL,
  `SellingExpenses_p` float DEFAULT NULL,
  `AdministrativeExpense` int(11) DEFAULT NULL,
  `AdministrativeExpense_p` float DEFAULT NULL,
  `ResearchAndDevelopmentExpenses` int(11) DEFAULT NULL,
  `ResearchAndDevelopmentExpenses_p` float DEFAULT NULL,
  `OperatingExpenses` int(11) DEFAULT NULL,
  `OperatingExpenses_p` float DEFAULT NULL,
  `NetOtherIncomeExpenses` int(11) DEFAULT NULL,
  `NetOtherIncomeExpenses_p` float DEFAULT NULL,
  `NetOperatingIncomeLoss` int(11) DEFAULT NULL,
  `NetOperatingIncomeLoss_p` float DEFAULT NULL,
  `OtherIncomeOthers` int(11) DEFAULT NULL,
  `OtherIncomeOthers_p` float DEFAULT NULL,
  `OtherRevenue` int(11) DEFAULT NULL,
  `OtherRevenue_p` float DEFAULT NULL,
  `ForeignExchangeGains` int(11) DEFAULT NULL,
  `ForeignExchangeGains_p` float DEFAULT NULL,
  `OtherGainsLosses` int(11) DEFAULT NULL,
  `OtherGainsLosses_p` float DEFAULT NULL,
  `FinanceCosts` int(11) DEFAULT NULL,
  `FinanceCosts_p` float DEFAULT NULL,
  `Y1` int(11) DEFAULT NULL,
  `Y1_p` float DEFAULT NULL,
  `NonoperatingIncomeAndExpenses` int(11) DEFAULT NULL,
  `NonoperatingIncomeAndExpenses_p` float DEFAULT NULL,
  `ProfitLossBeforeTax` int(11) DEFAULT NULL,
  `ProfitLossBeforeTax_p` float DEFAULT NULL,
  `IncomeTaxExpenseContinuingOperations` int(11) DEFAULT NULL,
  `IncomeTaxExpenseContinuingOperations_p` float DEFAULT NULL,
  `ProfitLossFromContinuingOperations` int(11) DEFAULT NULL,
  `ProfitLossFromContinuingOperations_p` float DEFAULT NULL,
  `ProfitLoss` int(11) DEFAULT NULL,
  `ProfitLoss_p` float DEFAULT NULL,
  `Y3` int(11) DEFAULT NULL,
  `Y3_p` float DEFAULT NULL,
  `Y4` int(11) DEFAULT NULL,
  `Y4_p` float DEFAULT NULL,
  `Y2` int(11) DEFAULT NULL,
  `Y2_p` float DEFAULT NULL,
  `IncomeTaxRelatingToComponentsOfOtherComprehensiveIncome` int(11) DEFAULT NULL,
  `IncomeTaxRelatingToComponentsOfOtherComprehensiveIncome_p` float DEFAULT NULL,
  `OtherComprehensiveIncome` int(11) DEFAULT NULL,
  `OtherComprehensiveIncome_p` float DEFAULT NULL,
  `ComprehensiveIncome` int(11) DEFAULT NULL,
  `ComprehensiveIncome_p` float DEFAULT NULL,
  `ProfitLossAttributableToOwnersOfParent` int(11) DEFAULT NULL,
  `ProfitLossAttributableToOwnersOfParent_p` float DEFAULT NULL,
  `ProfitLossAttributableToNoncontrollingInterests` int(11) DEFAULT NULL,
  `ProfitLossAttributableToNoncontrollingInterests_p` float DEFAULT NULL,
  `ComprehensiveIncomeAttributableToOwnersOfParent` int(11) DEFAULT NULL,
  `ComprehensiveIncomeAttributableToOwnersOfParent_p` float DEFAULT NULL,
  `ComprehensiveIncomeAttributableToNoncontrollingInterests` int(11) DEFAULT NULL,
  `ComprehensiveIncomeAttributableToNoncontrollingInterests_p` float DEFAULT NULL,
  `BasicEarningsLossPerShare` float DEFAULT NULL,
  `DilutedEarningsLossPerShare` float DEFAULT NULL,
  PRIMARY KEY (`stock_no`,`year`,`season`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- market_open_date
CREATE TABLE `market_open_date` (
  `date` date NOT NULL COMMENT '開市日期，自1992-06-01起至2017-3\n\n上市股票自1992-6\n\n上櫃股票自1994-1\n\n上市上櫃權證自2008-1',
  PRIMARY KEY (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- month_revenue
CREATE TABLE `month_revenue` (
  `stock_no` char(10) NOT NULL COMMENT '公司股票代號',
  `date` date NOT NULL COMMENT '本月營收之日期',
  `net_sales` bigint(20) NOT NULL COMMENT '本月營業淨收入',
  `pre_year_net_sales` bigint(20) NOT NULL COMMENT '前年同期營業淨收入',
  `increased_amount` bigint(20) NOT NULL COMMENT '增減金額 = 本月營業淨收入 - 前年同期營業淨收入',
  `increased_amount_percent` float NOT NULL COMMENT '增減金額百分比 = 增減金額 / 前年同期營業淨收入',
  `accumulated_amount` bigint(20) NOT NULL COMMENT '本年累計至當期之營業淨收總額',
  `pre_year_accumulated_amount` bigint(20) NOT NULL COMMENT '前年累計至當期之營業淨收總額',
  `accumulated_increased_amount` bigint(20) NOT NULL COMMENT '累計增減金額 = 本月營業淨收入 - 前年同期營業淨收入',
  `accumulated_increased_amount_percent` float NOT NULL COMMENT '累計增減金額百分比 = 累計增減金額 / 前年累計至當期之營業淨收總額',
  `note` text COMMENT '備註',
  PRIMARY KEY (`stock_no`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='台灣上市櫃月營收報表';

