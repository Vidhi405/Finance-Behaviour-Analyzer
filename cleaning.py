"""
Complete Clean and Retrain Pipeline
Removes outliers and retrains all models with lower sensitivity
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
import os
import json

print("="*60)
print("CLEANING DATA & RETRAINING MODELS")
print("="*60)

# ============================================
# 1. LOAD AND CLEAN DATA
# ============================================

print("\n📂 Loading cleaned dataset...")
df = pd.read_csv('outputs/cleaned_dataset1.csv', parse_dates=['date'])
print(f"   Before cleaning: {len(df):,} rows")
print(f"   Max amount: ₹{df['amount'].max():,.2f}")

# Remove extreme outliers (above ₹1,00,000)
MAX_AMOUNT = 100000
outliers = df[df['amount'] > MAX_AMOUNT]
print(f"\n🚫 Removing {len(outliers):,} outlier transactions above ₹{MAX_AMOUNT:,.0f}")

df = df[df['amount'] <= MAX_AMOUNT].copy()
print(f"   After removal: {len(df):,} rows")
print(f"   New max amount: ₹{df['amount'].max():,.2f}")

# Save cleaned data
df.to_csv('outputs/cleaned_dataset1_no_outliers.csv', index=False)
print(f"\n💾 Saved: outputs/cleaned_dataset1_no_outliers.csv")

# ============================================
# 2. ENGINEER FEATURES
# ============================================

print("\n🔧 Engineering features...")

# Amount features
df['amount_log'] = np.log1p(df['amount'])

# Time features
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
df['day_of_week'] = df['date'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

# Category dummies
cat_dummies = pd.get_dummies(df['category'], prefix='cat')
df = pd.concat([df, cat_dummies], axis=1)

# Day of week dummies
dow_dummies = pd.get_dummies(df['day_of_week'], prefix='dow')
df = pd.concat([df, dow_dummies], axis=1)

# Payment mode dummies
if 'payment_mode' in df.columns:
    df['payment_mode'] = df['payment_mode'].str.strip().str.title()
    pmt_dummies = pd.get_dummies(df['payment_mode'], prefix='payment')
    df = pd.concat([df, pmt_dummies], axis=1)

# ============================================
# 3. PREPARE FEATURES
# ============================================

print("\n📊 Preparing feature matrix...")

feature_cols = ['amount_log', 'month', 'day_of_week', 'is_weekend']

# Add category dummies
cat_cols = [col for col in df.columns if col.startswith('cat_')]
feature_cols.extend(cat_cols)

# Add day of week dummies
dow_cols = [col for col in df.columns if col.startswith('dow_')]
feature_cols.extend(dow_cols)

# Add payment mode dummies
pmt_cols = [col for col in df.columns if col.startswith('payment_')]
feature_cols.extend(pmt_cols)

X = df[feature_cols].fillna(0)
X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

print(f"   Feature matrix: {X.shape[0]:,} rows, {X.shape[1]} features")

# ============================================
# 4. TRAIN ISOLATION FOREST (LOWER SENSITIVITY)
# ============================================

print("\n🌲 Training Isolation Forest...")

# Test different contamination levels
print("   Testing contamination levels:")
contamination_options = [0.02, 0.03, 0.05]

for cont in contamination_options:
    iso_test = IsolationForest(contamination=cont, random_state=42, n_estimators=100)
    pred = iso_test.fit_predict(X)
    anomalies = (pred == -1).sum()
    print(f"      contamination={cont}: {anomalies} anomalies ({anomalies/len(X)*100:.2f}%)")

# Use 0.02 for stricter anomaly detection (only flag truly unusual)
iso_forest = IsolationForest(contamination=0.02, random_state=42, n_estimators=100)
anomaly_pred = iso_forest.fit_predict(X)
anomaly_labels = (anomaly_pred == -1).astype(int)

anomaly_count = anomaly_labels.sum()
print(f"\n   ✅ Using contamination=0.02")
print(f"   Anomalies detected: {anomaly_count:,} ({anomaly_count/len(X)*100:.2f}%)")

# ============================================
# 5. TRAIN K-MEANS
# ============================================

print("\n🎯 Training K-Means...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(X_scaled)

silhouette = silhouette_score(X_scaled, cluster_labels)
print(f"   Silhouette Score: {silhouette:.4f}")

print(f"\n   Cluster distribution:")
for i in range(4):
    count = (cluster_labels == i).sum()
    print(f"      Cluster {i}: {count:,} ({count/len(X)*100:.1f}%)")

# ============================================
# 6. ADD LABELS TO DATAFRAME
# ============================================

print("\n🏷️ Adding labels to dataframe...")
df['is_anomaly'] = anomaly_labels
df['cluster'] = cluster_labels

# ============================================
# 7. SAVE MODELS AND DATA
# ============================================

print("\n💾 Saving models and data...")

# Create models directory if not exists
os.makedirs('models', exist_ok=True)

# Save models
joblib.dump(iso_forest, 'models/isolation_forest.pkl')
joblib.dump(kmeans, 'models/kmeans.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
print("   ✅ Models saved to models/")

# Save labeled dataset
df.to_csv('outputs/labeled_dataset.csv', index=False)
print("   ✅ Labeled dataset saved to outputs/labeled_dataset.csv")

# Save feature columns list for backend
with open('models/feature_columns.json', 'w') as f:
    json.dump(feature_cols, f, indent=2)
print("   ✅ Feature columns saved to models/feature_columns.json")

# ============================================
# 8. GENERATE SUMMARY
# ============================================

print("\n" + "="*60)
print("✅ RETRAINING COMPLETE!")
print("="*60)
print(f"\n📊 FINAL DATA SUMMARY:")
print(f"   Total transactions: {len(df):,}")
print(f"   Total spending: ₹{df['amount'].sum():,.2f}")
print(f"   Average transaction: ₹{df['amount'].mean():,.2f}")
print(f"   Max transaction: ₹{df['amount'].max():,.2f}")
print(f"   Min transaction: ₹{df['amount'].min():,.2f}")
print(f"   Anomalies: {anomaly_count:,} ({anomaly_count/len(X)*100:.2f}%)")
print(f"   Clusters: 4")
print(f"   Features: {len(feature_cols)}")

# Category breakdown
print(f"\n📊 TOP SPENDING CATEGORIES:")
category_spend = df.groupby('category')['amount'].sum().sort_values(ascending=False).head(5)
for cat, amt in category_spend.items():
    print(f"   {cat}: ₹{amt:,.2f}")

# Payment mode breakdown
if 'payment_mode' in df.columns:
    print(f"\n💳 PAYMENT MODE DISTRIBUTION:")
    pmt_dist = df['payment_mode'].value_counts()
    for mode, count in pmt_dist.items():
        print(f"   {mode}: {count:,} transactions ({count/len(df)*100:.1f}%)")

# Check Food transactions by payment mode
print(f"\n🍔 FOOD TRANSACTIONS BY PAYMENT MODE:")
food_df = df[df['category'] == 'Food']
food_pmt = food_df['payment_mode'].value_counts()
for mode, count in food_pmt.items():
    print(f"   {mode}: {count:,} transactions ({count/len(food_df)*100:.1f}%)")

# Anomaly breakdown by category
print(f"\n⚠️ ANOMALIES BY CATEGORY:")
anomaly_cats = df[df['is_anomaly'] == 1]['category'].value_counts().head(10)
for cat, count in anomaly_cats.items():
    print(f"   {cat}: {count} anomalies")

print("\n" + "="*60)
print("✨ Now run: python ml_backend.py")
print("="*60)