import duckdb
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ====================== CONFIG ======================
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "../database/home_credit_dw.duckdb"
FIGURES_DIR = PROJECT_ROOT / "../reports/figures"
MODELS_DIR = PROJECT_ROOT / "../models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

print("🚀 Starting LightGBM Model Training (with Categorical Feature Support)...")

con = duckdb.connect(str(DB_PATH))

# Load training data only (TARGET IS NOT NULL)
df = con.execute("SELECT * FROM master_features WHERE TARGET IS NOT NULL").df()
print(f"✅ Data loaded: {df.shape[0]:,} rows")

# ====================== Prepare Features + Handle Categorical ======================
target = 'TARGET'
drop_cols = ['SK_ID_CURR', 'dataset', target]
feature_cols = [col for col in df.columns if col not in drop_cols]

X = df[feature_cols].copy()
y = df[target]

# 🔥 Critical fix: convert all object columns to 'category' dtype
cat_cols = X.select_dtypes(include=['object']).columns.tolist()
print(f"🔄 Converting {len(cat_cols)} categorical columns to 'category' dtype...")

for col in cat_cols:
    X[col] = X[col].astype('category')

print("✅ Categorical features converted successfully!")

# Train / Validation split
X_train, X_val, y_train, y_val = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"Training samples: {X_train.shape[0]:,} | Validation samples: {X_val.shape[0]:,}")

# ====================== LightGBM Parameters ======================
params = {
    'objective': 'binary',
    'boosting_type': 'gbdt',
    'metric': 'auc',
    'learning_rate': 0.05,
    'max_depth': 8,
    'num_leaves': 128,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': -1,
    'random_state': 42,
    'n_jobs': -1,
    'categorical_feature': 'auto'  # LightGBM automatically detects 'category' dtype columns
}

# ====================== Training ======================
print("🏋️ Training LightGBM model...")
lgb_train = lgb.Dataset(X_train, label=y_train)
lgb_val = lgb.Dataset(X_val, label=y_val, reference=lgb_train)

model = lgb.train(
    params,
    lgb_train,
    num_boost_round=2000,
    valid_sets=[lgb_train, lgb_val],
    callbacks=[lgb.early_stopping(100), lgb.log_evaluation(100)]
)

# ====================== Evaluation ======================
y_pred_prob = model.predict(X_val)
auc = roc_auc_score(y_val, y_pred_prob)
print(f"\n🎯 Validation AUC: {auc:.5f}")

y_pred = (y_pred_prob > 0.5).astype(int)
print(classification_report(y_val, y_pred))

# ====================== Feature Importance ======================
importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importance(importance_type='gain')
}).sort_values('importance', ascending=False).head(30)

plt.figure(figsize=(12,10))
sns.barplot(data=importance, x='importance', y='feature', palette='viridis')
plt.title('Top 30 Feature Importance (LightGBM)')
plt.savefig(FIGURES_DIR / '05_feature_importance.png', dpi=300, bbox_inches='tight')
plt.close()
print("📊 Feature importance plot saved")

# ====================== Save Model ======================
import joblib
joblib.dump(model, MODELS_DIR / 'lightgbm_default_risk.pkl')
print("💾 Model saved successfully!")

con.close()
print("\n🎉 Model training completed successfully! Ready for portfolio deployment.")