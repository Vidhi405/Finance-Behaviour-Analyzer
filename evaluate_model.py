"""
Model Evaluation for Personal Finance Behavior Analyzer
Evaluates trained models and generates performance metrics
"""

import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.cluster import KMeans
import joblib
import json
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================
# CONFIGURATION
# ============================================

MODELS_DIR = "models"
OUTPUT_DIR = "outputs"
DATA_FILE = "outputs/labeled_dataset.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_models():
    """Load trained models"""
    logger.info("Loading models...")
    
    iso_forest = joblib.load(f"{MODELS_DIR}/isolation_forest.pkl")
    kmeans = joblib.load(f"{MODELS_DIR}/kmeans.pkl")
    scaler = joblib.load(f"{MODELS_DIR}/scaler.pkl")
    
    logger.info("Models loaded successfully")
    return iso_forest, kmeans, scaler


def load_data():
    """Load labeled dataset"""
    logger.info(f"Loading data from {DATA_FILE}...")
    
    df = pd.read_csv(DATA_FILE, parse_dates=['date'])
    logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
    
    return df


def prepare_features(df):
    """Prepare feature matrix for evaluation (same as training)"""
    logger.info("Preparing features for evaluation...")
    
    # Numeric features used in training
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


def evaluate_isolation_forest(iso_forest, X, df):
    """Evaluate Isolation Forest performance"""
    logger.info("\n" + "="*50)
    logger.info("ISOLATION FOREST EVALUATION")
    logger.info("="*50)
    
    # Get predictions
    predictions = iso_forest.predict(X)
    anomaly_labels = (predictions == -1).astype(int)
    
    # Statistics
    anomaly_count = anomaly_labels.sum()
    anomaly_percentage = anomaly_count / len(anomaly_labels) * 100
    
    # Anomaly spending analysis
    anomaly_spend = df[anomaly_labels == 1]['amount'].sum()
    normal_spend = df[anomaly_labels == 0]['amount'].sum()
    avg_anomaly = df[anomaly_labels == 1]['amount'].mean()
    
    logger.info(f"Anomalies detected: {anomaly_count:,} ({anomaly_percentage:.2f}%)")
    logger.info(f"Anomaly total spend: ₹{anomaly_spend:,.2f}")
    logger.info(f"Normal total spend: ₹{normal_spend:,.2f}")
    logger.info(f"Average anomaly amount: ₹{avg_anomaly:,.2f}")
    
    # Anomaly by category
    anomaly_by_cat = df[anomaly_labels == 1]['category'].value_counts()
    logger.info("\nTop anomaly categories:")
    for cat, count in anomaly_by_cat.head(10).items():
        logger.info(f"  {cat}: {count} anomalies")
    
    # Anomaly by amount range
    logger.info("\nAnomaly by amount range:")
    ranges = [(0, 1000), (1000, 5000), (5000, 10000), (10000, 50000), (50000, float('inf'))]
    for low, high in ranges:
        count = ((df[anomaly_labels == 1]['amount'] >= low) & 
                 (df[anomaly_labels == 1]['amount'] < high)).sum()
        if high == float('inf'):
            logger.info(f"  ₹{low:,.0f}+: {count} anomalies")
        else:
            logger.info(f"  ₹{low:,.0f} - ₹{high:,.0f}: {count} anomalies")
    
    return {
        'anomaly_count': int(anomaly_count),
        'anomaly_percentage': anomaly_percentage,
        'anomaly_total_spend': float(anomaly_spend),
        'avg_anomaly': float(avg_anomaly),
        'top_anomaly_categories': anomaly_by_cat.head(10).to_dict()
    }


