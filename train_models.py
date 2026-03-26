"""
Enhanced Train Models with Better Clustering and Features
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
import logging
import json
import os
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

INPUT_FILE = "outputs/cleaned_dataset1_no_outliers.csv"
OUTPUT_DIR = "outputs"
MODELS_DIR = "models"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# ML Parameters
ISOLATION_FOREST_PARAMS = {
    'contamination': 0.02,
    'random_state': 42,
    'n_estimators': 100
}


def load_and_clean_data():
    """Load and prepare data"""
    logger.info("="*60)
    logger.info("LOADING DATA")
    logger.info("="*60)
    
    df = pd.read_csv(INPUT_FILE, parse_dates=['date'])
    logger.info(f"Loaded {len(df):,} rows")
    logger.info(f"Amount range: ₹{df['amount'].min():,.2f} - ₹{df['amount'].max():,.2f}")
    
    return df


def engineer_features(df):
    """Create enhanced features"""
    logger.info("\n--- ENGINEERING FEATURES ---")
    
    # Basic amount features
    df['amount_log'] = np.log1p(df['amount'])
    
    # Time features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Enhanced time features
    df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
    df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
    df['week_of_month'] = (df['date'].dt.day - 1) // 7 + 1
    
    # User behavior features
    df['user_transaction_count'] = df.groupby('user_id')['user_id'].transform('count')
    df['user_avg_amount'] = df.groupby('user_id')['amount'].transform('mean')
    
    # Days since last transaction
    df = df.sort_values(['user_id', 'date'])
    df['days_since_last'] = df.groupby('user_id')['date'].diff().dt.days.fillna(0)
    
    # Is above user average
    df['is_above_avg'] = (df['amount'] > df['user_avg_amount']).astype(int)
    
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
    
    logger.info(f"Added {len(cat_dummies.columns)} category features")
    logger.info(f"Added {len(dow_dummies.columns)} day-of-week features")
    logger.info(f"Added 6 enhanced features (user_avg, days_since, etc.)")
    
    return df


def prepare_features(df):
    """Prepare feature matrix"""
    feature_cols = ['amount_log', 'month', 'day_of_week', 'is_weekend',
                    'is_month_start', 'is_month_end', 'week_of_month',
                    'user_transaction_count', 'user_avg_amount', 
                    'days_since_last', 'is_above_avg']
    
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
    
    logger.info(f"Feature matrix: {X.shape[0]:,} rows, {X.shape[1]} features")
    
    return X, feature_cols


def find_optimal_clusters(X_scaled, max_k=10):
    """Find best number of clusters"""
    logger.info("\n🔍 Finding optimal clusters...")
    
    scores = []
    k_range = range(2, max_k + 1)
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        scores.append(score)
        logger.info(f"   k={k}: silhouette={score:.4f}")
    
    best_k = k_range[np.argmax(scores)]
    best_score = max(scores)
    
    logger.info(f"\n✅ Best k = {best_k} (silhouette={best_score:.4f})")
    
    # Plot
    plt.figure(figsize=(8, 4))
    plt.plot(k_range, scores, 'bo-')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Silhouette Score')
    plt.title('Optimal Cluster Selection')
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{OUTPUT_DIR}/optimal_clusters.png", dpi=150)
    plt.close()
    logger.info(f"   Saved: {OUTPUT_DIR}/optimal_clusters.png")
    
    return best_k


def train_models(X, df):
    """Train Isolation Forest and K-Means"""
    logger.info("\n" + "="*50)
    logger.info("TRAINING MODELS")
    logger.info("="*50)
    
    # 1. Isolation Forest
    logger.info("\n1. Isolation Forest (Anomaly Detection)...")
    iso_forest = IsolationForest(**ISOLATION_FOREST_PARAMS)
    anomaly_pred = iso_forest.fit_predict(X)
    anomaly_labels = (anomaly_pred == -1).astype(int)
    
    anomaly_count = anomaly_labels.sum()
    logger.info(f"   Anomalies: {anomaly_count:,} ({anomaly_count/len(X)*100:.2f}%)")
    
    # 2. K-Means with optimal clusters
    logger.info("\n2. K-Means (Behavioral Clustering)...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Find optimal k
    optimal_k = find_optimal_clusters(X_scaled)
    
    # Train with optimal k
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    silhouette = silhouette_score(X_scaled, cluster_labels)
    logger.info(f"\n   Silhouette Score: {silhouette:.4f}")
    
    logger.info(f"\n   Cluster distribution:")
    for i in range(optimal_k):
        count = (cluster_labels == i).sum()
        logger.info(f"      Cluster {i}: {count:,} ({count/len(X)*100:.1f}%)")
    
    # Save models
    logger.info("\n3. Saving models...")
    joblib.dump(iso_forest, f"{MODELS_DIR}/isolation_forest.pkl")
    joblib.dump(kmeans, f"{MODELS_DIR}/kmeans.pkl")
    joblib.dump(scaler, f"{MODELS_DIR}/scaler.pkl")
    logger.info(f"   Saved to {MODELS_DIR}/")
    
    metrics = {
        'silhouette_score': silhouette,
        'anomaly_count': int(anomaly_count),
        'anomaly_percentage': float(anomaly_count/len(X)*100),
        'optimal_clusters': optimal_k
    }
    
    return anomaly_labels, cluster_labels, metrics, iso_forest, kmeans, scaler


def add_cluster_names(df):
    """Add human-readable cluster names"""
    cluster_names = {}
    
    for i in range(df['cluster'].nunique()):
        cluster_df = df[df['cluster'] == i]
        
        if len(cluster_df) == 0:
            continue
        
        top_cat = cluster_df['category'].mode().iloc[0]
        top_payment = cluster_df['payment_mode'].mode().iloc[0] if 'payment_mode' in cluster_df.columns else "Mixed"
        avg_spend = cluster_df['amount'].mean()
        
        # Create descriptive name
        if avg_spend > 10000:
            spend_type = "High Spender"
        elif avg_spend > 5000:
            spend_type = "Medium Spender"
        else:
            spend_type = "Low Spender"
        
        cluster_names[i] = f"{spend_type} - {top_payment} User ({top_cat} Lover)"
    
    df['cluster_name'] = df['cluster'].map(cluster_names)
    
    logger.info("\n📊 Cluster Descriptions:")
    for i, name in cluster_names.items():
        count = (df['cluster'] == i).sum()
        logger.info(f"   Cluster {i}: {name} ({count} users)")
    
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
    
    # Save feature columns
    with open(f"{MODELS_DIR}/feature_columns.json", 'w') as f:
        json.dump(feature_cols, f, indent=2)
    logger.info(f"Saved: {MODELS_DIR}/feature_columns.json")
    
    # Save summary
    summary = {
        'total_transactions': len(df),
        'total_spend': float(df['amount'].sum()),
        'avg_transaction': float(df['amount'].mean()),
        'median_transaction': float(df['amount'].median()),
        'unique_categories': int(df['category'].nunique()),
        'unique_users': int(df['user_id'].nunique()),
        'cluster_distribution': df['cluster'].value_counts().to_dict(),
        'cluster_names': {int(k): v for k, v in df.groupby('cluster')['cluster_name'].first().to_dict().items()},
        'anomaly_count': int(df['is_anomaly'].sum()),
        'metrics': metrics,
        'features_used': feature_cols
    }
    
    with open(f"{OUTPUT_DIR}/training_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Saved: {OUTPUT_DIR}/training_summary.json")
    
    return summary


def main():
    """Main execution"""
    logger.info("="*60)
    logger.info("ENHANCED TRAINING PIPELINE")
    logger.info("="*60)
    
    # 1. Load data
    df = load_and_clean_data()
    
    # 2. Engineer features
    df = engineer_features(df)
    
    # 3. Prepare ML features
    X, feature_cols = prepare_features(df)
    
    # 4. Train models
    anomaly_labels, cluster_labels, metrics, iso_forest, kmeans, scaler = train_models(X, df)
    
    # 5. Add labels
    df['is_anomaly'] = anomaly_labels
    df['cluster'] = cluster_labels
    
    # 6. Add cluster names
    df = add_cluster_names(df)
    
    # 7. Save results
    summary = save_results(df, metrics, feature_cols)
    
    logger.info("\n" + "="*60)
    logger.info("✅ ENHANCED TRAINING COMPLETE!")
    logger.info("="*60)
    logger.info(f"   Optimal clusters: {metrics['optimal_clusters']}")
    logger.info(f"   Silhouette score: {metrics['silhouette_score']:.4f}")
    logger.info(f"   Anomalies: {metrics['anomaly_count']:,} ({metrics['anomaly_percentage']:.1f}%)")
    
    return summary


if __name__ == "__main__":
    main()