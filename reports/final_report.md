# Final Project Report - Home Credit Default Risk

**Date**: March 2026  
**Author**: Zainab Hashem  
**Objective**: Predict client default risk using relational banking data (Home Credit Default Risk - Kaggle)

### 1. Data Warehouse Architecture
- 10 raw CSV files (2.5 GB) loaded into **Star Schema** using DuckDB  
- Main fact table: `fact_application` + 6 fact tables (previous_application, bureau, credit_card_balance, installments_payments, POS_CASH_balance, bureau_balance)  
- Dimension view: `dim_client`  
- Final database size after compression: **0.87 GB**

### 2. Feature Engineering
- Built **50+ client-level aggregations** from 6 fact tables (count of approved loans, average credit amount, overdue ratio, late payment days, active loans, etc.)  
- Created `master_features` table: **356,255 clients × 135 columns**  
- These aggregations contributed significantly to model performance

### 3. Exploratory Data Analysis
- Default rate: **8.07%** (highly imbalanced)  
- Missing values: Housing features up to **69%** (COMMONAREA, NONLIVINGAPARTMENTS...)  
- Strongest correlations with TARGET:  
  - Positive: `DAYS_BIRTH` (+0.078)  
  - Negative: `EXT_SOURCE_3` (-0.179)

### 4. Modeling
- Algorithm: **LightGBM (gbdt)**  
- Validation AUC: **0.76889**  
- Early stopping after 181 rounds  
- Kaggle Public Score: **0.75883** | Private Score: **0.75608**  
- Top features (LightGBM Gain): EXT_SOURCE_3, EXT_SOURCE_2, ORGANIZATION_TYPE, DAYS_BIRTH, AMT_ANNUITY...

### 5. Business Impact
- Enables Home Credit to prioritize high-risk clients and reduce default rate  
- End-to-end pipeline ready for production (fast inference on new loan applications)

### Future Improvements
- Hyperparameter tuning with Optuna  
- Class weights / SMOTE for better recall on minority class  
- SHAP explainability  
- Time-based validation (to avoid leakage)

**Conclusion**  
Successfully implemented a **full end-to-end Data Engineering + Data Science pipeline** (Collect → DW → Feature Engineering → Modeling → Deployment) in under a week on a 2.5 GB relational dataset.