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

-- balance_sheet
CREATE TABLE `balance_sheet` (
  `stock_no` char(10) NOT NULL,
  `year` int(11) NOT NULL,
  `season` int(11) NOT NULL,
  `cash_and_cash_equivalents` bigint(20) DEFAULT NULL COMMENT '現金及約當現金 or 現金及約當現金合計',
  `cash_and_cash_equivalents_p` float DEFAULT NULL COMMENT '現金及約當現金 or 現金及約當現金合計%',
  `current_financial_assets_at_fair_value_through_profit_or_loss` bigint(20) DEFAULT NULL COMMENT '透過損益按公允價值衡量之金融資產-流動',
  `current_financial_assets_at_fair_value_through_profit_or_loss_p` float DEFAULT NULL COMMENT '透過損益按公允價值衡量之金融資產-流動%',
  `current_available_for_sale_financial_assets` bigint(20) DEFAULT NULL COMMENT '備供出售金融資產-流動淨額',
  `current_available_for_sale_financial_assets_p` float DEFAULT NULL COMMENT '備供出售金融資產-流動淨額%',
  `current_held_to_maturity_financial_assets` bigint(20) DEFAULT NULL COMMENT '持有至到期日金融資產-流動淨額',
  `current_held_to_maturity_financial_assets_p` float DEFAULT NULL COMMENT '持有至到期日金融資產-流動淨額%',
  `accounts_receivable_net` bigint(20) DEFAULT NULL COMMENT '應收帳款淨額',
  `accounts_receivable_net_p` float DEFAULT NULL COMMENT '應收帳款淨額%',
  `inventories` bigint(20) DEFAULT NULL COMMENT '存貨',
  `inventories_p` float DEFAULT NULL COMMENT '存貨%',
  `other_current_assets` bigint(20) DEFAULT NULL COMMENT '其他流動資產',
  `other_current_assets_p` float DEFAULT NULL COMMENT '其他流動資產%',
  `current_assets` bigint(20) DEFAULT NULL COMMENT '流動資產合計',
  `current_assets_p` float DEFAULT NULL COMMENT '流動資產合計%',
  `investment_accounted_for_using_equity_method` bigint(20) DEFAULT NULL COMMENT '採用權益法之投資 or 採用權益法之投資淨額',
  `investment_accounted_for_using_equity_method_p` float DEFAULT NULL COMMENT '採用權益法之投資 or 採用權益法之投資淨額%',
  `property_plant_and_equipment` bigint(20) DEFAULT NULL COMMENT '不動產、廠房及設備 or 不動產、廠房及設備合計',
  `property_plant_and_equipment_p` float DEFAULT NULL COMMENT '不動產、廠房及設備 or 不動產、廠房及設備合計%',
  `intangible_assets` bigint(20) DEFAULT NULL COMMENT '無形資產',
  `intangible_assets_p` float DEFAULT NULL COMMENT '無形資產%',
  `deferred_tax_assets` bigint(20) DEFAULT NULL COMMENT '遞延所得稅資產',
  `deferred_tax_assets_p` float DEFAULT NULL COMMENT '遞延所得稅資產%',
  `other_noncurrent_assets` bigint(20) DEFAULT NULL COMMENT '其他非流動資產',
  `other_noncurrent_assets_p` float DEFAULT NULL COMMENT '其他非流動資產%',
  `noncurrent_assets` bigint(20) DEFAULT NULL COMMENT '非流動資產合計 or 非流動資產合計',
  `noncurrent_assets_p` float DEFAULT NULL COMMENT '非流動資產合計 or 非流動資產合計%',
  `assets` bigint(20) DEFAULT NULL COMMENT '資產總額',
  `assets_p` float DEFAULT NULL COMMENT '資產總額%',
  `shortterm_borrowings` bigint(20) DEFAULT NULL COMMENT '短期借款 or 短期借款合計',
  `shortterm_borrowings_p` float DEFAULT NULL COMMENT '短期借款 or 短期借款合計%',
  `current_liabilities_c2` bigint(20) DEFAULT NULL COMMENT '透過損益按公允價值衡量之金融負債-流動 or 透過損益按公允價值衡量之金融負債－流動合計',
  `current_liabilities_c2_p` float DEFAULT NULL COMMENT '透過損益按公允價值衡量之金融負債-流動 or 透過損益按公允價值衡量之金融負債－流動合計%',
  `current_derivative_financial_liabilities_for_hedging` bigint(20) DEFAULT NULL COMMENT '避險之衍生金融負債-流動',
  `current_derivative_financial_liabilities_for_hedging_p` float DEFAULT NULL COMMENT '避險之衍生金融負債-流動%',
  `accounts_payable` bigint(20) DEFAULT NULL COMMENT '應付帳款',
  `accounts_payable_p` float DEFAULT NULL COMMENT '應付帳款%',
  `other_payables` bigint(20) DEFAULT NULL COMMENT '其他應付款 or 其他應付款合計',
  `other_payables_p` float DEFAULT NULL COMMENT '其他應付款 or 其他應付款合計%',
  `current_tax_liabilities` bigint(20) DEFAULT NULL COMMENT '本期所得稅負債 or 當期所得稅負債',
  `current_tax_liabilities_p` float DEFAULT NULL COMMENT '本期所得稅負債 or 當期所得稅負債%',
  `current_provisions` bigint(20) DEFAULT NULL COMMENT '負債準備-流動 or 負債準備－流動合計',
  `current_provisions_p` float DEFAULT NULL COMMENT '負債準備-流動 or 負債準備－流動合計%',
  `other_current_liabilities` bigint(20) DEFAULT NULL COMMENT '其他流動負債 or 其他流動負債合計',
  `other_current_liabilities_p` float DEFAULT NULL COMMENT '其他流動負債 or 其他流動負債合計%',
  `current_liabilities` bigint(20) DEFAULT NULL COMMENT '流動負債合計',
  `current_liabilities_p` float DEFAULT NULL COMMENT '流動負債合計%',
  `bonds_payable` bigint(20) DEFAULT NULL COMMENT '應付公司債 or 應付公司債合計',
  `bonds_payable_p` float DEFAULT NULL COMMENT '應付公司債 or 應付公司債合計%',
  `longterm_borrowings` bigint(20) DEFAULT NULL COMMENT '長期借款 or 長期借款合計',
  `longterm_borrowings_p` float DEFAULT NULL COMMENT '長期借款 or 長期借款合計%',
  `other_noncurrent_liabilities` bigint(20) DEFAULT NULL COMMENT '其他非流動負債 or 其他非流動負債合計',
  `other_noncurrent_liabilities_p` float DEFAULT NULL COMMENT '其他非流動負債 or 其他非流動負債合計%',
  `noncurrent_liabilities` bigint(20) DEFAULT NULL COMMENT '非流動負債合計',
  `noncurrent_liabilities_p` float DEFAULT NULL COMMENT '非流動負債合計%',
  `liabilities` bigint(20) DEFAULT NULL COMMENT '負債總計 or 負債總額',
  `liabilities_p` float DEFAULT NULL COMMENT '負債總計 or 負債總額',
  `ordinary_share` bigint(20) DEFAULT NULL COMMENT '普通股股本',
  `ordinary_share_p` float DEFAULT NULL COMMENT '普通股股本',
  `capital_stock` bigint(20) DEFAULT NULL COMMENT '股本合計',
  `capital_stock_p` float DEFAULT NULL COMMENT '股本合計%',
  `capital_surplus_additional_paid_in_capital` bigint(20) DEFAULT NULL COMMENT '資本公積-發行溢價',
  `capital_surplus_additional_paid_in_capital_p` float DEFAULT NULL COMMENT '資本公積-發行溢價%',
  `capital_surplus_c2` bigint(20) DEFAULT NULL COMMENT '資本公積-認列對子公司所有權權益變動數',
  `capital_surplus_c2_p` float DEFAULT NULL COMMENT '資本公積-認列對子公司所有權權益變動數%',
  `capital_surplus_donated_assets_received` bigint(20) DEFAULT NULL COMMENT '資本公積-受贈資產',
  `capital_surplus_donated_assets_received_p` float DEFAULT NULL COMMENT '資本公積-受贈資產%',
  `capital_surplus_c4` bigint(20) DEFAULT NULL COMMENT '資本公積-採用權益法認列關聯企業及合資股權淨值之變動數',
  `capital_surplus_c4_p` float DEFAULT NULL COMMENT '資本公積-採用權益法認列關聯企業及合資股權淨值之變動數%',
  `capital_surplus_net_assets_from_merger` bigint(20) DEFAULT NULL COMMENT '資本公積-合併溢額',
  `capital_surplus_net_assets_from_merger_p` float DEFAULT NULL COMMENT '資本公積-合併溢額%',
  `capital_surplus` bigint(20) DEFAULT NULL COMMENT '資本公積合計',
  `capital_surplus_p` float DEFAULT NULL COMMENT '資本公積合計%',
  `legal_reserve` bigint(20) DEFAULT NULL COMMENT '法定盈餘公積',
  `legal_reserve_p` float DEFAULT NULL COMMENT '法定盈餘公積%',
  `retained_earnings_c2` bigint(20) DEFAULT NULL COMMENT '未分配盈餘(或待彌補虧損)',
  `retained_earnings_c2_p` float DEFAULT NULL COMMENT '未分配盈餘(或待彌補虧損)%',
  `retained_earnings` bigint(20) DEFAULT NULL COMMENT '保留盈餘合計',
  `retained_earnings_p` float DEFAULT NULL COMMENT '保留盈餘合計%',
  `other_equity_interest` bigint(20) DEFAULT NULL COMMENT '其他權益合計',
  `other_equity_interest_p` float DEFAULT NULL COMMENT '其他權益合計%',
  `equity_attributable_to_owners_of_parent` bigint(20) DEFAULT NULL COMMENT '歸屬於母公司業主之權益合計',
  `equity_attributable_to_owners_of_parent_p` float DEFAULT NULL COMMENT '歸屬於母公司業主之權益合計%',
  `noncontrolling_interests` bigint(20) DEFAULT NULL COMMENT '非控制權益',
  `noncontrolling_interests_p` float DEFAULT NULL COMMENT '非控制權益%',
  `equity` bigint(20) DEFAULT NULL COMMENT '權益總計',
  `equity_p` float DEFAULT NULL COMMENT '權益總計%',
  `balance_sheet_other_column_1` bigint(20) DEFAULT NULL COMMENT '預收股款(權益項下)之約當發行股數(單位:股)',
  `balance_sheet_other_column_1_p` float DEFAULT NULL COMMENT '預收股款(權益項下)之約當發行股數(單位:股)%',
  `balance_sheet_other_column_2` bigint(20) DEFAULT NULL,
  `balance_sheet_other_column_2_p` float DEFAULT NULL COMMENT '母公司暨子公司所持有之母公司庫藏股股數(單位:股)%',
  PRIMARY KEY (`stock_no`,`year`,`season`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='資產負債表';

-- statement_of_comprehensive_income
CREATE TABLE `statement_of_comprehensive_income` (
  `stock_no` char(10) NOT NULL,
  `year` int(11) NOT NULL,
  `season` int(11) NOT NULL,
  `operating_revenue` bigint(20) DEFAULT NULL COMMENT '營業收入合計',
  `operating_revenue_p` float DEFAULT NULL COMMENT '營業收入合計%',
  `operating_costs` bigint(20) DEFAULT NULL COMMENT '營業成本合計',
  `operating_costs_p` float DEFAULT NULL COMMENT '營業成本合計%',
  `gross_profit_loss_from_operations` bigint(20) DEFAULT NULL COMMENT '營業毛利（毛損）',
  `gross_profit_loss_from_operations_p` float DEFAULT NULL COMMENT '營業毛利（毛損）%',
  `unrealized_profit_loss_from_sales` bigint(20) DEFAULT NULL COMMENT '未實現銷貨（損）益',
  `unrealized_profit_loss_from_sales_p` float DEFAULT NULL COMMENT '未實現銷貨（損）益%',
  `realized_profit_loss_on_from_sales` bigint(20) DEFAULT NULL COMMENT '已實現銷貨（損）益',
  `realized_profit_loss_on_from_sales_p` float DEFAULT NULL COMMENT '已實現銷貨（損）益%',
  `gross_profit_loss_from_operations_net` bigint(20) DEFAULT NULL COMMENT '營業毛利（毛損）淨額',
  `gross_profit_loss_from_operations_net_p` float DEFAULT NULL COMMENT '營業毛利（毛損）淨額%',
  `selling_expenses` bigint(20) DEFAULT NULL COMMENT '推銷費用',
  `selling_expenses_p` float DEFAULT NULL COMMENT '推銷費用%',
  `administrative_expense` bigint(20) DEFAULT NULL COMMENT '管理費用',
  `administrative_expense_p` float DEFAULT NULL COMMENT '管理費用%',
  `research_and_development_expenses` bigint(20) DEFAULT NULL COMMENT '研究發展費用',
  `research_and_development_expenses_p` float DEFAULT NULL COMMENT '研究發展費用%',
  `operating_expenses` bigint(20) DEFAULT NULL COMMENT '營業費用合計',
  `operating_expenses_p` float DEFAULT NULL COMMENT '營業費用合計%',
  `net_other_income_expenses` bigint(20) DEFAULT NULL COMMENT '其他收益及費損淨額',
  `net_other_income_expenses_p` float DEFAULT NULL COMMENT '其他收益及費損淨額%',
  `net_operating_income_loss` bigint(20) DEFAULT NULL COMMENT '營業利益（損失）',
  `net_operating_income_loss_p` float DEFAULT NULL COMMENT '營業利益（損失）%',
  `other_income_others` bigint(20) DEFAULT NULL COMMENT '其他收入',
  `other_income_others_p` float DEFAULT NULL COMMENT '其他收入%',
  `other_gains_losses` bigint(20) DEFAULT NULL COMMENT '其他利益及損失淨額',
  `other_gains_losses_p` float DEFAULT NULL COMMENT '其他利益及損失淨額%',
  `finance_costs` bigint(20) DEFAULT NULL COMMENT '財務成本淨額',
  `finance_costs_p` float DEFAULT NULL COMMENT '財務成本淨額%',
  `other_income_c4` bigint(20) DEFAULT NULL COMMENT '採用權益法認列之關聯企業及合資損益之份額淨額',
  `other_income_c4_p` float DEFAULT NULL COMMENT '採用權益法認列之關聯企業及合資損益之份額淨額%',
  `nonoperating_income_and_expenses` bigint(20) DEFAULT NULL COMMENT '營業外收入及支出合計',
  `nonoperating_income_and_expenses_p` float DEFAULT NULL COMMENT '營業外收入及支出合計%',
  `profit_loss_before_tax` bigint(20) DEFAULT NULL COMMENT '稅前淨利（淨損）',
  `profit_loss_before_tax_p` float DEFAULT NULL COMMENT '稅前淨利（淨損）%',
  `income_tax_expense_continuing_operations` bigint(20) DEFAULT NULL COMMENT '所得稅費用（利益）合計',
  `income_tax_expense_continuing_operations_p` float DEFAULT NULL COMMENT '所得稅費用（利益）合計%',
  `profit_loss_from_continuing_operations` bigint(20) DEFAULT NULL COMMENT '繼續營業單位本期淨利（淨損）',
  `profit_loss_from_continuing_operations_p` float DEFAULT NULL COMMENT '繼續營業單位本期淨利（淨損）%',
  `profit_loss` bigint(20) DEFAULT NULL COMMENT '本期淨利（淨損）',
  `profit_loss_p` float DEFAULT NULL COMMENT '本期淨利（淨損）%',
  `other_comprehensive_income` bigint(20) DEFAULT NULL COMMENT '其他綜合損益（淨額）',
  `other_comprehensive_income_p` float DEFAULT NULL COMMENT '其他綜合損益（淨額）%',
  `comprehensive_income` bigint(20) DEFAULT NULL COMMENT '本期綜合損益總額',
  `comprehensive_income_p` float DEFAULT NULL COMMENT '本期綜合損益總額%',
  `profit_loss_attributable_to_owners_of_parent` bigint(20) DEFAULT NULL COMMENT '母公司業主（淨利／損）',
  `profit_loss_attributable_to_owners_of_parent_p` float DEFAULT NULL COMMENT '母公司業主（淨利／損）%',
  `profit_loss_attributable_to_noncontrolling_interests` bigint(20) DEFAULT NULL COMMENT '非控制權益（淨利／損）',
  `profit_loss_attributable_to_noncontrolling_interests_p` float DEFAULT NULL COMMENT '非控制權益（淨利／損）%',
  `comprehensive_income_attributable_to_owners_of_parent` bigint(20) DEFAULT NULL COMMENT '母公司業主（綜合損益）',
  `comprehensive_income_attributable_to_owners_of_parent_p` float DEFAULT NULL COMMENT '母公司業主（綜合損益）%',
  `comprehensive_income_attributable_to_noncontrolling_interests` bigint(20) DEFAULT NULL COMMENT '非控制權益（綜合損益）',
  `comprehensive_income_attributable_to_noncontrolling_interests_p` float DEFAULT NULL COMMENT '非控制權益（綜合損益）%',
  `basic_earnings_loss_per_share` float DEFAULT NULL COMMENT '基本每股盈餘',
  `diluted_earnings_loss_per_share` float DEFAULT NULL COMMENT '稀釋每股盈餘',
  PRIMARY KEY (`stock_no`,`year`,`season`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='綜合損益表';
