# python-taiwan-stock

## Target
- Help someone to build their own financial database 



## Feature
- Base on python 2.7 & mysql
- Crawl Taiwan financial data to local database which build yourself
- Basic Fundamental Analysis



#Financial Statements

###Statement of Comprehensive Income
|            欄位          |           名稱          |
--------------------------|-------------------------
OperatingRevenue | operating_revenue
OperatingCosts | operating_costs
GrossProfitLossFromOperations| gross_profit_loss_from_operations
UnrealizedProfitLossOnFromSales| unrealized_profit_loss_from_sales
RealizedProfitLossOnFromSales| realized_profit_loss_on_from_sales
GrossProfitLossFromOperationsNet| gross_profit_loss_from_operations_net
OperatingExpenses|
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;SellingExpenses| selling_expenses
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;AdministrativeExpense| administrative_expense
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ResearchAndDevelopmentExpenses| research_and_development_expenses
&nbsp;&nbsp;&nbsp;&nbsp;OperatingExpenses| operating_expenses
NetOtherIncomeExpenses|
&nbsp;&nbsp;&nbsp;&nbsp;NetOtherIncomeExpenses| net_other_income_expenses
NetOperatingIncomeLoss| net_operating_income_loss
NonoperatingIncomeAndExpenses|
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OtherIncomeOthers| other_income_others
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OtherGainsLosses| other_gains_losses
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;FinanceCosts| finance_costs
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ShareOfProfitLossOfAssociatesAndJointVenturesAccountedForUsingEquityMethod| **other_income_c4**
&nbsp;&nbsp;&nbsp;&nbsp;NonoperatingIncomeAndExpenses| nonoperating_income_and_expenses
ProfitLossBeforeTax| profit_loss_before_tax
IncomeTaxExpenseContinuingOperations| income_tax_expense_continuing_operations
ProfitLossFromContinuingOperations| profit_loss_from_continuing_operations
ProfitLoss| profit_loss
ItemsLikelyToBeReclassifiedToProfitOrLossInSubsequentPeriod|
&nbsp;&nbsp;&nbsp;&nbsp;OtherComprehensiveIncome| other_comprehensive_income
ComprehensiveIncome| comprehensive_income
ProfitLossAttributableToOwnersOfParent| profit_loss_attributable_to_owners_of_parent
ProfitLossAttributableToNoncontrollingInterests| profit_loss_attributable_to_noncontrolling_interests
ComprehensiveIncomeAttributableToOwnersOfParent| comprehensive_income_attributable_to_owners_of_parent
ComprehensiveIncomeAttributableToNoncontrollingInterests| comprehensive_income_attributable_to_noncontrolling_interests
BasicEarningsLossPerShare|
&nbsp;&nbsp;&nbsp;&nbsp;BasicEarningsLossPerShare| basic_earnings_loss_per_share
DilutedEarningsLossPerShare|
&nbsp;&nbsp;&nbsp;&nbsp;DilutedEarningsLossPerShare| diluted_earnings_loss_per_share
####GrossProfitLossFromOperationsNet
- GrossProfitLossFromOperations ＋ UnrealizedProfitLossOnFromSales + RealizedProfitLossOnFromSales
####OperatingExpenses
- SellingExpenses + AdministrativeExpense + ResearchAndDevelopmentExpenses
####NonoperatingIncomeAndExpenses
- OtherIncomeOthers + OtherGainsLosses - FinanceCosts + ShareOfProfitLossOfAssociatesAndJointVenturesAccountedForUsingEquityMethod



## The project is keep ongoing and update irregularly





# python-taiwan-stock (Traditional Chinese)

## 目的
- 協助使用者建立屬於自己的的金融資料庫



## 功能
- 開發在 python 2.7 & mysql
- 爬台灣金融資料到本地端建立的資料庫
- 簡易的基本分析



##財務報表

###綜合損益表
|            欄位          |           名稱          |
--------------------------|-------------------------
營業收入合計 | operating_revenue
營業成本合計 | operating_costs
營業毛利(毛損)| gross_profit_loss_from_operations
未實現銷貨(損)益| unrealized_profit_loss_from_sales
已實現銷貨(損)益| realized_profit_loss_on_from_sales
營業毛利(毛損)淨額| gross_profit_loss_from_operations_net
營業費用|
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;推銷費用| selling_expenses
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;管理費用| administrative_expense
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;研究發展費用| research_and_development_expenses
&nbsp;&nbsp;&nbsp;&nbsp;營業費用合計| operating_expenses
其他收益及費損淨額|
&nbsp;&nbsp;&nbsp;&nbsp;其他收益及費損淨額| net_other_income_expenses
營業利益(損失)| net_operating_income_loss
營業外收入及支出|
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;其他收入| other_income_others
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;其他利益及損失淨額| other_gains_losses
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;財務成本淨額| finance_costs
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;採用權益法認列之關聯企業及合資損益之份額淨額| **other_income_c4**
&nbsp;&nbsp;&nbsp;&nbsp;營業外收入及支出合計| nonoperating_income_and_expenses
稅前淨利(淨損)| profit_loss_before_tax
所得稅費用(利益)合計| income_tax_expense_continuing_operations
繼續營業單位本期淨利(淨損)| profit_loss_from_continuing_operations
本期淨利(淨損)| profit_loss
後續可能重分類至損益之項目|
&nbsp;&nbsp;&nbsp;&nbsp;其他綜合損益(淨額)| other_comprehensive_income
本期綜合損益總額| comprehensive_income
&nbsp;&nbsp;&nbsp;&nbsp;母公司業主(淨利／損)| profit_loss_attributable_to_owners_of_parent
&nbsp;&nbsp;&nbsp;&nbsp;非控制權益(淨利／損)| profit_loss_attributable_to_noncontrolling_interests
&nbsp;&nbsp;&nbsp;&nbsp;母公司業主(綜合損益)| comprehensive_income_attributable_to_owners_of_parent
&nbsp;&nbsp;&nbsp;&nbsp;非控制權益(綜合損益)| comprehensive_income_attributable_to_noncontrolling_interests
基本每股盈餘|
&nbsp;&nbsp;&nbsp;&nbsp;基本每股盈餘| basic_earnings_loss_per_share
稀釋每股盈餘|
&nbsp;&nbsp;&nbsp;&nbsp;稀釋每股盈餘| diluted_earnings_loss_per_share
####營業毛利(毛損)淨額
- 營業毛利(毛損) ＋ 未實現銷貨(損)益 + 已實現銷貨(損)益
####營業費用合計
- 推銷費用 + 管理費用 + 研究發展費用
####營業外收入及支出合計
- 其他收入 + 其他利益及損失淨額 - 財務成本淨額 + 採用權益法認列之關聯企業及合資損益之份額淨額



## 本專案持續開發中，且會不定期更新