def evaluate_kmeans(kmeans, scaler, X, df):
    """Evaluate K-Means clustering"""
    logger.info("\n" + "="*50)
    logger.info("K-MEANS CLUSTERING EVALUATION")
    logger.info("="*50)
    
    # Scale and predict
    X_scaled = scaler.transform(X)
    cluster_labels = kmeans.predict(X_scaled)
    
    # Cluster metrics
    silhouette = silhouette_score(X_scaled, cluster_labels)
    calinski = calinski_harabasz_score(X_scaled, cluster_labels)
    davies = davies_bouldin_score(X_scaled, cluster_labels)
    
    logger.info(f"Silhouette Score: {silhouette:.4f}")
    logger.info(f"Calinski-Harabasz: {calinski:.2f}")
    logger.info(f"Davies-Bouldin: {davies:.4f}")
    
    # Interpretation
    logger.info("\nInterpretation:")
    if silhouette > 0.5:
        logger.info("  ✓ Good clustering - clusters are well-separated")
    elif silhouette > 0.3:
        logger.info("  ◐ Moderate clustering - some overlap between clusters")
    else:
        logger.info("  ✗ Poor clustering - clusters are not well-separated")
    
    if davies < 1.0:
        logger.info("  ✓ Good intra-cluster similarity")
    elif davies < 1.5:
        logger.info("  ◐ Moderate intra-cluster similarity")
    else:
        logger.info("  ✗ Poor intra-cluster similarity")
    
    # Cluster profiles
    logger.info("\nCluster Profiles:")
    for i in range(kmeans.n_clusters):
        cluster_df = df[cluster_labels == i]
        if len(cluster_df) > 0:
            logger.info(f"\n  Cluster {i} ({len(cluster_df):,} transactions):")
            logger.info(f"    Avg amount: ₹{cluster_df['amount'].mean():,.2f}")
            logger.info(f"    Median amount: ₹{cluster_df['amount'].median():,.2f}")
            logger.info(f"    Top category: {cluster_df['category'].mode().iloc[0]}")
            logger.info(f"    Top payment: {cluster_df['payment_mode'].mode().iloc[0] if 'payment_mode' in cluster_df.columns else 'N/A'}")
            logger.info(f"    % of total spend: {cluster_df['amount'].sum() / df['amount'].sum() * 100:.1f}%")
    
    return {
        'silhouette_score': silhouette,
        'calinski_harabasz_score': calinski,
        'davies_bouldin_score': davies,
        'n_clusters': kmeans.n_clusters,
        'interpretation': {
            'silhouette': 'good' if silhouette > 0.5 else 'moderate' if silhouette > 0.3 else 'poor',
            'davies': 'good' if davies < 1.0 else 'moderate' if davies < 1.5 else 'poor'
        }
    }


def evaluate_per_user(df):
    """Evaluate model performance per user"""
    logger.info("\n" + "="*50)
    logger.info("PER-USER EVALUATION")
    logger.info("="*50)
    
    user_results = []
    
    for user_id in df['user_id'].unique():
        user_df = df[df['user_id'] == user_id]
        user_results.append({
            'user_id': user_id,
            'transactions': int(len(user_df)),
            'total_spend': float(user_df['amount'].sum()),
            'avg_spend': float(user_df['amount'].mean()),
            'anomaly_count': int(user_df['is_anomaly'].sum()),
            'cluster': int(user_df['cluster'].mode().iloc[0]) if len(user_df) > 0 else None
        })
    
    user_df = pd.DataFrame(user_results)
    user_df.to_csv(f"{OUTPUT_DIR}/user_evaluation.csv", index=False)
    logger.info(f"Saved user evaluation to {OUTPUT_DIR}/user_evaluation.csv")
    
    logger.info(f"\nUser Summary:")
    logger.info(f"  Total users: {len(user_df):,}")
    logger.info(f"  Users with anomalies: {(user_df['anomaly_count'] > 0).sum():,}")
    logger.info(f"  Avg transactions per user: {user_df['transactions'].mean():.1f}")
    logger.info(f"  Avg spend per user: ₹{user_df['total_spend'].mean():,.2f}")
    
    return user_df


def find_optimal_clusters(X_scaled, max_k=10):
    """Find optimal number of clusters using elbow method"""
    logger.info("\n" + "="*50)
    logger.info("OPTIMAL CLUSTER ANALYSIS")
    logger.info("="*50)
    
    inertias = []
    silhouettes = []
    k_range = range(2, max_k + 1)
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        inertias.append(kmeans.inertia_)
        silhouettes.append(silhouette_score(X_scaled, labels))
        logger.info(f"  k={k}: inertia={kmeans.inertia_:,.0f}, silhouette={silhouettes[-1]:.4f}")
    
    # Find best k by silhouette score
    best_k = k_range[np.argmax(silhouettes)]
    
    logger.info(f"\nRecommended optimal k: {best_k}")
    logger.info(f"  (based on silhouette score)")
    
    return {
        'optimal_k': best_k,
        'inertias': inertias,
        'silhouettes': silhouettes,
        'k_range': list(k_range)
    }


def get_model_info():
    """Get model file sizes and info"""
    models_info = {}
    for model_file in ['isolation_forest.pkl', 'kmeans.pkl', 'scaler.pkl']:
        path = f"{MODELS_DIR}/{model_file}"
        if os.path.exists(path):
            size_kb = os.path.getsize(path) / 1024
            models_info[model_file] = f"{size_kb:.1f} KB"
    
    logger.info(f"\nModel sizes: {models_info}")
    return models_info


