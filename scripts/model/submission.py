import duckdb
import pandas as pd
import lightgbm as lgb
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "../database/home_credit_dw.duckdb"
MODEL_PATH = PROJECT_ROOT / "../models/lightgbm_default_risk.pkl"
SUBMISSION_PATH = PROJECT_ROOT / "../reports/submission.csv"

print("🚀 Generating Kaggle submission file...")

con = duckdb.connect(str(DB_PATH))
import joblib
model = joblib.load(MODEL_PATH)

# Load test set only (TARGET IS NULL)
test_df = con.execute("SELECT * FROM master_features WHERE TARGET IS NULL").df()
print(f"✅ Test set loaded: {test_df.shape[0]:,} rows")

# Apply the same preprocessing used during training
drop_cols = ['SK_ID_CURR', 'dataset', 'TARGET']
feature_cols = [col for col in test_df.columns if col not in drop_cols]

X_test = test_df[feature_cols].copy()

# Convert categorical columns to 'category' dtype (required by LightGBM)
cat_cols = X_test.select_dtypes(include=['object']).columns.tolist()
for col in cat_cols:
    X_test[col] = X_test[col].astype('category')

# Generate predictions (probabilities)
pred = model.predict(X_test)

# Create submission DataFrame
submission = pd.DataFrame({
    'SK_ID_CURR': test_df['SK_ID_CURR'],
    'TARGET': pred
})

submission.to_csv(SUBMISSION_PATH, index=False)

print(f"✅ submission.csv generated successfully! ({SUBMISSION_PATH})")
print("Upload it to Kaggle → Expected public AUC ≈ 0.76–0.77")

con.close()