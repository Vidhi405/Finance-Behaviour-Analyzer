"""
Model Evaluation for Personal Finance Behavior Analyzer
"""

import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler
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
    logger.info("Loading data...")
    df = pd.read_csv(f"{OUTPUT_DIR}/labeled_dataset.csv", parse_dates=['date'])
    logger.info(f"Loaded {len(df):,} rows")
    return df


def prepare_features(df):
    """Prepare features for evaluation"""
    logger.info("Preparing features...")
    
    feature_cols = [col for col in df.columns if col not in [
        'date', 'transaction_id', 'user_id', 'notes', 'is_anomaly', 'cluster'
    ]]
    
    # Filter to numeric and dummy columns
    feature_cols = [col for col in feature_cols if col not in [
        'transaction_type', 'category', 'payment_mode', 'location', 'source'
    ]]
    
    X = df[feature_cols].fillna(0)
    logger.info(f"Feature matrix: {X.shape}")
    
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
    
    logger.info(f"Anomalies detected: {anomaly_count:,} ({anomaly_percentage:.2f}%)")
    logger.info(f"Anomaly total spend: ₹{anomaly_spend:,.2f}")
    logger.info(f"Normal total spend: ₹{normal_spend:,.2f}")
    
    # Anomaly by category
    anomaly_by_cat = df[anomaly_labels == 1]['category'].value_counts().head(10)
    logger.info("\nTop anomaly categories:")
    for cat, count in anomaly_by_cat.items():
        logger.info(f"  {cat}: {count} anomalies")
    
    # Anomaly by amount range
    logger.info("\nAnomaly by amount range:")
    ranges = [(0, 1000), (1000, 5000), (5000, 10000), (10000, 50000), (50000, float('inf'))]
    for low, high in ranges:
        count = ((df[anomaly_labels == 1]['amount'] >= low) & 
                 (df[anomaly_labels == 1]['amount'] < high)).sum()
        logger.info(f"  ₹{low:,.0f} - ₹{high:,.0f}: {count} anomalies")
    
    return {
        'anomaly_count': int(anomaly_count),
        'anomaly_percentage': anomaly_percentage,
        'anomaly_total_spend': float(anomaly_spend),
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