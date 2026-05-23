Generate a dashboard from this config.

config_text = r'''/*FACTORY
TITLE: HR Dashboard
THEME(1:nsw-blue): 1
DB(1:Oracle 2:PostgreSQL 3:Snowflake 4:CSV 5:Excel): 4
SOURCE: C:\Users\Admin\Documents\Life\projects\pbi-dashboard-factory\phase1_dummy_data.csv

1.CNT(max5): ①CNT_Measure_1 AS "Record ID" ②③④⑤
2.SUM(max10): ①SUM_Measure_1 AS "Total Budget"($#,0.00) ②SUM_Measure_2 AS "Headcount"(#) ③SUM_Measure_3 AS "Hours Worked"(#.0) ④⑤⑥⑦⑧⑨⑩
3.AVG(max5): ①AVG_Measure_1 AS "Avg Rating"(#.0) ②③④⑤
4.DATE: DateKey AS "Date Reported"
5.KEY(max10): ①Key_Dim_1 AS "Department" ②Key_Dim_2 AS "Office Location" ③Key_Dim_3 AS "Employment Type" ④Key_Dim_4 AS "Grade" ⑤⑥⑦⑧⑨⑩
6.OTHER: Other_Field_1 AS "Full Name", Other_Field_2 AS "Email", Other_Field_3 AS "Notes"
*/'''