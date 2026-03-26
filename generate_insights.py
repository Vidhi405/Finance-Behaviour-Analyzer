"""
Generate Insights and Visualizations from Labeled Dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================
# CONFIGURATION
# ============================================

INPUT_FILE = "outputs/labeled_dataset.csv"
OUTPUT_DIR = "outputs"
VIZ_DIR = f"{OUTPUT_DIR}/visualizations"

os.makedirs(VIZ_DIR, exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")


def load_data():
    """Load labeled dataset"""
    logger.info(f"Loading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE, parse_dates=['date'])
    logger.info(f"Loaded {len(df):,} rows")
    return df


def get_spending_insights(df):
    """Generate spending insights"""
    logger.info("\n--- GENERATING SPENDING INSIGHTS ---")
    
    # Convert Period to string for JSON serialization
    monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
    
    insights = {
        'summary': {
            'total_transactions': int(len(df)),
            'total_spend': float(df['amount'].sum()),
            'avg_transaction': float(df['amount'].mean()),
            'median_transaction': float(df['amount'].median()),
            'max_transaction': float(df['amount'].max()),
            'min_transaction': float(df['amount'].min())
        },
        'category_breakdown': df.groupby('category')['amount'].agg(['sum', 'mean', 'count']).to_dict(),
        'monthly_trend': {str(k): float(v) for k, v in monthly.to_dict().items()},
        'weekly_pattern': {str(k): float(v) for k, v in df.groupby('day_of_week')['amount'].mean().to_dict().items()},
        'anomaly_insights': {
            'anomaly_count': int(df['is_anomaly'].sum()),
            'anomaly_total': float(df[df['is_anomaly'] == 1]['amount'].sum()),
            'avg_anomaly': float(df[df['is_anomaly'] == 1]['amount'].mean()),
            'top_anomaly_categories': df[df['is_anomaly'] == 1]['category'].value_counts().head(5).to_dict()
        }
    }
    
    # Cluster insights
    for i in sorted(df['cluster'].unique()):
        cluster_df = df[df['cluster'] == i]
        insights[f'cluster_{i}'] = {
            'size': int(len(cluster_df)),
            'total_spend': float(cluster_df['amount'].sum()),
            'avg_transaction': float(cluster_df['amount'].mean()),
            'top_category': cluster_df['category'].mode().iloc[0] if len(cluster_df) > 0 else None,
            'top_5_categories': cluster_df['category'].value_counts().head(5).to_dict()
        }
    
    return insights


def create_visualizations(df):
    """Create all visualizations"""
    logger.info("\n--- CREATING VISUALIZATIONS ---")
    
    # 1. Spending by Category
    fig, ax = plt.subplots(figsize=(12, 6))
    category_spend = df.groupby('category')['amount'].sum().sort_values(ascending=False).head(10)
    bars = ax.bar(range(len(category_spend)), category_spend.values, color='skyblue')
    ax.set_xticks(range(len(category_spend)))
    ax.set_xticklabels(category_spend.index, rotation=45, ha='right')
    ax.set_xlabel('Category')
    ax.set_ylabel('Total Spending (₹)')
    ax.set_title('Top 10 Spending Categories')
    for bar, val in zip(bars, category_spend.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                f'₹{val/1000:.0f}k', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(f"{VIZ_DIR}/1_spending_by_category.png", dpi=150)
    plt.close()
    logger.info("   Saved: 1_spending_by_category.png")
    
    # 2. Anomaly Detection
    fig, ax = plt.subplots(figsize=(12, 5))
    normal = df[df['is_anomaly'] == 0]['amount'].sample(min(5000, len(df[df['is_anomaly'] == 0])))
    anomalies = df[df['is_anomaly'] == 1]['amount']
    ax.scatter(range(len(normal)), normal, alpha=0.5, s=10, label='Normal', color='green')
    ax.scatter(range(len(anomalies)), anomalies, alpha=0.7, s=30, label='Anomaly', color='red')
    ax.set_xlabel('Transaction Index')
    ax.set_ylabel('Amount (₹)')
    ax.set_title(f'Anomaly Detection ({len(anomalies)} anomalies detected)')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{VIZ_DIR}/2_anomaly_detection.png", dpi=150)
    plt.close()
    logger.info("   Saved: 2_anomaly_detection.png")
    
    # 3. Cluster Distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    cluster_counts = df['cluster'].value_counts().sort_index()
    axes[0].pie(cluster_counts.values, labels=[f'Cluster {i}' for i in cluster_counts.index], 
                autopct='%1.1f%%', startangle=90)
    axes[0].set_title('Cluster Distribution')
    
    cluster_avg = df.groupby('cluster')['amount'].mean()
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12'][:len(cluster_avg)]
    axes[1].bar(range(len(cluster_avg)), cluster_avg.values, color=colors)
    axes[1].set_xticks(range(len(cluster_avg)))
    axes[1].set_xticklabels([f'Cluster {i}' for i in cluster_avg.index])
    axes[1].set_xlabel('Cluster')
    axes[1].set_ylabel('Average Amount (₹)')
    axes[1].set_title('Average Transaction by Cluster')
    for i, val in enumerate(cluster_avg.values):
        axes[1].text(i, val, f'₹{val:,.0f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f"{VIZ_DIR}/3_cluster_distribution.png", dpi=150)
    plt.close()
    logger.info("   Saved: 3_cluster_distribution.png")
    
    # 4. Amount Distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].hist(df['amount'], bins=50, edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('Amount (₹)')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Transaction Amount Distribution')
    axes[0].axvline(df['amount'].mean(), color='red', linestyle='--', label=f'Mean: ₹{df["amount"].mean():,.0f}')
    axes[0].axvline(df['amount'].median(), color='green', linestyle='--', label=f'Median: ₹{df["amount"].median():,.0f}')
    axes[0].legend()
    
    cluster_data = [df[df['cluster'] == i]['amount'] for i in sorted(df['cluster'].unique())]
    axes[1].boxplot(cluster_data, tick_labels=[f'Cluster {i}' for i in sorted(df['cluster'].unique())])
    axes[1].set_xlabel('Cluster')
    axes[1].set_ylabel('Amount (₹)')
    axes[1].set_title('Amount Distribution by Cluster')
    
    plt.tight_layout()
    plt.savefig(f"{VIZ_DIR}/4_amount_distribution.png", dpi=150)
    plt.close()
    logger.info("   Saved: 4_amount_distribution.png")
    
    # 5. Spending Trend Over Time
    fig, ax = plt.subplots(figsize=(14, 6))
    daily_spend = df.groupby(df['date'].dt.date)['amount'].sum()
    ax.plot(range(len(daily_spend)), daily_spend.values, linewidth=1, color='steelblue')
    ax.set_xlabel('Days')
    ax.set_ylabel('Daily Spending (₹)')
    ax.set_title('Daily Spending Trend')
    
    ma = daily_spend.rolling(window=7, min_periods=1).mean()
    ax.plot(range(len(ma)), ma.values, color='red', linewidth=2, label='7-day Moving Average')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f"{VIZ_DIR}/5_spending_trend.png", dpi=150)
    plt.close()
    logger.info("   Saved: 5_spending_trend.png")
    
    # 6. Heatmap: Day of Week vs Category
    fig, ax = plt.subplots(figsize=(14, 8))
    pivot = pd.crosstab(df['day_of_week'], df['category'], values=df['amount'], aggfunc='mean').fillna(0)
    day_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot.index = [day_labels[i] if i < len(day_labels) else i for i in pivot.index]
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax)
    ax.set_title('Average Spending by Day and Category (₹)')
    plt.tight_layout()
    plt.savefig(f"{VIZ_DIR}/6_heatmap_day_category.png", dpi=150)
    plt.close()
    logger.info("   Saved: 6_heatmap_day_category.png")
    
    # 7. Cluster Profiles
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for i, cluster in enumerate(sorted(df['cluster'].unique())):
        if i >= 4:
            break
        cluster_df = df[df['cluster'] == cluster]
        top_cats = cluster_df['category'].value_counts().head(5)
        axes[i].barh(range(len(top_cats)), top_cats.values, color='coral')
        axes[i].set_yticks(range(len(top_cats)))
        axes[i].set_yticklabels(top_cats.index)
        axes[i].set_xlabel('Transaction Count')
        axes[i].set_title(f'Cluster {cluster}: {len(cluster_df):,} transactions')
    
    plt.tight_layout()
    plt.savefig(f"{VIZ_DIR}/7_cluster_profiles.png", dpi=150)
    plt.close()
    logger.info("   Saved: 7_cluster_profiles.png")
    
    logger.info(f"\nAll visualizations saved to: {VIZ_DIR}/")


def generate_report(df, insights):
    """Generate human-readable report"""
    logger.info("\n--- GENERATING REPORT ---")
    
    report_lines = []
    report_lines.append("="*70)
    report_lines.append("PERSONAL FINANCE BEHAVIOR ANALYZER - INSIGHTS REPORT")
    report_lines.append("="*70)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Summary
    report_lines.append("1. OVERVIEW")
    report_lines.append("-"*40)
    report_lines.append(f"   Total Transactions: {insights['summary']['total_transactions']:,}")
    report_lines.append(f"   Total Spending: Rs.{insights['summary']['total_spend']:,.2f}")
    report_lines.append(f"   Average Transaction: Rs.{insights['summary']['avg_transaction']:,.2f}")
    report_lines.append(f"   Median Transaction: Rs.{insights['summary']['median_transaction']:,.2f}")
    report_lines.append(f"   Max Transaction: Rs.{insights['summary']['max_transaction']:,.2f}")
    report_lines.append(f"   Min Transaction: Rs.{insights['summary']['min_transaction']:,.2f}")
    report_lines.append("")
    
    # Top Categories
    report_lines.append("2. TOP SPENDING CATEGORIES")
    report_lines.append("-"*40)
    cat_data = pd.DataFrame(insights['category_breakdown'])
    cat_data = cat_data.sort_values('sum', ascending=False).head(10)
    for cat, row in cat_data.iterrows():
        report_lines.append(f"   {cat}: Rs.{row['sum']:,.2f} ({int(row['count']):,} transactions, Avg: Rs.{row['mean']:,.2f})")
    report_lines.append("")
    
    # Anomalies
    report_lines.append("3. ANOMALY INSIGHTS")
    report_lines.append("-"*40)
    report_lines.append(f"   Anomalies Detected: {insights['anomaly_insights']['anomaly_count']:,}")
    report_lines.append(f"   Total Anomaly Spending: Rs.{insights['anomaly_insights']['anomaly_total']:,.2f}")
    report_lines.append(f"   Average Anomaly: Rs.{insights['anomaly_insights']['avg_anomaly']:,.2f}")
    report_lines.append("   Top Anomaly Categories:")
    for cat, count in insights['anomaly_insights']['top_anomaly_categories'].items():
        report_lines.append(f"      - {cat}: {count} transactions")
    report_lines.append("")
    
    # Clusters
    report_lines.append("4. BEHAVIORAL CLUSTERS")
    report_lines.append("-"*40)
    for i in range(4):
        cluster_key = f'cluster_{i}'
        if cluster_key in insights:
            rep = insights[cluster_key]
            report_lines.append(f"   Cluster {i}: {rep['size']:,} transactions")
            report_lines.append(f"      Total Spend: Rs.{rep['total_spend']:,.2f}")
            report_lines.append(f"      Avg Transaction: Rs.{rep['avg_transaction']:,.2f}")
            report_lines.append(f"      Top Category: {rep['top_category']}")
    report_lines.append("")
    
    # Weekly Pattern
    report_lines.append("5. WEEKLY SPENDING PATTERN")
    report_lines.append("-"*40)
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i, amount in sorted(insights['weekly_pattern'].items()):
        day = day_names[int(i)] if int(i) < len(day_names) else i
        report_lines.append(f"   {day}: Rs.{amount:,.2f}")
    report_lines.append("")
    
    # Monthly Trend (Top 6 months)
    report_lines.append("6. MONTHLY SPENDING TREND (Top 6 months)")
    report_lines.append("-"*40)
    monthly = pd.Series(insights['monthly_trend']).sort_values(ascending=False).head(6)
    for month, amount in monthly.items():
        report_lines.append(f"   {month}: Rs.{amount:,.2f}")
    report_lines.append("")
    
    # Payment Mode Distribution
    if 'payment_mode' in df.columns:
        report_lines.append("7. PAYMENT MODE DISTRIBUTION")
        report_lines.append("-"*40)
        pmt_dist = df['payment_mode'].value_counts()
        for mode, count in pmt_dist.items():
            pct = count / len(df) * 100
            report_lines.append(f"   {mode}: {count:,} transactions ({pct:.1f}%)")
        report_lines.append("")
    
    report_lines.append("="*70)
    report_lines.append("END OF REPORT")
    report_lines.append("="*70)
    
    report_text = "\n".join(report_lines)
    
    # Save with UTF-8 encoding
    with open(f"{OUTPUT_DIR}/insights_report.txt", 'w', encoding='utf-8') as f:
        f.write(report_text)
    logger.info(f"Saved: {OUTPUT_DIR}/insights_report.txt")
    
    # Save insights as JSON with UTF-8
    with open(f"{OUTPUT_DIR}/insights_result.json", 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved: {OUTPUT_DIR}/insights_result.json")
    
    print("\n" + report_text)


def main():
    """Main execution"""
    logger.info("="*60)
    logger.info("GENERATING INSIGHTS & VISUALIZATIONS")
    logger.info("="*60)
    
    # Load data
    df = load_data()
    
    # Generate insights
    insights = get_spending_insights(df)
    
    # Create visualizations
    create_visualizations(df)
    
    # Generate report
    generate_report(df, insights)
    
    logger.info("\n✅ Insights generation complete!")
    logger.info(f"   Visualizations: {VIZ_DIR}/")
    logger.info(f"   Report: {OUTPUT_DIR}/insights_report.txt")
    logger.info(f"   JSON: {OUTPUT_DIR}/insights_result.json")


if __name__ == "__main__":
    main()