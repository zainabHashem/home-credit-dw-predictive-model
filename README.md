# Home Credit Default Risk - End-to-End Data Warehouse + Predictive Model

![Kaggle Score](https://img.shields.io/badge/Kaggle-Public%20Score%200.75883-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![DuckDB](https://img.shields.io/badge/DuckDB-1.0+-yellow)
![LightGBM](https://img.shields.io/badge/LightGBM-AUC%200.76889-orange)

**Full End-to-End Pipeline**: Collect → Data Warehouse → Feature Engineering → EDA → Modeling → Deployment

---

### 📊 Project Overview
Built a complete **Star Schema Data Warehouse** on the famous Home Credit Default Risk dataset (2.5 GB, 10 relational CSV files).  
Performed advanced feature engineering with **50+ client-level aggregations**, comprehensive EDA, and trained a **LightGBM model** achieving:

- **Validation AUC**: **0.76889**
- **Kaggle Public Score**: **0.75883**
- **Kaggle Private Score**: **0.75608**

---

### 🏗️ Data Warehouse Schema (Star Schema)

```mermaid
erDiagram
    FACT_APPLICATION {
        int SK_ID_CURR PK
        int TARGET
        float AMT_CREDIT
        string NAME_CONTRACT_TYPE
    }

    DIM_CLIENT {
        int SK_ID_CURR PK
        string CODE_GENDER
        string NAME_INCOME_TYPE
        string ORGANIZATION_TYPE
    }

    FACT_PREVIOUS_APPLICATION {
        int SK_ID_PREV PK
        int SK_ID_CURR FK
        float AMT_CREDIT
    }

    FACT_BUREAU {
        int SK_ID_BUREAU PK
        int SK_ID_CURR FK
        float AMT_CREDIT_SUM
    }

    FACT_CREDIT_CARD {
        int SK_ID_PREV FK
        float AMT_BALANCE
    }

    FACT_INSTALLMENTS {
        int SK_ID_PREV FK
        float AMT_PAYMENT
    }

    FACT_POS_CASH {
        int SK_ID_PREV FK
        int SK_DPD
    }

    FACT_APPLICATION ||--o{ DIM_CLIENT : "belongs_to"
    FACT_APPLICATION ||--o{ FACT_PREVIOUS_APPLICATION : "has_many"
    FACT_APPLICATION ||--o{ FACT_BUREAU : "has_many"
    FACT_PREVIOUS_APPLICATION ||--o{ FACT_CREDIT_CARD : "has_monthly"
    FACT_PREVIOUS_APPLICATION ||--o{ FACT_INSTALLMENTS : "has_payments"
    FACT_PREVIOUS_APPLICATION ||--o{ FACT_POS_CASH : "has_monthly"

```
Star Schema Design: Central fact_application table connected to one dimension table and multiple historical fact tables for rich behavioral features.

🛠️ Tech Stack

Data Warehouse: DuckDB (Star Schema + Views)
ETL & Aggregations: Python + SQL
EDA & Visualization: Pandas, Matplotlib, Seaborn
Modeling: LightGBM

📁 Project Structure
texthome_credit_dw_project/
├── database/                  # home_credit_dw.duckdb (0.87 GB)
├── data/raw/                  # Original 10 CSVs
├── scripts/
│   ├── etl/load_to_duckdb.py
│   ├── features/aggregations.py
│   ├── eda/eda_analysis.py
│   └── model/train_lightgbm.py + submission.py
├── reports/figures/           # All plots
├── models/                    # lightgbm_default_risk.txt
├── reports/                   # final_report.md + submission.csv
└── README.md

📈 Exploratory Data Analysis

Top Missing Values
<img src="reports/figures/02_missing_values.png" alt="Missing Values">
Top Correlations with TARGET
<img src="reports/figures/03_top_correlations.png" alt="Top Correlations">
Key Feature Distributions
<img src="reports/figures/04_dist_avg_cc_balance.png" alt="Avg CC Balance">
<img src="reports/figures/04_dist_avg_days_late.png" alt="Avg Days Late">
<img src="reports/figures/04_dist_avg_prev_credit.png" alt="Avg Previous Credit">
<img src="reports/figures/04_dist_bureau_loans.png" alt="Bureau Loans">
<img src="reports/figures/04_dist_bureau_overdue_ratio.png" alt="Bureau Overdue Ratio">
<img src="reports/figures/04_dist_late_count.png" alt="Late Count">
Feature Importance (LightGBM)
<img src="reports/figures/05_feature_importance.png" alt="Feature Importance">

🎯 Model Results

Validation AUC: 0.76889
Kaggle Public Score: 0.75883
Top Features: EXT_SOURCE_3, EXT_SOURCE_2, ORGANIZATION_TYPE, DAYS_BIRTH, late_count, bureau_overdue_ratio


🚀 How to Reproduce
Bashgit clone https://github.com/zainabHashem/home-credit-dw-predictive-model.git
cd home-credit-dw-predictive-model
pip install -r requirements.txt
# Put the 10 CSVs in data/raw/
python scripts/etl/load_to_duckdb.py
python scripts/features/aggregations.py
python scripts/model/train_lightgbm.py
python scripts/model/submission.py

📋 Portfolio Highlights

Designed & implemented Star Schema Data Warehouse on 2.5 GB relational dataset (27M+ rows)
Built 50+ client-level aggregations from 6 fact tables
Achieved Kaggle Public AUC 0.75883 with LightGBM
Complete end-to-end automated pipeline

Made with ❤️ by Zainab Hashem
March 2026
