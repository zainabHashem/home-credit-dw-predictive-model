import duckdb
from pathlib import Path
import time

# ====================== CONFIG ======================
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "../database/home_credit_dw.duckdb"

print("Starting Feature Engineering Aggregations (50+ features)...")
con = duckdb.connect(str(DB_PATH))

start_time = time.time()

# 1. Previous Applications Aggregations
print("1. Aggregating previous_application...")
con.execute("""
CREATE OR REPLACE TABLE agg_previous AS
SELECT 
    SK_ID_CURR,
    COUNT(*) AS prev_count,
    SUM(CASE WHEN NAME_CONTRACT_STATUS = 'Approved' THEN 1 ELSE 0 END) AS approved_count,
    AVG(AMT_CREDIT) AS avg_prev_credit,
    MAX(AMT_CREDIT) AS max_prev_credit,
    AVG(CNT_PAYMENT) AS avg_term,
    MAX(DAYS_DECISION) AS most_recent_prev_days,
    SUM(AMT_DOWN_PAYMENT) AS total_down_payment,
    AVG(AMT_ANNUITY) AS avg_annuity
FROM previous_application
GROUP BY SK_ID_CURR
""")

# 2. Bureau Aggregations
print("2. Aggregating bureau...")
con.execute("""
CREATE OR REPLACE TABLE agg_bureau AS
SELECT 
    SK_ID_CURR,
    COUNT(*) AS bureau_loans,
    SUM(CASE WHEN CREDIT_ACTIVE = 'Active' THEN 1 ELSE 0 END) AS active_loans,
    AVG(AMT_CREDIT_SUM) AS avg_credit_amount,
    MAX(AMT_CREDIT_MAX_OVERDUE) AS max_overdue,
    AVG(DAYS_CREDIT) AS avg_days_since_credit,
    SUM(AMT_CREDIT_SUM_DEBT) AS total_debt
FROM bureau
GROUP BY SK_ID_CURR
""")

# 3. Bureau Balance (Monthly)
print("3. Aggregating bureau_balance...")
con.execute("""
CREATE OR REPLACE TABLE agg_bureau_balance AS
SELECT 
    b.SK_ID_CURR,
    COUNT(*) AS bureau_months,
    SUM(CASE WHEN bb.STATUS = 'C' THEN 1 ELSE 0 END) AS closed_months,
    SUM(CASE WHEN bb.STATUS IN ('1','2','3','4','5') THEN 1 ELSE 0 END) AS overdue_months,
    AVG(CASE WHEN bb.STATUS IN ('1','2','3','4','5') THEN 1.0 ELSE 0 END) AS overdue_ratio
FROM bureau b
JOIN bureau_balance bb ON b.SK_ID_BUREAU = bb.SK_ID_BUREAU
GROUP BY b.SK_ID_CURR
""")

# 4. Credit Card Balance
print("4. Aggregating credit_card_balance...")
con.execute("""
CREATE OR REPLACE TABLE agg_credit_card AS
SELECT 
    SK_ID_CURR,
    COUNT(*) AS cc_months,
    AVG(AMT_BALANCE) AS avg_cc_balance,
    MAX(AMT_CREDIT_LIMIT_ACTUAL) AS max_limit,
    AVG(AMT_DRAWINGS_CURRENT / NULLIF(AMT_CREDIT_LIMIT_ACTUAL, 0)) AS avg_utilization,
    AVG(AMT_PAYMENT_TOTAL_CURRENT) AS avg_payment
FROM credit_card_balance
GROUP BY SK_ID_CURR
""")

# 5. Installments Payments
print("5. Aggregating installments_payments...")
con.execute("""
CREATE OR REPLACE TABLE agg_installments AS
SELECT 
    SK_ID_CURR,
    COUNT(*) AS installments_count,
    AVG(AMT_INSTALMENT) AS avg_inst_amount,
    SUM(AMT_PAYMENT) AS total_paid,
    AVG(DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT) AS avg_days_late,
    SUM(CASE WHEN (DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT) > 0 THEN 1 ELSE 0 END) AS late_count
FROM installments_payments
GROUP BY SK_ID_CURR
""")

# 6. POS CASH Balance
print("6. Aggregating POS_CASH_balance...")
con.execute("""
CREATE OR REPLACE TABLE agg_pos_cash AS
SELECT 
    SK_ID_CURR,
    COUNT(*) AS pos_months,
    SUM(CASE WHEN SK_DPD > 0 THEN 1 ELSE 0 END) AS pos_overdue_months,
    AVG(MONTHS_BALANCE) AS avg_pos_months
FROM POS_CASH_balance
GROUP BY SK_ID_CURR
""")

# ====================== Master Features Table (ready for Modeling) ======================
print("Creating master_features table (combining all aggregations with fact_application)...")
con.execute("""
CREATE OR REPLACE TABLE master_features AS
SELECT 
    f.* EXCLUDE(dataset),
    COALESCE(p.prev_count, 0) AS prev_count,
    COALESCE(p.approved_count, 0) AS approved_count,
    COALESCE(p.avg_prev_credit, 0) AS avg_prev_credit,
    COALESCE(b.bureau_loans, 0) AS bureau_loans,
    COALESCE(b.active_loans, 0) AS active_loans,
    COALESCE(b.avg_credit_amount, 0) AS avg_credit_amount,
    COALESCE(bb.bureau_months, 0) AS bureau_months,
    COALESCE(bb.overdue_ratio, 0) AS bureau_overdue_ratio,
    COALESCE(c.avg_cc_balance, 0) AS avg_cc_balance,
    COALESCE(c.avg_utilization, 0) AS avg_cc_utilization,
    COALESCE(i.avg_days_late, 0) AS avg_days_late,
    COALESCE(i.late_count, 0) AS late_count,
    COALESCE(pos.pos_overdue_months, 0) AS pos_overdue_months
FROM fact_application f
LEFT JOIN agg_previous p ON f.SK_ID_CURR = p.SK_ID_CURR
LEFT JOIN agg_bureau b ON f.SK_ID_CURR = b.SK_ID_CURR
LEFT JOIN agg_bureau_balance bb ON f.SK_ID_CURR = bb.SK_ID_CURR
LEFT JOIN agg_credit_card c ON f.SK_ID_CURR = c.SK_ID_CURR
LEFT JOIN agg_installments i ON f.SK_ID_CURR = i.SK_ID_CURR
LEFT JOIN agg_pos_cash pos ON f.SK_ID_CURR = pos.SK_ID_CURR
""")

print("All aggregations created successfully and master_features table is ready!")

# Final statistics
total_rows = con.execute("SELECT COUNT(*) FROM master_features").fetchone()[0]
print(f"master_features table contains {total_rows:,} rows")
print(f"Total time elapsed: {time.time() - start_time:.1f} seconds")

con.close()
print("\nFeature Engineering complete! Ready for EDA and Modeling.")