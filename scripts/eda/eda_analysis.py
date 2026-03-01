import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ====================== CONFIG ======================
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "../database/home_credit_dw.duckdb"
FIGURES_DIR = PROJECT_ROOT / "../reports/figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

print("🚀 Starting Professional EDA on master_features...")

con = duckdb.connect(str(DB_PATH))

# Load master_features into Pandas DataFrame (very fast)
df = con.execute("SELECT * FROM master_features").df()

print(f"✅ master_features loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ====================== 1. TARGET Distribution ======================
plt.figure(figsize=(8,5))
sns.countplot(data=df, x='TARGET', palette='viridis')
plt.title('TARGET Distribution (Default Risk)', fontsize=16)
plt.ylabel('Number of Clients')
plt.savefig(FIGURES_DIR / '01_target_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("📊 1. Target distribution saved")

# ====================== 2. Missing Values ======================
missing = df.isnull().mean() * 100
missing = missing[missing > 0].sort_values(ascending=False)
print(f"🔍 Top 10 columns with missing values: \n{missing.head(10)}")

missing.head(15).plot(kind='barh', figsize=(10,6), color='orange')
plt.title('Top 15 Missing Values (%)')
plt.xlabel('% Missing')
plt.savefig(FIGURES_DIR / '02_missing_values.png', dpi=300, bbox_inches='tight')
plt.close()

# ====================== 3. Numerical Features Statistics ======================
num_cols = df.select_dtypes(include=['float64', 'int64']).columns
stats = df[num_cols].describe().T
stats.to_csv(PROJECT_ROOT / "reports/numerical_stats.csv")
print("📋 Numerical statistics saved to reports/")

# ====================== 4. Correlation with TARGET (Top 20) ======================
corr = df[num_cols].corr()['TARGET'].sort_values(ascending=False).drop('TARGET')
top_corr = corr.head(20)

plt.figure(figsize=(10,8))
sns.barplot(x=top_corr.values, y=top_corr.index, palette='coolwarm')
plt.title('Top 20 Features Correlated with TARGET')
plt.xlabel('Correlation')
plt.savefig(FIGURES_DIR / '03_top_correlations.png', dpi=300, bbox_inches='tight')
plt.close()
print("📈 Top correlations plot saved")

# ====================== 5. Key Feature Distributions ======================
key_features = [
    'avg_prev_credit',
    'bureau_loans',
    'avg_cc_balance',
    'avg_days_late',
    'late_count',
    'bureau_overdue_ratio'
]

for feat in key_features:
    if feat in df.columns:
        plt.figure(figsize=(8,5))
        sns.histplot(data=df, x=feat, hue='TARGET', bins=50, kde=True)
        plt.title(f'Distribution of {feat} by TARGET')
        plt.savefig(FIGURES_DIR / f'04_dist_{feat}.png', dpi=300, bbox_inches='tight')
        plt.close()

print("📊 Key feature distributions saved")

# ====================== 6. Save Summary Report ======================
summary = f"""
=== EDA Summary Report ===
Total rows: {df.shape[0]:,}
Total columns: {df.shape[1]}
Default rate: {df['TARGET'].mean()*100:.2f}%
Missing columns: {len(missing)}

Top positive correlation with TARGET: {corr.index[0]} ({corr.iloc[0]:.3f})
Top negative correlation: {corr.index[-1]} ({corr.iloc[-1]:.3f})
"""

with open(PROJECT_ROOT / "reports/eda_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)

print("\n🎉 EDA completed successfully! All plots saved in reports/figures/")
print("📁 Open the reports/figures folder to review the visualizations")
print("Next Step: Model Training (LightGBM)")

con.close()