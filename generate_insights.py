"""
Generate Enhanced Insights and Visualizations from Labeled Dataset
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

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")


def load_data():
    """Load labeled dataset"""
    logger.info(f"Loading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE, parse_dates=['date'])
    logger.info(f"Loaded {len(df):,} rows")
    return df


def get_monthly_comparison(df):
    """Compare current month vs previous month"""
    current_month = df['date'].dt.month.max()
    prev_month = current_month - 1 if current_month > 1 else 12
    
    current_data = df[df['date'].dt.month == current_month]
    prev_data = df[df['date'].dt.month == prev_month]
    
    current_total = current_data['amount'].sum()
    prev_total = prev_data['amount'].sum()
    
    change = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
    
    return {
        'current_month': int(current_month),
        'previous_month': int(prev_month),
        'current_total': float(current_total),
        'previous_total': float(prev_total),
        'change_percent': float(change),
        'trend': 'up' if change > 0 else 'down'
    }


def get_peak_times(df):
    """Find when user spends the most"""
    daily = df.groupby('day_of_week')['amount'].sum().sort_values(ascending=False)
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    peak_days = {day_names[int(d)]: float(amt) for d, amt in daily.head(3).items()}
    
    return {'peak_days': peak_days}


def get_savings_opportunities(df):
    """Find potential savings areas"""
    opportunities = []
    
    # High frequency low-value transactions
    low_value = df[df['amount'] < 500]
    if len(low_value) > 50:
        opportunities.append({
            'type': 'small_transactions',
            'count': int(len(low_value)),
            'total': float(low_value['amount'].sum()),
            'suggestion': f"Consolidate {len(low_value)} small purchases to save mental energy"
        })
    
    # Category with highest average spend
    high_avg = df.groupby('category')['amount'].mean().sort_values(ascending=False).head(1)
    for cat, avg in high_avg.items():
        if avg > 10000:
            opportunities.append({
                'type': 'high_avg_category',
                'category': cat,
                'avg_amount': float(avg),
                'suggestion': f"Your {cat} transactions average ₹{avg:,.0f}. Look for cheaper alternatives"
            })
    
    # Weekend vs weekday
    weekend_avg = df[df['is_weekend'] == 1]['amount'].mean()
    weekday_avg = df[df['is_weekend'] == 0]['amount'].mean()
    if weekend_avg > weekday_avg * 1.3 and weekend_avg > 0:
        opportunities.append({
            'type': 'weekend_spending',
            'weekend_avg': float(weekend_avg),
            'weekday_avg': float(weekday_avg),
            'suggestion': f"You spend {int((weekend_avg/weekday_avg - 1)*100)}% more on weekends. Plan ahead!"
        })
    
    return opportunities


def get_spending_alerts(df):
    """Generate alerts for unusual spending"""
    alerts = []
    
    monthly_avg = df.groupby('category')['amount'].mean()
    current_month = df[df['date'].dt.month == df['date'].dt.month.max()]
    
    for cat in monthly_avg.index:
        cat_current = current_month[current_month['category'] == cat]['amount'].sum()
        cat_avg = monthly_avg[cat]
        
        if cat_current > cat_avg * 2 and cat_avg > 0:
            alerts.append({
                'type': 'category_spike',
                'category': cat,
                'current': float(cat_current),
                'average': float(cat_avg),
                'increase': f"{int((cat_current/cat_avg - 1)*100)}%"
            })
    
    return alerts


def get_spending_insights(df):
    """Generate all spending insights"""
    logger.info("\n--- GENERATING SPENDING INSIGHTS ---")
    
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
        },
        # NEW INSIGHTS
        'monthly_comparison': get_monthly_comparison(df),
        'peak_times': get_peak_times(df),
        'savings_opportunities': get_savings_opportunities(df),
        'spending_alerts': get_spending_alerts(df)
    }
    
    # Cluster insights
    for i in sorted(df['cluster'].unique()):
        cluster_df = df[df['cluster'] == i]
        insights[f'cluster_{i}'] = {
            'size': int(len(cluster_df)),
            'total_spend': float(cluster_df['amount'].sum()),
            'avg_transaction': float(cluster_df['amount'].mean()),
            'top_category': cluster_df['category'].mode().iloc[0] if len(cluster_df) > 0 else None,
            'cluster_name': cluster_df['cluster_name'].iloc[0] if 'cluster_name' in cluster_df.columns else f"Cluster {i}",
            'top_5_categories': cluster_df['category'].value_counts().head(5).to_dict()
        }
    
    return insights


def create_enhanced_visualizations(df):
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
    
    # 2. Monthly Comparison
    fig, ax = plt.subplots(figsize=(10, 5))
    mc = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
    ax.plot(range(len(mc)), mc.values, marker='o', linewidth=2, color='steelblue')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Spending (₹)')
    ax.set_title('Monthly Spending Trend')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{VIZ_DIR}/2_monthly_trend.png", dpi=150)
    plt.close()
    logger.info("   Saved: 2_monthly_trend.png")
    
    # 3. Cluster Distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    cluster_counts = df['cluster'].value_counts().sort_index()
    axes[0].pie(cluster_counts.values, labels=[f'Cluster {i}' for i in cluster_counts.index], 
                autopct='%1.1f%%', startangle=90)
    axes[0].set_title('Cluster Distribution')
    cluster_avg = df.groupby('cluster')['amount'].mean()
    colors = plt.cm.Set3(range(len(cluster_avg)))
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
    
    # 4. Weekly Pattern Heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    pivot = pd.crosstab(df['day_of_week'], df['category'], values=df['amount'], aggfunc='mean').fillna(0)
    day_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot.index = [day_labels[i] if i < len(day_labels) else i for i in pivot.index]
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax)
    ax.set_title('Average Spending by Day and Category (₹)')
    plt.tight_layout()
    plt.savefig(f"{VIZ_DIR}/4_heatmap_day_category.png", dpi=150)
    plt.close()
    logger.info("   Saved: 4_heatmap_day_category.png")
    
    # 5. Anomaly Detection Scatter
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
    plt.savefig(f"{VIZ_DIR}/5_anomaly_detection.png", dpi=150)
    plt.close()
    logger.info("   Saved: 5_anomaly_detection.png")
    
    logger.info(f"\nAll visualizations saved to: {VIZ_DIR}/")


def generate_enhanced_report(df, insights):
    """Generate enhanced human-readable report"""
    logger.info("\n--- GENERATING REPORT ---")
    
    report_lines = []
    report_lines.append("="*70)
    report_lines.append("PERSONAL FINANCE BEHAVIOR ANALYZER - ENHANCED INSIGHTS REPORT")
    report_lines.append("="*70)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Overview
    report_lines.append("1. OVERVIEW")
    report_lines.append("-"*40)
    report_lines.append(f"   Total Transactions: {insights['summary']['total_transactions']:,}")
    report_lines.append(f"   Total Spending: ₹{insights['summary']['total_spend']:,.2f}")
    report_lines.append(f"   Average Transaction: ₹{insights['summary']['avg_transaction']:,.2f}")
    report_lines.append(f"   Median Transaction: ₹{insights['summary']['median_transaction']:,.2f}")
    report_lines.append("")
    
    # Monthly Comparison
    mc = insights['monthly_comparison']
    report_lines.append("2. MONTHLY COMPARISON")
    report_lines.append("-"*40)
    report_lines.append(f"   Current Month: Month {mc['current_month']} - ₹{mc['current_total']:,.2f}")
    report_lines.append(f"   Previous Month: Month {mc['previous_month']} - ₹{mc['previous_total']:,.2f}")
    report_lines.append(f"   Change: {mc['change_percent']:.1f}% ({mc['trend']})")
    report_lines.append("")
    
    # Top Categories
    report_lines.append("3. TOP SPENDING CATEGORIES")
    report_lines.append("-"*40)
    cat_data = pd.DataFrame(insights['category_breakdown'])
    cat_data = cat_data.sort_values('sum', ascending=False).head(10)
    for cat, row in cat_data.iterrows():
        report_lines.append(f"   {cat}: ₹{row['sum']:,.2f} ({int(row['count']):,} transactions, Avg: ₹{row['mean']:,.2f})")
    report_lines.append("")
    
    # Anomalies
    report_lines.append("4. ANOMALY INSIGHTS")
    report_lines.append("-"*40)
    report_lines.append(f"   Anomalies Detected: {insights['anomaly_insights']['anomaly_count']:,}")
    report_lines.append(f"   Total Anomaly Spending: ₹{insights['anomaly_insights']['anomaly_total']:,.2f}")
    report_lines.append(f"   Average Anomaly: ₹{insights['anomaly_insights']['avg_anomaly']:,.2f}")
    report_lines.append("   Top Anomaly Categories:")
    for cat, count in insights['anomaly_insights']['top_anomaly_categories'].items():
        report_lines.append(f"      - {cat}: {count} transactions")
    report_lines.append("")
    
    # Alerts
    if insights['spending_alerts']:
        report_lines.append("5. SPENDING ALERTS")
        report_lines.append("-"*40)
        for alert in insights['spending_alerts']:
            report_lines.append(f"   ⚠️ {alert['category']} spending up {alert['increase']} this month!")
            report_lines.append(f"      Current: ₹{alert['current']:,.2f} vs Avg: ₹{alert['average']:,.2f}")
        report_lines.append("")
    
    # Savings Opportunities
    if insights['savings_opportunities']:
        report_lines.append("6. SAVINGS OPPORTUNITIES")
        report_lines.append("-"*40)
        for opp in insights['savings_opportunities']:
            report_lines.append(f"   💡 {opp['suggestion']}")
        report_lines.append("")
    
    # Peak Times
    pt = insights['peak_times']
    report_lines.append("7. PEAK SPENDING TIMES")
    report_lines.append("-"*40)
    for day, amount in pt['peak_days'].items():
        report_lines.append(f"   {day}: ₹{amount:,.2f}")
    report_lines.append("")
    
    # Clusters
    report_lines.append("8. BEHAVIORAL CLUSTERS")
    report_lines.append("-"*40)
    for i in range(len([k for k in insights.keys() if k.startswith('cluster_')])):
        cluster_key = f'cluster_{i}'
        if cluster_key in insights:
            rep = insights[cluster_key]
            report_lines.append(f"   Cluster {i}: {rep['cluster_name']}")
            report_lines.append(f"      Size: {rep['size']:,} transactions")
            report_lines.append(f"      Total Spend: ₹{rep['total_spend']:,.2f}")
            report_lines.append(f"      Avg Transaction: ₹{rep['avg_transaction']:,.2f}")
    report_lines.append("")
    
    report_lines.append("="*70)
    report_lines.append("END OF REPORT")
    report_lines.append("="*70)
    
    report_text = "\n".join(report_lines)
    
    with open(f"{OUTPUT_DIR}/enhanced_insights_report.txt", 'w', encoding='utf-8') as f:
        f.write(report_text)
    logger.info(f"Saved: {OUTPUT_DIR}/enhanced_insights_report.txt")
    
    with open(f"{OUTPUT_DIR}/enhanced_insights_result.json", 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved: {OUTPUT_DIR}/enhanced_insights_result.json")
    
    print("\n" + report_text)


def main():
    """Main execution"""
    logger.info("="*60)
    logger.info("ENHANCED INSIGHTS GENERATION")
    logger.info("="*60)
    
    df = load_data()
    insights = get_spending_insights(df)
    create_enhanced_visualizations(df)
    generate_enhanced_report(df, insights)
    
    logger.info("\n✅ Enhanced insights generation complete!")


if __name__ == "__main__":
    main()