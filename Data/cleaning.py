"""
Complete Data Cleaning Pipeline for Dataset 1
WITH OUTLIER REMOVAL
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================
# CONFIGURATION
# ============================================

INPUT_FILE = "data/cleaned_file.csv"
OUTPUT_FILE = "outputs/cleaned_dataset1.csv"

# Remove transactions above this amount (₹1,00,000 = 1 lakh)
MAX_AMOUNT = 100000

# Category fixes
CATEGORY_FIXES = {
    'Educaton': 'Education', 'education': 'Education', 'EDU': 'Education',
    'Rentt': 'Rent', 'Rnt': 'Rent', 'rent': 'Rent', 'RENT': 'Rent',
    'Utlities': 'Utilities', 'Utilties': 'Utilities', 'Utility': 'Utilities',
    'utilities': 'Utilities', 'Utilites': 'Utilities',
    'Entrtnmnt': 'Entertainment', 'Entertain': 'Entertainment',
    'entertainment': 'Entertainment',
    'Foodd': 'Food', 'Foods': 'Food', 'FOOD': 'Food', 'Fod': 'Food',
    'Helth': 'Health', 'HEALTH': 'Health', 'health': 'Health',
    'Traval': 'Travel', 'TRAVEL': 'Travel', 'travel': 'Travel', 'Travl': 'Travel',
    'Savings': 'Savings', 'SAVINGS': 'Savings', 'Saving': 'Savings',
    'Others': 'Other', 'Other': 'Other', 'Misc': 'Other', 'OTHERS': 'Other',
    'Utilties': 'Utilities',
}

PAYMENT_FIXES = {
    'Crd': 'Card', 'CRD': 'Card', 'CARD': 'Card', 'card': 'Card',
    'UPi': 'UPI', 'UPI': 'UPI', 'upi': 'UPI',
    'csh': 'Cash', 'Csh': 'Cash', 'CASH': 'Cash', 'cash': 'Cash',
    'Bank Transfr': 'Bank Transfer', 'BankTransfer': 'Bank Transfer',
    'Bank_Transfer': 'Bank Transfer', 'bank transfer': 'Bank Transfer',
}

LOCATION_FIXES = {
    'Ahm': 'Ahmedabad', 'Ahmd': 'Ahmedabad', 'AHMEDABAD': 'Ahmedabad',
    'Ban': 'Bangalore', 'Bangalore': 'Bangalore', 'BANGALORE': 'Bangalore',
    'Che': 'Chennai', 'Chennai': 'Chennai', 'CHENNAI': 'Chennai',
    'Del': 'Delhi', 'Delhi': 'Delhi', 'DELHI': 'Delhi', 'DEL': 'Delhi',
    'Hyd': 'Hyderabad', 'Hyderabad': 'Hyderabad', 'HYDERABAD': 'Hyderabad', 'HYD': 'Hyderabad',
    'Jai': 'Jaipur', 'Jaipur': 'Jaipur', 'JAIPUR': 'Jaipur', 'JAI': 'Jaipur',
    'Kol': 'Kolkata', 'Kolkata': 'Kolkata', 'KOLKATA': 'Kolkata', 'KOL': 'Kolkata',
    'Luc': 'Lucknow', 'Lucknow': 'Lucknow', 'LUCKNOW': 'Lucknow', 'LUC': 'Lucknow',
    'Mum': 'Mumbai', 'Mumbai': 'Mumbai', 'MUMBAI': 'Mumbai', 'MUM': 'Mumbai',
    'Pun': 'Pune', 'Pune': 'Pune', 'PUNE': 'Pune', 'PUN': 'Pune',
}


def clean_amount(amount_str):
    """Convert amount string to float"""
    if pd.isna(amount_str):
        return None
    
    amount_str = str(amount_str).strip()
    amount_str = re.sub(r'[₹$]', '', amount_str)
    amount_str = re.sub(r'^Rs\.', '', amount_str, flags=re.IGNORECASE)
    amount_str = amount_str.replace(',', '')
    amount_str = re.sub(r'[^\d.-]', '', amount_str)
    
    try:
        return float(amount_str)
    except ValueError:
        return None


def parse_date(date_str):
    """Parse date from various formats"""
    if pd.isna(date_str):
        return None
    
    date_str = str(date_str).strip()
    formats = ['%Y-%m-%d', '%d-%m-%y', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    try:
        return pd.to_datetime(date_str)
    except:
        return None


def clean_data():
    """Main cleaning function with outlier removal"""
    logger.info("="*70)
    logger.info("STARTING DATA CLEANING PIPELINE")
    logger.info("="*70)
    
    # 1. LOAD DATA
    logger.info("\n📂 Step 1: Loading data...")
    df = pd.read_csv(INPUT_FILE, encoding='utf-8')
    logger.info(f"   Loaded {len(df):,} rows")
    
    # 2. FILTER TRANSACTIONS
    logger.info("\n🔍 Step 2: Filtering expenses...")
    df = df[df['transaction_type'] == 'Expense'].copy()
    logger.info(f"   After filtering: {len(df):,} rows")
    
    # 3. CLEAN AMOUNTS
    logger.info("\n💰 Step 3: Cleaning amounts...")
    df['amount'] = df['amount'].apply(clean_amount)
    df = df.dropna(subset=['amount']).copy()
    df = df[df['amount'] >= 0].copy()
    logger.info(f"   After cleaning: {len(df):,} rows")
    
    # 4. REMOVE OUTLIERS - KEY FIX!
    logger.info(f"\n🚫 Step 4: Removing outliers above ₹{MAX_AMOUNT:,.0f}...")
    original_len = len(df)
    outlier_count = (df['amount'] > MAX_AMOUNT).sum()
    df = df[df['amount'] <= MAX_AMOUNT].copy()
    logger.info(f"   Removed {outlier_count:,} outlier transactions ({outlier_count/original_len*100:.2f}%)")
    logger.info(f"   New max amount: ₹{df['amount'].max():,.2f}")
    
    # 5. CLEAN DATES
    logger.info("\n📅 Step 5: Cleaning dates...")
    df['date'] = df['date'].apply(parse_date)
    df = df.dropna(subset=['date']).copy()
    logger.info(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    
    # Extract date components
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # 6. CLEAN CATEGORIES
    logger.info("\n🏷️ Step 6: Cleaning categories...")
    df['category'] = df['category'].str.strip().replace(CATEGORY_FIXES)
    df['category'] = df['category'].str.title()
    logger.info(f"   Unique categories: {df['category'].nunique()}")
    
    # 7. CLEAN PAYMENT MODE
    logger.info("\n💳 Step 7: Cleaning payment mode...")
    df['payment_mode'] = df['payment_mode'].str.strip().replace(PAYMENT_FIXES)
    df['payment_mode'] = df['payment_mode'].str.title()
    
    # 8. CLEAN LOCATION
    logger.info("\n📍 Step 8: Cleaning location...")
    df['location'] = df['location'].str.strip().str.title()
    df['location'] = df['location'].replace(LOCATION_FIXES)
    
    # 9. CLEAN NOTES
    logger.info("\n📝 Step 9: Cleaning notes...")
    df['notes'] = df['notes'].fillna('')
    df['notes'] = df['notes'].str.replace('...', '', regex=False)
    df['notes'] = df['notes'].str.replace('!!!', '', regex=False)
    df['notes'] = df['notes'].str.replace('xyz123', '', regex=False)
    df['notes'] = df['notes'].str.replace('asdfgh', '', regex=False)
    df['notes'] = df['notes'].str.strip()
    
    # 10. SAVE
    logger.info("\n💾 Step 10: Saving cleaned dataset...")
    df.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"   Saved: {OUTPUT_FILE}")
    logger.info(f"   Final rows: {len(df):,}")
    
    # 11. SUMMARY
    logger.info("\n" + "="*70)
    logger.info("CLEANING COMPLETE - SUMMARY")
    logger.info("="*70)
    logger.info(f"💰 Total spent: ₹{df['amount'].sum():,.2f}")
    logger.info(f"💰 Average transaction: ₹{df['amount'].mean():,.2f}")
    logger.info(f"💰 Median transaction: ₹{df['amount'].median():,.2f}")
    logger.info(f"💰 Max transaction: ₹{df['amount'].max():,.2f}")
    logger.info(f"👥 Unique users: {df['user_id'].nunique()}")
    logger.info(f"🏷️ Unique categories: {df['category'].nunique()}")
    logger.info(f"📅 Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    
    return df


if __name__ == "__main__":
    clean_data()
    print("\n✨ Now run train_models.py")