import os
from typing import Dict, List

class Config:
    """Configuration settings for the Finance Tracker application"""
    
    # App Configuration
    APP_TITLE = "💰 Finance Tracker"
    PAGE_LAYOUT = "centered"
    
    # Google Sheets Configuration
    SPREADSHEET_NAME = "MyFinanceTracker"
    WORKSHEET_NAME = "Tracker"
    
    # Required Google Sheets scopes
    GOOGLE_SHEETS_SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Cache Configuration
    CACHE_TTL_HOURS = 1  # 1 hour for resource cache
    CACHE_TTL_MINUTES = 5  # 5 minutes for data cache
    
    # Categories and Subcategories
    SUBCATEGORIES: Dict[str, List[str]] = {
        "Income": [
            "Salary", "Freelancing", "Business Income", "Rental Income", 
            "Interest/Dividends", "Bonus", "Gift", "Other Income"
        ],
        "Expense": [
            "Food & Dining", "Groceries", "Transportation", "Utilities", 
            "Rent/EMI", "Healthcare", "Entertainment", "Shopping", 
            "Education", "Insurance", "Travel", "Personal Care", "Other Expense"
        ],
        "Investment": [
            "Mutual Funds", "Stocks", "Fixed Deposits", "PPF", "EPF", 
            "Gold", "Real Estate", "Crypto", "Bonds", "Other Investment"
        ],
        "Other": [
            "Transfer", "Loan Given", "Loan Received", "Tax Payment", "Miscellaneous"
        ],
        "Leave": ["Maid", "Cook"]
    }
    
    # UI Configuration
    CATEGORY_COLORS = {
        "Income": "#28a745",
        "Expense": "#dc3545", 
        "Investment": "#c8b002",
        "Other": "#6c757d",
        "Leave": "#6366f1"
    }
    
    # Theme colors for different metric types
    METRIC_THEMES = {
        "income": {"bg": "#ecfdf5", "color": "#10b981", "border": "#10b981"},
        "expense": {"bg": "#fef2f2", "color": "#ef4444", "border": "#ef4444"},
        "investment": {"bg": "#fffbeb", "color": "#f59e0b", "border": "#f59e0b"},
        "balance": {"bg": "#eff6ff", "color": "#3b82f6", "border": "#3b82f6"}
    }
    
    # Calendar themes
    CALENDAR_THEMES = {
        "expense": {"bg": "#fffde6", "color": "#dc3545", "border": "#f5c6cb"},
        "income": {"bg": "#fffde6", "color": "#28a745", "border": "#c3e6cb"},
        "investment": {"bg": "#fffde6", "color": "#c8b002", "border": "#ffeaa7"}
    }
    
    @staticmethod
    def get_debug_mode() -> bool:
        """Get debug mode from environment variable"""
        return os.getenv("DEBUG_MODE", "False").lower() == "true"