def generate_report(iso_results, kmeans_results, user_results, optimal_results, model_info):
    """Generate human-readable evaluation report"""
    
    report_lines = []
    report_lines.append("="*70)
    report_lines.append("MODEL EVALUATION REPORT")
    report_lines.append("="*70)
    report_lines.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Isolation Forest
    report_lines.append("ISOLATION FOREST (Anomaly Detection)")
    report_lines.append("-"*40)
    report_lines.append(f"  Anomalies detected: {iso_results['anomaly_count']:,}")
    report_lines.append(f"  Anomaly percentage: {iso_results['anomaly_percentage']:.2f}%")
    report_lines.append(f"  Anomaly total spend: ₹{iso_results['anomaly_total_spend']:,.2f}")
    report_lines.append(f"  Average anomaly: ₹{iso_results['avg_anomaly']:,.2f}")
    report_lines.append("")
    report_lines.append("  Top Anomaly Categories:")
    for cat, count in list(iso_results['top_anomaly_categories'].items())[:5]:
        report_lines.append(f"    - {cat}: {count} anomalies")
    report_lines.append("")
    
    # K-Means
    report_lines.append("K-MEANS (Behavioral Clustering)")
    report_lines.append("-"*40)
    report_lines.append(f"  Silhouette Score: {kmeans_results['silhouette_score']:.4f}")
    report_lines.append(f"  Calinski-Harabasz: {kmeans_results['calinski_harabasz_score']:.2f}")
    report_lines.append(f"  Davies-Bouldin: {kmeans_results['davies_bouldin_score']:.4f}")
    report_lines.append(f"  Interpretation: {kmeans_results['interpretation']}")
    report_lines.append("")
    
    # User Evaluation - FIXED
    report_lines.append("PER-USER EVALUATION")
    report_lines.append("-"*40)
    report_lines.append(f"  Total users: {len(user_results):,}")
    report_lines.append(f"  Users with anomalies: {(user_results['anomaly_count'] > 0).sum():,}")
    report_lines.append(f"  Avg transactions per user: {user_results['transactions'].mean():.1f}")
    report_lines.append(f"  Avg spend per user: ₹{user_results['total_spend'].mean():,.2f}")
    report_lines.append("")
    
    # Optimal Clusters
    report_lines.append("OPTIMAL CLUSTER ANALYSIS")
    report_lines.append("-"*40)
    report_lines.append(f"  Recommended k: {optimal_results['optimal_k']}")
    report_lines.append("")
    
    # Model Info
    report_lines.append("MODEL FILES")
    report_lines.append("-"*40)
    for name, size in model_info.items():
        report_lines.append(f"  {name}: {size}")
    report_lines.append("")
    
    report_lines.append("="*70)
    report_lines.append("END OF REPORT")
    report_lines.append("="*70)
    
    report_text = "\n".join(report_lines)
    
    with open(f"{OUTPUT_DIR}/evaluation_report.txt", 'w', encoding='utf-8') as f:
        f.write(report_text)
    logger.info(f"Saved: {OUTPUT_DIR}/evaluation_report.txt")
    
    print("\n" + report_text)


def save_evaluation_results(iso_results, kmeans_results, user_results, optimal_results, model_info):
    """Save evaluation results"""
    logger.info("\n--- SAVING EVALUATION RESULTS ---")
    
    results = {
        'isolation_forest': iso_results,
        'kmeans': kmeans_results,
        'user_evaluation': {
            'total_users': int(len(user_results)),
            'users_with_anomalies': int((user_results['anomaly_count'] > 0).sum()),
            'avg_transactions_per_user': float(user_results['transactions'].mean()),
            'avg_spend_per_user': float(user_results['total_spend'].mean())
        },
        'optimal_clusters': optimal_results,
        'model_info': model_info,
        'evaluation_timestamp': pd.Timestamp.now().isoformat()
    }
    
    with open(f"{OUTPUT_DIR}/evaluation_result.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved: {OUTPUT_DIR}/evaluation_result.json")
    
    # Generate human-readable report
    generate_report(iso_results, kmeans_results, user_results, optimal_results, model_info)


def main():
    """Main execution"""
    logger.info("="*60)
    logger.info("MODEL EVALUATION")
    logger.info("="*60)
    
    # Load models and data
    iso_forest, kmeans, scaler = load_models()
    df = load_data()
    X, feature_cols = prepare_features(df)
    
    # Evaluate Isolation Forest
    iso_results = evaluate_isolation_forest(iso_forest, X, df)
    
    # Evaluate K-Means
    kmeans_results = evaluate_kmeans(kmeans, scaler, X, df)
    
    # Per-user evaluation
    user_results = evaluate_per_user(df)
    
    # Find optimal clusters
    X_scaled = scaler.transform(X)
    optimal_results = find_optimal_clusters(X_scaled)
    
    # Get model info
    model_info = get_model_info()
    
    # Save results
    save_evaluation_results(iso_results, kmeans_results, user_results, optimal_results, model_info)
    
    logger.info("\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()