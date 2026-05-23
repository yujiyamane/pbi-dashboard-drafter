Generate another dashboard with different data.

config_text = r'''/*FACTORY
TITLE: Finance Dashboard
THEME(1:nsw-blue): 1
DB(1:Oracle 2:PostgreSQL 3:Snowflake 4:CSV 5:Excel): 4
SOURCE: C:\Users\Admin\Documents\Life\projects\pbi-dashboard-factory\finance_dummy_data.csv

1.CNT(max5): ①CNT_Measure_1 AS "Invoice Count" ②CNT_Measure_2 AS "Client Count" ③④⑤
2.SUM(max10): ①SUM_Measure_1 AS "Total Revenue"($#,0.00) ②SUM_Measure_2 AS "Total Cost"($#,0.00) ③SUM_Measure_3 AS "Total Profit"($#,0.00) ④SUM_Measure_4 AS "Total Tax"($#,0.00) ⑤⑥⑦⑧⑨⑩
3.AVG(max5): ①AVG_Measure_1 AS "Avg Margin"(%) ②AVG_Measure_2 AS "Avg Days to Pay"(#.0) ③④⑤
4.DATE: DateKey AS "Date Invoiced"
5.KEY(max10): ①Key_Dim_1 AS "Business Unit" ②Key_Dim_2 AS "Region" ③Key_Dim_3 AS "Account Type" ④Key_Dim_4 AS "Payment Method" ⑤⑥⑦⑧⑨⑩
6.OTHER: Other_Field_1 AS "Client Name", Other_Field_2 AS "Invoice Ref", Other_Field_3 AS "Notes"
*/'''