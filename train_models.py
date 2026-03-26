"""
Train Models on Cleaned Dataset
Personal Finance Behavior Analyzer
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import joblib
import logging
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================
# CONFIGURATION
# ============================================

INPUT_FILE = "outputs/cleaned_dataset1.csv"
OUTPUT_DIR = "outputs"
MODELS_DIR = "models"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# ML Parameters
ISOLATION_FOREST_PARAMS = {
    'contamination': 0.05,
    'random_state': 42,
    'n_estimators': 100
}

KMEANS_PARAMS = {
    'n_clusters': 4,
    'random_state': 42,
    'n_init': 10
}


def load_data():
    """Load cleaned dataset"""
    logger.info("="*60)
    logger.info("LOADING CLEANED DATASET")
    logger.info("="*60)
    
    df = pd.read_csv(INPUT_FILE, parse_dates=['date'])
    logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
    
    # Display amount stats
    logger.info(f"\nAmount Statistics:")
    logger.info(f"  Min: ₹{df['amount'].min():,.2f}")
    logger.info(f"  Max: ₹{df['amount'].max():,.2f}")
    logger.info(f"  Mean: ₹{df['amount'].mean():,.2f}")
    logger.info(f"  Median: ₹{df['amount'].median():,.2f}")
    
    return df


def engineer_features(df):
    """Create features for ML models"""
    logger.info("\n--- ENGINEERING FEATURES ---")
    
    # Amount features
    df['amount_log'] = np.log1p(df['amount'])
    
    # Category one-hot encoding
    cat_dummies = pd.get_dummies(df['category'], prefix='cat')
    df = pd.concat([df, cat_dummies], axis=1)
    
    # Day of week dummies
    dow_dummies = pd.get_dummies(df['day_of_week'], prefix='dow')
    df = pd.concat([df, dow_dummies], axis=1)
    
    # Payment mode dummies
    if 'payment_mode' in df.columns:
        pmt_dummies = pd.get_dummies(df['payment_mode'], prefix='payment')
        df = pd.concat([df, pmt_dummies], axis=1)
    
    logger.info(f"Added {len(cat_dummies.columns)} category features")
    logger.info(f"Added {len(dow_dummies.columns)} day-of-week features")
    
    return df


def prepare_ml_features(df):
    """Prepare feature matrix - ONLY numeric columns"""
    # Numeric features
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
    
    # Select only these columns
    X = df[feature_cols].copy()
    
    # Ensure all columns are numeric
    X = X.apply(pd.to_numeric, errors='coerce')
    X = X.fillna(0)
    
    logger.info(f"Feature matrix: {X.shape[0]:,} rows, {X.shape[1]} features")
    
    return X, feature_cols


def train_models(X):
    """Train Isolation Forest and K-Means"""
    logger.info("\n" + "="*50)
    logger.info("TRAINING MODELS")
    logger.info("="*50)
    
    # 1. Isolation Forest (Anomaly Detection)
    logger.info("\n1. Isolation Forest (Anomaly Detection)...")
    iso_forest = IsolationForest(**ISOLATION_FOREST_PARAMS)
    anomaly_labels = iso_forest.fit_predict(X)
    anomaly_labels = (anomaly_labels == -1).astype(int)
    
    anomaly_count = anomaly_labels.sum()
    logger.info(f"   Anomalies detected: {anomaly_count:,} ({anomaly_count/len(X)*100:.2f}%)")
    
    # 2. K-Means (Behavioral Clustering)
    logger.info("\n2. K-Means (Behavioral Clustering)...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(**KMEANS_PARAMS)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    # Cluster metrics
    silhouette = silhouette_score(X_scaled, cluster_labels)
    calinski = calinski_harabasz_score(X_scaled, cluster_labels)
    davies = davies_bouldin_score(X_scaled, cluster_labels)
    
    logger.info(f"   Silhouette Score: {silhouette:.4f}")
    logger.info(f"   Calinski-Harabasz: {calinski:.2f}")
    logger.info(f"   Davies-Bouldin: {davies:.4f}")
    
    logger.info(f"\n   Cluster distribution:")
    for i in range(KMEANS_PARAMS['n_clusters']):
        count = (cluster_labels == i).sum()
        logger.info(f"      Cluster {i}: {count:,} ({count/len(X)*100:.2f}%)")
    
    # Save models
    logger.info("\n3. Saving models...")
    joblib.dump(iso_forest, f"{MODELS_DIR}/isolation_forest.pkl")
    joblib.dump(kmeans, f"{MODELS_DIR}/kmeans.pkl")
    joblib.dump(scaler, f"{MODELS_DIR}/scaler.pkl")
    logger.info(f"   Saved to {MODELS_DIR}/")
    
    metrics = {
        'silhouette_score': silhouette,
        'calinski_harabasz_score': calinski,
        'davies_bouldin_score': davies,
        'anomaly_count': int(anomaly_count),
        'anomaly_percentage': float(anomaly_count/len(X)*100)
    }
    
    return anomaly_labels, cluster_labels, metrics, iso_forest, kmeans, scaler


def add_labels(df, anomaly_labels, cluster_labels):
    """Add labels to dataframe"""
    df['is_anomaly'] = anomaly_labels
    df['cluster'] = cluster_labels
    
    logger.info("\n--- LABELED DATA SUMMARY ---")
    logger.info(f"Anomalies: {df['is_anomaly'].sum():,}")
    logger.info(f"Normal: {(df['is_anomaly'] == 0).sum():,}")
    
    logger.info(f"\nCluster spending patterns:")
    for i in range(KMEANS_PARAMS['n_clusters']):
        cluster_df = df[df['cluster'] == i]
        if len(cluster_df) > 0:
            logger.info(f"\n  Cluster {i} ({len(cluster_df):,} transactions):")
            logger.info(f"    Avg amount: ₹{cluster_df['amount'].mean():,.2f}")
            logger.info(f"    Median: ₹{cluster_df['amount'].median():,.2f}")
            logger.info(f"    Top category: {cluster_df['category'].mode().iloc[0]}")
            if 'payment_mode' in cluster_df.columns:
                logger.info(f"    Top payment: {cluster_df['payment_mode'].mode().iloc[0]}")
    
    return df


def save_results(df, metrics, feature_cols):
    """Save all outputs"""
    logger.info("\n--- SAVING RESULTS ---")
    
    # Save labeled dataset
    df.to_csv(f"{OUTPUT_DIR}/labeled_dataset.csv", index=False)
    logger.info(f"Saved: {OUTPUT_DIR}/labeled_dataset.csv")
    
    # Save labels
    np.save(f"{OUTPUT_DIR}/anomaly_labels.npy", df['is_anomaly'].values)
    np.save(f"{OUTPUT_DIR}/cluster_labels.npy", df['cluster'].values)
    
    # Save training summary
    summary = {
        'total_transactions': len(df),
        'total_spend': float(df['amount'].sum()),
        'avg_transaction': float(df['amount'].mean()),
        'median_transaction': float(df['amount'].median()),
        'unique_categories': int(df['category'].nunique()),
        'unique_users': int(df['user_id'].nunique()),
        'date_range': {
            'start': str(df['date'].min()),
            'end': str(df['date'].max())
        },
        'cluster_distribution': df['cluster'].value_counts().to_dict(),
        'anomaly_count': int(df['is_anomaly'].sum()),
        'metrics': metrics,
        'features_used': feature_cols
    }
    
    with open(f"{OUTPUT_DIR}/training_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Saved: {OUTPUT_DIR}/training_summary.json")
    
    # Save results for API
    results = {
        'status': 'success',
        'summary': summary,
        'models': {
            'isolation_forest': ISOLATION_FOREST_PARAMS,
            'kmeans': KMEANS_PARAMS
        }
    }
    
    with open(f"{OUTPUT_DIR}/training_result.json", 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved: {OUTPUT_DIR}/training_result.json")
    
    return summary


def main():
    """Main execution"""
    logger.info("="*60)
    logger.info("PERSONAL FINANCE BEHAVIOR ANALYZER")
    logger.info("="*60)
    
    # 1. Load cleaned data
    df = load_data()
    
    # 2. Engineer features
    df = engineer_features(df)
    
    # 3. Prepare ML features
    X, feature_cols = prepare_ml_features(df)
    
    # 4. Train models
    anomaly_labels, cluster_labels, metrics, iso_forest, kmeans, scaler = train_models(X)
    
    # 5. Add labels
    df_labeled = add_labels(df, anomaly_labels, cluster_labels)
    
    # 6. Save results
    summary = save_results(df_labeled, metrics, feature_cols)
    
    logger.info("\n" + "="*60)
    logger.info("✅ TRAINING COMPLETE!")
    logger.info("="*60)
    logger.info(f"Outputs: {OUTPUT_DIR}/")
    logger.info(f"Models: {MODELS_DIR}/")
    
    return summary


if __name__ == "__main__":
    main()