import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, List
from src.services.google_sheets_service import GoogleSheetsService
from src.models.transaction import Transaction
from config.config import Config

class DataService:
    """Service for managing transaction data operations"""
    
    def __init__(self):
        self.sheets_service = GoogleSheetsService()
        self._cache_buster = None
    
    @st.cache_data(ttl=Config.CACHE_TTL_MINUTES * 60)
    def load_data_cached(_self, cache_buster=None) -> pd.DataFrame:
        """Load data with caching"""
        try:
            data = _self.sheets_service.get_all_records()
            df = pd.DataFrame(data)
            
            if not df.empty:
                # Convert Date column to datetime
                df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                # Remove any rows with invalid dates
                df = df.dropna(subset=['Date'])
                # Reset index
                df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            return pd.DataFrame()
    
    def load_data(self) -> pd.DataFrame:
        """Load data with cache busting when new transactions are added"""
        return self.load_data_cached(self._cache_buster)
    
    def add_transaction(self, transaction: Transaction) -> tuple[bool, str]:
        """Add a new transaction"""
        try:
            if Config.get_debug_mode():
                st.write(f"🔍 Debug: Adding transaction - {transaction}")
            
            success, message = self.sheets_service.add_record(transaction.to_row())
            
            if success:
                # Update cache buster to force data reload
                self._cache_buster = datetime.now().isoformat()
                # Clear cached data
                self.load_data_cached.clear()
            
            return success, message
            
        except Exception as e:
            return False, f"Error adding transaction: {str(e)}"
    
    def check_duplicate_leave(self, df: pd.DataFrame, date: datetime, subcategory: str) -> bool:
        """Check if leave already exists for given date and person"""
        if df.empty:
            return False
        
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        selected_date = pd.to_datetime(date).date()
        
        duplicate = df[
            (df["Category"] == "Leave") &
            (df["Subcategory"] == subcategory) &
            (df["Date"].dt.date == selected_date)
        ]
        
        return not duplicate.empty
    
    def get_monthly_data(self, df: pd.DataFrame, year: int, months: List[int]) -> pd.DataFrame:
        """Filter data for specific months and year"""
        return df[(df["Date"].dt.month.isin(months)) & (df["Date"].dt.year == year)]
    
    def get_category_totals(self, df: pd.DataFrame) -> dict:
        """Calculate totals by category"""
        return {
            'income': df[df["Category"] == "Income"]["Amount (₹)"].sum(),
            'expense': df[df["Category"] == "Expense"]["Amount (₹)"].sum(),
            'investment': df[df["Category"] == "Investment"]["Amount (₹)"].sum(),
            'expense_shubham': df[(df["Category"] == "Expense") & (df["Paid by"] == "Shubham")]["Amount (₹)"].sum(),
            'expense_yashika': df[(df["Category"] == "Expense") & (df["Paid by"] == "Yashika")]["Amount (₹)"].sum(),
        }
    
    def get_monthly_trend(self, df: pd.DataFrame, category: str, months: int = 6) -> pd.DataFrame:
        """Get monthly trend data for a category"""
        today = datetime.today()
        start_month = today.month - months
        start_year = today.year
        if start_month <= 0:
            start_month += 12
            start_year -= 1

        # Get data from (start_year, start_month) onward
        df = df[df["Date"] >= datetime(start_year, start_month, 1)]
        df = df[df["Category"] == category]

        if df.empty:
            return pd.DataFrame()

        # Group by Year+Month and sum
        df["YearMonth"] = df["Date"].dt.to_period("M")
        trend_df = df.groupby("YearMonth")["Amount (₹)"].sum().reset_index()
        trend_df["YearMonth"] = trend_df["YearMonth"].astype(str)
        trend_df["YearMonth"] = trend_df["YearMonth"].apply(lambda x: pd.to_datetime(x).strftime("%b %Y"))

        return trend_df
    
    def get_leave_summary(self, df: pd.DataFrame, year: int, month: int) -> dict:
        """Get leave summary for a specific month"""
        leave_data = df[(df["Date"].dt.year == year) & 
                       (df["Date"].dt.month == month) & 
                       (df["Category"] == "Leave")]
        
        return {
            'maid_leaves': len(leave_data[leave_data["Subcategory"] == "Maid"]),
            'cook_leaves': len(leave_data[leave_data["Subcategory"] == "Cook"]),
            'leave_data': leave_data
        }
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.load_data_cached.clear()
        self._cache_buster = None