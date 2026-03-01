import duckdb
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# ====================== CONFIG ======================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "../data/raw"
DB_PATH = PROJECT_ROOT / "../database/home_credit_dw.duckdb"

# Create the database folder if it doesn't exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

print("Starting to load the Data Warehouse...")

# ====================== Connect to DuckDB ======================
con = duckdb.connect(str(DB_PATH))

# Performance settings
con.execute("PRAGMA memory_limit='8GB';")
con.execute("PRAGMA threads=8;")

# ====================== Load all files ======================
files_to_load = {
    "application_train": "application_train.csv",
    "application_test": "application_test.csv",
    "previous_application": "previous_application.csv",
    "bureau": "bureau.csv",
    "bureau_balance": "bureau_balance.csv",
    "credit_card_balance": "credit_card_balance.csv",
    "installments_payments": "installments_payments.csv",
    "POS_CASH_balance": "POS_CASH_balance.csv",
    "HomeCredit_columns_description": "HomeCredit_columns_description.csv",
}

for table_name, filename in files_to_load.items():
    file_path = DATA_RAW / filename
    
    if file_path.exists():
        print(f"Loading {filename} ...")
        
        # Load directly into DuckDB (fastest way)
        con.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto('{file_path}', 
                header=True, 
                delim=',', 
                ignore_errors=True,
                sample_size=-1
            )
        """)
        
        # Print quick stats
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"{table_name}: {count:,} rows loaded successfully.")
    else:
        print(f"WARNING: File not found: {filename}")

# ====================== Create Star Schema Views ======================
print("\nCreating Star Schema Views...")

# Create fact table view combining train and test datasets
con.execute("""
    CREATE OR REPLACE VIEW fact_application AS 
    SELECT *, 'train' AS dataset FROM application_train
    UNION ALL BY NAME
    SELECT *, 'test'  AS dataset FROM application_test;
""")

print("fact_application view created (train + test, TARGET=NULL for test)")

# Create dimension view for clients to be used in future aggregations
con.execute("""
    CREATE OR REPLACE VIEW dim_client AS 
    SELECT DISTINCT 
        SK_ID_CURR, 
        CODE_GENDER, 
        FLAG_OWN_CAR, 
        FLAG_OWN_REALTY, 
        CNT_CHILDREN, 
        NAME_INCOME_TYPE, 
        NAME_EDUCATION_TYPE, 
        NAME_FAMILY_STATUS, 
        OCCUPATION_TYPE, 
        ORGANIZATION_TYPE 
    FROM fact_application;
""")

print("dim_client view created successfully.")

# ====================== Close connection ======================
con.close()
print(f"\nData Warehouse is 100% ready!")
print(f"Database path: {DB_PATH}")
print(f"Current database size: {DB_PATH.stat().st_size / (1024**3):.2f} GB")
print("\nNext step: run aggregations.py to build client-level features.")