import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import json
from google.oauth2.service_account import Credentials
import calendar
import openpyxl
import time

# MUST BE FIRST - Set page config
st.set_page_config(page_title="💰 Finance Tracker", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
/* Hide Streamlit UI elements */
#MainMenu, footer, header, [data-testid="stToolbarActions"] {
    visibility: hidden !important;
    height: 0px !important;
}

/* REMOVE ALL TOP SPACING */
section.main > div { 
    padding-top: 0rem !important;
}
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 1rem !important;
}

/* Tighten the h1 title itself */
h1 {
    text-align: center !important;
    margin-top: 0rem !important;
    margin-bottom: 0.8rem !important;
    font-size: 1.6rem !important;
}

/* Optional: control mobile view */
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
}
</style>
""", unsafe_allow_html=True)


# Unified CSS: Hide UI, center title, reduce top spacing, and mobile tweaks
custom_css = """
<style>
    /* Hide Streamlit UI elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbarActions"] { display: none !important; }
    header { visibility: hidden; }

    /* Reduce top padding globally */
    .main .block-container {
        padding-top: 0.1rem !important;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
        max-width: 100%;
    }

    /* Center and shrink h1 title */
    h1 {
        text-align: center !important;
        margin-top: 0rem !important;
        margin-bottom: 0.8rem !important;
        font-size: 1.6rem !important;
    }

    /* Custom grid layout for metrics */
    .custom-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr !important;
        gap: 0.5rem !important;
        margin: 1rem 0 !important;
    }

    .custom-metric {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 2px solid #e0e0e0;
        padding: 0.8rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .custom-metric .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
        color: #6c757d;
    }

    .custom-metric .metric-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #333;
    }

    .metric-income { 
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #a7f3d0 100%) !important;
        border: 0px solid #10b981 !important;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.15) !important;
    }
    .metric-expense { 
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 50%, #fecaca 100%) !important;
        border: 0px solid #ef4444 !important;
        box-shadow: 0 2px 10px rgba(239, 68, 68, 0.15) !important;
    }
    .metric-investment { 
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 50%, #fde68a 100%) !important;
        border: 0px solid #f59e0b !important;
        box-shadow: 0 2px 10px rgba(245, 158, 11, 0.15) !important;
    }
    .metric-balance { 
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 50%, #93c5fd 100%) !important;
        border: 0px solid #3b82f6 !important;
        box-shadow: 0 2px 10px rgba(59, 130, 246, 0.15) !important;
    }
    .recent-entry {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.25rem 0;
        font-size: 0.85rem;
    }

    .entry-date { font-weight: 600; color: #495057; }
    .entry-category { font-weight: 500; }
    .entry-amount { font-weight: 700; float: right; }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container { padding: 0.5rem 0.25rem !important; }
        .custom-grid { gap: 0.25rem !important; }
        .custom-metric { padding: 0.6rem; min-height: 70px; }
        .custom-metric .metric-value { font-size: 1rem; }
    }

    /* Font sizes for headings */
    h2 { font-size: 1.2rem !important; margin: 0.3rem 0 !important; }
    h3 { font-size: 1.0rem !important; margin: 0.25rem 0 !important; }

    /* Input label font sizes */
    .stSelectbox label, .stDateInput label, .stTextInput label, .stNumberInput label {
        font-size: 1.0rem !important;
    }

    /* Tab font sizes */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.9rem !important;
    }

    /* Button styling */
    .stButton button {
        font-size: 0.85rem !important;
    }

    /* Calendar specific styles for different categories */
    .calendar-expense .calendar-day .expense-amount {
        background: #ffe6e6 !important;
        color: #dc3545 !important;
        border: 1px solid #f5c6cb !important;
    }
    
    .calendar-income .calendar-day .income-amount {
        background: #e6ffe6 !important;
        color: #28a745 !important;
        border: 1px solid #c3e6cb !important;
    }
    
    .calendar-investment .calendar-day .investment-amount {
        background: #fffde6 !important;
        color: #c8b002 !important;
        border: 1px solid #ffeaa7 !important;
    }
    
    /* Calendar container spacing */
    .calendar-section {
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 12px;
        border: 1px solid #e9ecef;
    }
    
    .calendar-section h4 {
        margin-bottom: 0.8rem !important;
        color: #495057;
        font-size: 1.1rem !important;
    }

    /* Evenly distribute tabs horizontally */
    /* Distribute tab names evenly */
    .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        justify-content: space-evenly !important;
    }

    /* Style individual tab items */
    .stTabs [data-baseweb="tab"] {
        flex-grow: 1 !important;
        text-align: center !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 0.25rem !important;
    }


    /* Custom grid layout for leave */
    .leave-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 0.5rem !important;
        margin: 1rem 0 !important;
    }


</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Debug mode toggle
DEBUG_MODE = False

# Initialize session state for cache invalidation
if 'last_transaction_time' not in st.session_state:
    st.session_state.last_transaction_time = None

# Connect to Google Sheets with proper error handling and caching
@st.cache_resource(ttl=3600)  # Cache for 1 hour
def get_gsheet_connection():
    try:
        # Define the required scope
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        # Get credentials from secrets
        creds_dict = st.secrets["gcp_service_account"]
        
        if DEBUG_MODE:
            st.write("🔍 Debug: Credentials loaded from secrets")

        # Create Credentials object using google-auth (compatible method)
        creds = Credentials.from_service_account_info(
            creds_dict, 
            scopes=scope
        )

        # Use gc (gspread client) with proper authorization
        gc = gspread.authorize(creds)
        
        if DEBUG_MODE:
            st.write("🔍 Debug: Google Sheets client authorized successfully")
            
        return gc
        
    except KeyError as e:
        st.error(f"❌ Missing secret key: {str(e)}. Please check your secrets configuration.")
        if DEBUG_MODE:
            st.write("🔍 Debug: Available secrets:", list(st.secrets.keys()))
        return None
    except Exception as e:
        st.error(f"❌ Error connecting to Google Sheets: {str(e)}")
        if DEBUG_MODE:
            st.write(f"🔍 Debug: Full error: {type(e).__name__}: {str(e)}")
        return None

# Subcategories
SUBCATEGORIES = {
    "Income": ["Salary", "Freelancing", "Business Income", "Rental Income", "Interest/Dividends", "Bonus", "Gift", "Other Income"],
    "Expense": ["Food & Dining", "Groceries", "Transportation", "Utilities", "Rent/EMI", "Healthcare", "Entertainment", "Shopping", "Education", "Insurance", "Travel", "Personal Care", "Other Expense"],
    "Investment": ["Mutual Funds", "Stocks", "Fixed Deposits", "PPF", "EPF", "Gold", "Real Estate", "Crypto", "Bonds", "Other Investment"],
    "Other": ["Transfer", "Loan Given", "Loan Received", "Tax Payment", "Miscellaneous"],
    "Leave": ["Maid", "Cook"]
}

# Custom metric component
def create_custom_metric_card(label, value, metric_type):
    return f"""
    <div class="custom-metric metric-{metric_type}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

# Get fresh worksheet connection (not cached to avoid auth issues)
def get_worksheet():
    """Get a fresh worksheet connection every time"""
    try:
        client = get_gsheet_connection()
        if client is None:
            return None
            
        # Try to open the spreadsheet
        sheet = client.open("MyFinanceTracker")
        ws = sheet.worksheet("Tracker")
        
        if DEBUG_MODE:
            st.write("🔍 Debug: Successfully connected to spreadsheet and worksheet")
        
        return ws
        
    except gspread.SpreadsheetNotFound:
        st.error("❌ Spreadsheet 'MyFinanceTracker' not found. Please check the name and sharing permissions.")
        return None
    except gspread.WorksheetNotFound:
        st.error("❌ Worksheet 'Tracker' not found. Please check the worksheet name.")
        return None
    except Exception as e:
        st.error(f"❌ Error accessing worksheet: {str(e)}")
        if DEBUG_MODE:
            st.write(f"🔍 Debug: Full worksheet error: {type(e).__name__}: {str(e)}")
        return None

# Load data with smart caching that respects transaction additions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data_cached(cache_buster=None):
    """Load data with cache busting parameter"""
    try:
        ws = get_worksheet()
        if ws is None:
            return pd.DataFrame()
            
        # Get all records
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        
        if DEBUG_MODE:
            st.write(f"🔍 Debug: Loaded {len(df)} records from sheet")
        
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
        if DEBUG_MODE:
            st.write(f"🔍 Debug: Full load error: {type(e).__name__}: {str(e)}")
        return pd.DataFrame()

def load_data():
    """Load data with cache busting when new transactions are added"""
    cache_buster = st.session_state.last_transaction_time
    return load_data_cached(cache_buster)

# Helper function to format numbers with K/M abbreviations
def format_amount(value):
    if value >= 1000000:
        return f"₹{value/1000000:.1f}M"
    elif value >= 100000:
        return f"₹{value/100000:.1f}L"
    elif value >= 1000:
        return f"₹{value/1000:.1f}K"
    else:
        return f"₹{value:.0f}"


# Updated create_calendar_view function
def create_calendar_view(df, selected_year, selected_month, category_filter=None, calendar_theme="expense"):
    """Create a category-filtered calendar view showing daily amounts"""
    import calendar
    
    # Filter data for selected month/year and category
    month_data = df[(df["Date"].dt.year == selected_year) & 
                   (df["Date"].dt.month == selected_month)]
    
    if category_filter:
        month_data = month_data[month_data["Category"] == category_filter]
    
    # Group by date and calculate daily totals
    daily_summary = month_data.groupby(month_data["Date"].dt.day)["Amount (₹)"].sum()

    calendar.setfirstweekday(calendar.SUNDAY)

    # Get calendar layout
    cal = calendar.monthcalendar(selected_year, selected_month)
    month_name = calendar.month_name[selected_month]
    
    # Theme-based styling
    theme_colors = {
        "expense": {"bg": "#fffde6", "color": "#dc3545", "border": "#f5c6cb"},
        "income": {"bg": "#fffde6", "color": "#28a745", "border": "#c3e6cb"},
        "investment": {"bg": "#fffde6", "color": "#c8b002", "border": "#ffeaa7"}
    }
    
    theme = theme_colors.get(calendar_theme, theme_colors["expense"])
    
    # Create HTML calendar
    calendar_html = f"""
    <style>
    .calendar-container-{calendar_theme} {{
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 0 auto;
        max-width: 100%;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        overflow: hidden;
    }}
    
    .calendar-header-{calendar_theme} {{
        background: linear-gradient(135deg, {theme["color"]} 0%, {theme["color"]}dd 100%);
        color: white;
        text-align: center;
        padding: 0.8rem;
        font-size: 0.95rem;
        font-weight: 600;
    }}
    
    .calendar-grid-{calendar_theme} {{
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 1px;
        background: #e9ecef;
    }}
    
    .day-header-{calendar_theme} {{
        background: #f8f9fa;
        padding: 0.4rem 0.2rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.75rem;
        color: #6c757d;
        border-bottom: 1px solid #dee2e6;
    }}
    
    .calendar-day-{calendar_theme} {{
        background: white;
        min-height: 70px;
        padding: 0.25rem;
        display: flex;
        flex-direction: column;
        position: relative;
        border: 1px solid #f0f0f0;
    }}
    
    .calendar-day-{calendar_theme}.other-month {{
        background: #f8f9fa;
        color: #adb5bd;
    }}
    
    .calendar-day-{calendar_theme}.today {{
        background: #fff3cd;
        border: 2px solid #ffc107;
    }}
    
    .day-number-{calendar_theme} {{
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.2rem;
        color: #495057;
    }}
    
    .amount-{calendar_theme} {{
        font-size: 0.65rem;
        font-weight: 600;
        color: {theme["color"]};
        background: {theme["bg"]};
        padding: 0.1rem 0.25rem;
        border-radius: 6px;
        margin: 0.05rem 0;
        text-align: center;
        border: 1px solid {theme["border"]};
    }}
    
    @media (max-width: 768px) {{
        .calendar-day-{calendar_theme} {{
            min-height: 60px;
            padding: 0.2rem;
        }}
        .day-number-{calendar_theme} {{
            font-size: 0.75rem;
        }}
        .amount-{calendar_theme} {{
            font-size: 0.6rem;
            padding: 0.05rem 0.2rem;
        }}
    }}
    </style>
    
    <div class="calendar-container-{calendar_theme}">
        <div class="calendar-header-{calendar_theme}">
            {month_name} {selected_year} - Daily {category_filter if category_filter else 'Totals'}
        </div>
        <div class="calendar-grid-{calendar_theme}">
            <!-- Day headers -->
            <div class="day-header-{calendar_theme}">Sun</div>
            <div class="day-header-{calendar_theme}">Mon</div>
            <div class="day-header-{calendar_theme}">Tue</div>
            <div class="day-header-{calendar_theme}">Wed</div>
            <div class="day-header-{calendar_theme}">Thu</div>
            <div class="day-header-{calendar_theme}">Fri</div>
            <div class="day-header-{calendar_theme}">Sat</div>
    """
    
    # Get today's date for highlighting
    today = datetime.today()
    is_current_month = (today.year == selected_year and today.month == selected_month)
    
    # Generate calendar days
    for week in cal:
        for day in week:
            if day == 0:
                calendar_html += f'<div class="calendar-day-{calendar_theme} other-month"></div>'
            else:
                # Check if this is today
                is_today = is_current_month and day == today.day
                today_class = " today" if is_today else ""
                
                calendar_html += f'<div class="calendar-day-{calendar_theme}{today_class}">'
                calendar_html += f'<div class="day-number-{calendar_theme}">{day}</div>'
                
                # Add transaction amount for this day
                if day in daily_summary.index:
                    amount = daily_summary[day]
                    if amount > 0:
                        formatted_amount = format_amount(amount)
                        calendar_html += f'<div class="amount-{calendar_theme}">{formatted_amount}</div>'

                calendar_html += '</div>'
    
    calendar_html += """
        </div>
    </div>
    """
    
    return calendar_html


def create_Leave_calendar_view(df, selected_year, selected_month):
    """Create a calendar view showing Leave for both maid and cook"""
    import calendar
    
    # Filter data for selected month/year and Leave category
    month_data = df[(df["Date"].dt.year == selected_year) & 
                   (df["Date"].dt.month == selected_month) & 
                   (df["Category"] == "Leave")]
    
    # Group by date and person
    daily_Leave = {}
    for _, row in month_data.iterrows():
        day = row["Date"].day
        person = row["Subcategory"]
        if day not in daily_Leave:
            daily_Leave[day] = []
        daily_Leave[day].append(person)

    calendar.setfirstweekday(calendar.SUNDAY)
    
    # Get calendar layout
    cal = calendar.monthcalendar(selected_year, selected_month)
    month_name = calendar.month_name[selected_month]
    
    # Create HTML calendar
    calendar_html = f"""
    <style>
    .Leave-calendar-container {{
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 0 auto;
        max-width: 100%;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        overflow: hidden;
    }}
    
    .Leave-calendar-header {{
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        text-align: center;
        padding: 0.8rem;
        font-size: 0.95rem;
        font-weight: 600;
    }}
    
    .Leave-calendar-grid {{
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 1px;
        background: #e9ecef;
    }}
    
    .Leave-day-header {{
        background: #f8f9fa;
        padding: 0.4rem 0.2rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.75rem;
        color: #6c757d;
        border-bottom: 1px solid #dee2e6;
    }}
    
    .Leave-calendar-day {{
        background: white;
        min-height: 70px;
        padding: 0.25rem;
        display: flex;
        flex-direction: column;
        position: relative;
        border: 1px solid #f0f0f0;
    }}
    
    .Leave-calendar-day.other-month {{
        background: #f8f9fa;
        color: #adb5bd;
    }}
    
    .Leave-calendar-day.today {{
        background: #fff3cd;
        border: 2px solid #ffc107;
    }}
    
    .Leave-day-number {{
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.2rem;
        color: #495057;
    }}
    
    .leave-indicator {{
        font-size: 0.6rem;
        font-weight: 600;
        padding: 0.1rem 0.25rem;
        border-radius: 6px;
        margin: 0.05rem 0;
        text-align: center;
        border: 1px solid;
    }}
    
    .leave-maid {{
        background: #fce4ec;
        color: #e91e63;
        border-color: #f8bbd9;
    }}
    
    .leave-cook {{
        background: #e3f2fd;
        color: #2196f3;
        border-color: #bbdefb;
    }}
    
    @media (max-width: 768px) {{
        .Leave-calendar-day {{
            min-height: 60px;
            padding: 0.2rem;
        }}
        .Leave-day-number {{
            font-size: 0.75rem;
        }}
        .leave-indicator {{
            font-size: 0.55rem;
            padding: 0.05rem 0.2rem;
        }}
    }}
    </style>
    
    <div class="Leave-calendar-container">
        <div class="Leave-calendar-header">
            {month_name} {selected_year} - Leave Calendar
        </div>
        <div class="Leave-calendar-grid">
            <!-- Day headers -->
            <div class="Leave-day-header">Sun</div>
            <div class="Leave-day-header">Mon</div>
            <div class="Leave-day-header">Tue</div>
            <div class="Leave-day-header">Wed</div>
            <div class="Leave-day-header">Thu</div>
            <div class="Leave-day-header">Fri</div>
            <div class="Leave-day-header">Sat</div>
    """
    
    # Get today's date for highlighting
    today = datetime.today()
    is_current_month = (today.year == selected_year and today.month == selected_month)
    
    # Generate calendar days
    for week in cal:
        for day in week:
            if day == 0:
                calendar_html += f'<div class="Leave-calendar-day other-month"></div>'
            else:
                # Check if this is today
                is_today = is_current_month and day == today.day
                today_class = " today" if is_today else ""
                
                calendar_html += f'<div class="Leave-calendar-day{today_class}">'
                calendar_html += f'<div class="Leave-day-number">{day}</div>'
                
                # Add leave indicators for this day
                if day in daily_Leave:
                    for person in daily_Leave[day]:
                        if person == "Maid":
                            calendar_html += f'<div class="leave-indicator leave-maid">Maid</div>'
                        elif person == "Cook":
                            calendar_html += f'<div class="leave-indicator leave-cook">Cook</div>'

                calendar_html += '</div>'
    
    calendar_html += """
        </div>
    </div>
    """
    
    return calendar_html


def get_monthly_trend(df, category, months=6):
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


# Function to add transaction with fresh connection
def add_transaction(date, category, subcategory, description, amount):
    try:
        if DEBUG_MODE:
            st.write(f"🔍 Debug: Attempting to add transaction - Date: {date}, Category: {category}, Amount: {amount}")
        
        # Get a fresh worksheet connection for write operations
        ws = get_worksheet()
        if ws is None:
            return False, "Could not connect to worksheet"
        
        # Convert date to string format
        date_str = date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date)
        
        # Prepare the row data
        new_row = [date_str, category, subcategory, description.strip().title(), float(amount), paid_by]
        
        if DEBUG_MODE:
            st.write(f"🔍 Debug: Row data prepared: {new_row}")
        
        # Try to add the row to the sheet with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if DEBUG_MODE:
                    st.write(f"🔍 Debug: Attempt {attempt + 1} to add row...")
                
                result = ws.append_row(new_row, value_input_option='USER_ENTERED')
                
                if DEBUG_MODE:
                    st.write(f"🔍 Debug: Sheet response: {result}")
                
                # Update cache buster to force data reload
                st.session_state.last_transaction_time = datetime.now().isoformat()
                
                return True, "Transaction added successfully!"
                
            except Exception as retry_error:
                if DEBUG_MODE:
                    st.write(f"🔍 Debug: Attempt {attempt + 1} failed: {str(retry_error)}")
                
                if attempt == max_retries - 1:
                    # Last attempt failed, raise the error
                    raise retry_error
                
                # Wait a bit before retrying
                import time
                time.sleep(1)
        
    except gspread.exceptions.APIError as e:
        error_msg = f"Google Sheets API Error: {str(e)}"
        if DEBUG_MODE:
            st.write(f"🔍 Debug API Error: {error_msg}")
        return False, error_msg
    except ValueError as e:
        error_msg = f"Value Error (check amount format): {str(e)}"
        if DEBUG_MODE:
            st.write(f"🔍 Debug Value Error: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if DEBUG_MODE:
            st.write(f"🔍 Debug Unexpected Error: {type(e).__name__}: {error_msg}")
        return False, error_msg

# Add debug information at the top
if DEBUG_MODE:
    st.sidebar.header("🔧 Debug Information")
    
    # Check secrets
    try:
        secrets_available = "gcp_service_account" in st.secrets
        st.sidebar.write(f"Secrets available: {secrets_available}")
        if secrets_available:
            creds_keys = list(st.secrets["gcp_service_account"].keys())
            st.sidebar.write(f"Credential keys: {creds_keys}")
    except Exception as e:
        st.sidebar.write(f"Error checking secrets: {e}")
    
    # Show cache info
    st.sidebar.write(f"Last transaction: {st.session_state.last_transaction_time}")

st.title("💸 Daily Tracker")

# Load data
df = load_data()

# Check if we have any data or connection issues
if df.empty:
    # Try to get worksheet to check connection
    test_ws = get_worksheet()
    if test_ws is None:
        st.error("❌ Could not connect to Google Sheets. Please check your credentials and sheet permissions.")
        st.info("💡 Common issues:\n- Check if 'MyFinanceTracker' spreadsheet exists\n- Verify the service account has edit permissions\n- Ensure 'Tracker' worksheet exists\n- Check your secrets configuration")
        st.stop()

# Initialize session state for form reset
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

# Initialize session state for form data
if 'form_category' not in st.session_state:
    st.session_state.form_category = "Expense"

# CREATE TABS HERE
tab1, tab2, tab3 = st.tabs(["📝 Transactions", "📊 Summary", "🏠 Leave"])


# -------------------------
# TAB 1: ADD TRANSACTION
# -------------------------
with tab1:
    st.header("📝 Add New Transaction")
    
    # Form inputs OUTSIDE the form to enable dynamic updates
# Form inputs OUTSIDE the form to enable dynamic updates
    col1, col2 = st.columns(2)
    date = col1.date_input("Date", datetime.today(), key=f"date_{st.session_state.form_key}")

    # Category selection with callback to update subcategories
    category = col2.selectbox(
        "Category", 
        ["Expense", "Income", "Investment", "Other", "Leave"],
        index=["Expense", "Income", "Investment", "Other", "Leave"].index(st.session_state.form_category),
        key=f"category_select_{st.session_state.form_key}"
    )

    # Update session state when category changes
    if category != st.session_state.form_category:
        st.session_state.form_category = category

    # Dynamic subcategory based on selected category
    subcategory_options = SUBCATEGORIES.get(category, [])
    subcategory = st.selectbox("Subcategory", subcategory_options, key=f"subcategory_{st.session_state.form_key}")

    if category != "Leave":
        description = st.text_input("Description", placeholder="Enter transaction description", key=f"description_{st.session_state.form_key}")
        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.0f", step=1.0, key=f"amount_{st.session_state.form_key}")
        paid_by = st.selectbox("Paid By", ["Shubham", "Yashika"], key=f"paidby_{st.session_state.form_key}")

    else:
        description = ""
        amount = 0.0

    
    # Add validation display
    if DEBUG_MODE:
        st.write("🔍 **Current Form Values:**")
        st.write(f"- Date: {date}")
        st.write(f"- Category: {category}")
        st.write(f"- Subcategory: {subcategory}")
        st.write(f"- Description: '{description}'")
        st.write(f"- Amount: {amount}")
    
    # Submit button outside form for immediate response
    if st.button("💾 Add Transaction", use_container_width=True):
        errors = []

        if category != "Leave":
            if amount <= 0:
                errors.append("Amount must be greater than 0")
            if not description.strip():
                errors.append("Description cannot be empty")
        if not subcategory:
            errors.append("Please select a subcategory")

        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Handle duplicate leave logic
            selected_date = pd.to_datetime(date).date()
            if category == "Leave":
                df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

                duplicate = df[
                    (df["Category"] == "Leave") &
                    (df["Subcategory"] == subcategory) &
                    (df["Date"].dt.date == selected_date)
                ]

                if not duplicate.empty:
                    st.error(f"❌ Leave already recorded for {subcategory} on {selected_date.strftime('%d %b %Y')}")
                    # st.stop()
                    time.sleep(3)
                    st.rerun()

            # Add transaction
            success, message = add_transaction(date, category, subcategory, description.strip(), amount)

            if success:
                load_data_cached.clear()
                st.success("✅ Transaction successfully recorded!")
                st.balloons()
                import time
                time.sleep(2)
                st.session_state.form_key += 1
                st.session_state.form_category = "Expense"
                st.rerun()
            else:
                st.error("❌ " + message)

                
                # Additional troubleshooting info
                st.info("💡 **Troubleshooting Tips:**\n"
                       "- Check if the Google Sheet is accessible\n"
                       "- Verify the service account has edit permissions\n"
                       "- Try refreshing the page\n"
                       "- Check your internet connection")
    
    # Show recent transactions in the add transaction tab for reference
    if not df.empty:
        st.markdown("---")
        st.subheader("🕒 Last 5 Transactions")
        
        # Get last 5 rows from the dataframe (most recent entries by index)
        recent_df = df[df["Category"] != "Leave"].tail(5).iloc[::-1]  # Get last 5 and reverse order to show newest first
        
        for _, row in recent_df.iterrows():
            date_str = row["Date"].strftime("%d %b")
            category_color = {"Income": "#28a745", "Expense": "#dc3545", "Investment": "#c8b002", "Other": "#6c757d"}
            color = category_color.get(row["Category"], "#6c757d")
            
            st.markdown(f"""
            <div class="recent-entry">
                <span class="entry-date">{date_str}</span> | 
                <span class="entry-category" style="color: {color};">{row["Category"]}</span> - {row["Subcategory"]}
                <span class="entry-amount" style="color: {color};">₹{row["Amount (₹)"]:,.0f}</span>
                <br><small style="color: black;">{row["Description"]}</small>
            </div>
            """, unsafe_allow_html=True)


    # Download section
    st.markdown("---")
    # st.subheader("📥 Download Data")

    if not df.empty:
        # Convert datetime to string for Excel compatibility
        df_download = df.copy()
        df_download["Date"] = df_download["Date"].dt.strftime("%Y-%m-%d")
        
        # Convert to Excel bytes
        from io import BytesIO
        excel_buffer = BytesIO()
        df_download.to_excel(excel_buffer, index=False, sheet_name="Finance_Data")
        excel_buffer.seek(0)
        
        # Download button
        st.download_button(
            label="📊 Download as Excel",
            data=excel_buffer.getvalue(),
            file_name=f"finance_tracker_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxlsx",
            use_container_width=True
        )
    else:
        st.info("No data available to download")
# -------------------------
# TAB 2: SUMMARY & ANALYTICS
# -------------------------
with tab2:
    # -------------------------
    # Monthly Summary Cards
    # -------------------------
    st.header("📊 Monthly Summary")

    if not df.empty:
        # Month and Year selection with multi-select option
        col1, col2, col3 = st.columns(3)
        
        with col1:
            available_years = sorted(df["Date"].dt.year.unique(), reverse=True)
            default_year = datetime.now().year if datetime.now().year in available_years else available_years[0]
            selected_year = st.selectbox("Year", available_years, index=available_years.index(default_year))
        
        with col2:
            # Get months available for the selected year
            year_data = df[df["Date"].dt.year == selected_year]
            available_months = sorted(year_data["Date"].dt.month.unique())
            month_names = [(month, datetime(2000, month, 1).strftime('%B')) for month in available_months]
            
            # Set default to current month if available
            current_month = datetime.now().month
            default_months = [current_month] if current_month in available_months and selected_year == datetime.now().year else [available_months[0]] if available_months else []
            
            selected_month_names = st.multiselect(
                "Month(s)", 
                options=[name for _, name in month_names],
                default=[datetime(2000, month, 1).strftime('%B') for month in default_months],
                help="Select one or multiple months"
            )
            
            # Convert back to month numbers
            selected_months = [month for month, name in month_names if name in selected_month_names]
        
        with col3:
            st.write("")  # Spacer
            st.write("")  # Spacer
            analysis_period = f"{', '.join(selected_month_names)} {selected_year}" if selected_month_names else "No months selected"
        
        if selected_months:
            # Filter for selected months and year
            selected_period_df = df[(df["Date"].dt.month.isin(selected_months)) & (df["Date"].dt.year == selected_year)]
            
            # Calculate totals for selected period
            total_income = selected_period_df[selected_period_df["Category"] == "Income"]["Amount (₹)"].sum()
            total_expense = selected_period_df[selected_period_df["Category"] == "Expense"]["Amount (₹)"].sum()
            total_expense_shubham = selected_period_df[(selected_period_df["Category"] == "Expense") & (selected_period_df["Paid by"] == "Shubham")]["Amount (₹)"].sum()
            total_expense_yashika = selected_period_df[(selected_period_df["Category"] == "Expense") & (selected_period_df["Paid by"] == "Yashika")]["Amount (₹)"].sum()
            total_investment = selected_period_df[selected_period_df["Category"] == "Investment"]["Amount (₹)"].sum()
            total_investment_alltime = df[df["Category"] == "Investment"]["Amount (₹)"].sum()
            net_savings = total_income - total_expense - total_investment
            
            # Display selected period
            st.subheader(f"📅 {analysis_period}")
            
            # Custom grid
            grid_html = f"""
            <div class="custom-grid">
                {create_custom_metric_card("💸 Expense", f"₹{total_expense:,.0f}<br><small style='font-size: 0.7rem; color: #666;'>👨 {format_amount(total_expense_shubham)}  |  👩 {format_amount(total_expense_yashika)}</small>", "expense")}
                {create_custom_metric_card("📈 Investment", f"₹{total_investment:,.0f}<br><small style='font-size: 0.7rem; color: #666;'>Total: ₹{total_investment_alltime:,.0f}</small>", "investment")}            
                {create_custom_metric_card("💰 Income", f"₹{total_income:,.0f}", "income")}
                
                
            """
            st.markdown(grid_html, unsafe_allow_html=True)
        else:
            st.warning("Please select at least one month to view summary")
            selected_period_df = pd.DataFrame()  # Empty dataframe for charts section
        
        # -------------------------
        # Charts Section with Integrated Calendar
        # -------------------------
        if selected_months and not selected_period_df.empty:
            # st.header("📈 Analytics")
            
            # For calendar display, we'll use the first selected month
            # If multiple months selected, show calendar for the first one
            calendar_year = selected_year
            calendar_month = selected_months[0] if selected_months else None
            
            if len(selected_months) > 1:
                st.info(f"📅 Calendar shows daily breakdown for {datetime(2000, calendar_month, 1).strftime('%B')} {calendar_year} (first selected month)")
            
            # Chart tabs for Income, Expenses, and Investments
            chart_tab1, chart_tab2, chart_tab3 = st.tabs(["💸 Expenses", "📈 Investments", "💰 Income"])

            with chart_tab1:
                expense_df = selected_period_df[selected_period_df["Category"] == "Expense"]
                if not expense_df.empty:
                    # Calendar View for Expenses
                    # st.markdown('<div class="calendar-section">', unsafe_allow_html=True)
                    # st.markdown("#### 📅 Daily Expense Calendar")
                    
                    if calendar_month:
                        calendar_html = create_calendar_view(df, calendar_year, calendar_month, "Expense", "expense")
                        st.markdown(calendar_html, unsafe_allow_html=True)
                    
                    # st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Bar Chart for Expenses
                    # st.markdown("#### 📊 Expense Breakdown by Category")
                    expense_by_subcat = expense_df.groupby("Subcategory")["Amount (₹)"].sum().reset_index()
                    expense_by_subcat = expense_by_subcat.sort_values("Amount (₹)", ascending=False)
                    
                    # Add formatted labels for better readability
                    expense_by_subcat['Amount_Label'] = expense_by_subcat['Amount (₹)'].apply(format_amount)
                    
                    fig_exp = px.bar(expense_by_subcat, 
                                   x="Subcategory", 
                                   y="Amount (₹)",
                                   title="Expense Breakdown",
                                   text="Amount_Label")
                    fig_exp.update_layout(
                        height=400, 
                        xaxis_tickangle=-45, 
                        showlegend=False,
                        font=dict(size=12),
                        title_x=0.3,
                        title_font_size=16,
                        yaxis_title=None
                    )
                    fig_exp.update_traces(textposition='outside', marker_color='#dc3545')
                    # Adjust y-axis to accommodate labels
                    max_value = expense_by_subcat['Amount (₹)'].max()
                    fig_exp.update_yaxes(range=[0, max_value * 1.2])
                    
                    st.plotly_chart(fig_exp, use_container_width=True, config={'staticPlot': True})

                    # Monthly trend line chart
                    trend_exp = get_monthly_trend(df, "Expense", months=6)
                    trend_exp["Amount_Label"] = trend_exp["Amount (₹)"].apply(format_amount)

                    if not trend_exp.empty:
                        # st.markdown("6 Months Trend")
                        fig_line_exp = px.line(
                            trend_exp,
                            x="YearMonth",
                            y="Amount (₹)",
                            text="Amount_Label",  # 👈 Use your formatted labels
                            markers=True,
                            line_shape="linear",
                            title="6 Months Trend"
                        )

                        fig_line_exp.update_traces(
                            line_color='#dc3545',
                            textposition="top center"
                        )

                        fig_line_exp.update_layout(
                            yaxis_title="Amount (₹)",
                            xaxis_title="Month",
                            font=dict(size=12),
                            height=300,
                            title_font_size=16,
                            title_x=0.32,
                            xaxis_type='category',
                            margin=dict(t=80)
                        )

                        # Generate custom y-axis tick labels
                        y_max = trend_exp["Amount (₹)"].max()
                        y_pad = y_max * 0.2  # 20% padding
                        fig_line_exp.update_yaxes(range=[0, y_max + y_pad])
                        tick_step = y_max / 5  # Or use a fixed step like 50000
                        tick_vals = [round(i) for i in list(range(0, int(y_max * 1.1), int(tick_step)))]

                        fig_line_exp.update_yaxes(
                            range=[0, y_max + y_max * 0.2],
                            tickvals=tick_vals,
                            ticktext=[format_amount(v) for v in tick_vals]
                        )

                        st.plotly_chart(fig_line_exp, use_container_width=True, config={'staticPlot': True})
                    
                    # Top expenses
                    # st.subheader("🔝 Top Expenses")
                    # for _, row in expense_by_subcat.head(5).iterrows():
                    #     st.write(f"**{row['Subcategory']}**: ₹{row['Amount (₹)']:,.0f}")
                else:
                    st.info("No expense data for selected period")

            
            with chart_tab2:
                investment_df = selected_period_df[selected_period_df["Category"] == "Investment"]
                if not investment_df.empty:
                    # Calendar View for Investments
                    # st.markdown('<div class="calendar-section">', unsafe_allow_html=True)
                    # st.markdown("#### 📅 Daily Investment Calendar")
                    
                    if calendar_month:
                        calendar_html = create_calendar_view(df, calendar_year, calendar_month, "Investment", "investment")
                        st.markdown(calendar_html, unsafe_allow_html=True)
                    
                    # st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Bar Chart for Investments
                    # st.markdown("#### 📊 Investment Breakdown by Category")
                    investment_by_subcat = investment_df.groupby("Subcategory")["Amount (₹)"].sum().reset_index()
                    investment_by_subcat = investment_by_subcat.sort_values("Amount (₹)", ascending=False)
                    
                    # Add formatted labels for better readability
                    investment_by_subcat['Amount_Label'] = investment_by_subcat['Amount (₹)'].apply(format_amount)
                    
                    fig_inv = px.bar(investment_by_subcat, 
                                   x="Subcategory", 
                                   y="Amount (₹)",
                                   title="Investment Breakdown",
                                   text="Amount_Label")
                    fig_inv.update_layout(
                        height=400, 
                        xaxis_tickangle=-45, 
                        showlegend=False,
                        font=dict(size=12),
                        title_font_size=16,
                        title_x=0.3,
                        yaxis_title=None
                    )
                    fig_inv.update_traces(textposition='outside', marker_color='#c8b002')
                    # Adjust y-axis to accommodate labels
                    max_value = investment_by_subcat['Amount (₹)'].max()
                    fig_inv.update_yaxes(range=[0, max_value * 1.2])
                    
                    st.plotly_chart(fig_inv, use_container_width=True, config={'staticPlot': True})

                    # Monthly trend line chart
                    trend_exp = get_monthly_trend(df, "Investment", months=6)
                    trend_exp["Amount_Label"] = trend_exp["Amount (₹)"].apply(format_amount)

                    if not trend_exp.empty:
                        # st.markdown("6 Months Trend")
                        fig_line_exp = px.line(
                            trend_exp,
                            x="YearMonth",
                            y="Amount (₹)",
                            text="Amount_Label",  # 👈 Use your formatted labels
                            markers=True,
                            line_shape="linear",
                            title="6 Months Trend"
                        )

                        fig_line_exp.update_traces(
                            line_color='#c8b002',
                            textposition="top center"
                        )

                        fig_line_exp.update_layout(
                            yaxis_title="Amount (₹)",
                            xaxis_title="Month",
                            font=dict(size=12),
                            height=300,
                            title_font_size=16,
                            title_x=0.32,
                            xaxis_type='category',
                            margin=dict(t=80)
                        )

                        # Generate custom y-axis tick labels
                        y_max = trend_exp["Amount (₹)"].max()
                        y_pad = y_max * 0.2  # 20% padding
                        fig_line_exp.update_yaxes(range=[0, y_max + y_pad])
                        tick_step = y_max / 5  # Or use a fixed step like 50000
                        tick_vals = [round(i) for i in list(range(0, int(y_max * 1.1), int(tick_step)))]

                        fig_line_exp.update_yaxes(
                            range=[0, y_max + y_max * 0.2],
                            tickvals=tick_vals,
                            ticktext=[format_amount(v) for v in tick_vals]
                        )

                        st.plotly_chart(fig_line_exp, use_container_width=True, config={'staticPlot': True})
                    
                    # Investment summary
                    # st.subheader("💼 Investment Summary")
                    # for _, row in investment_by_subcat.iterrows():
                    #     st.write(f"**{row['Subcategory']}**: ₹{row['Amount (₹)']:,.0f}")
                else:
                    st.info("No investment data for selected period")

            with chart_tab3:
                income_df = selected_period_df[selected_period_df["Category"] == "Income"]
                if not income_df.empty:
                    # Calendar View for Income
                    # st.markdown('<div class="calendar-section">', unsafe_allow_html=True)
                    # st.markdown("#### 📅 Daily Income Calendar")
                    
                    if calendar_month:
                        calendar_html = create_calendar_view(df, calendar_year, calendar_month, "Income", "income")
                        st.markdown(calendar_html, unsafe_allow_html=True)
                    
                    # st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Bar Chart for Income
                    # st.markdown("#### 📊 Income Breakdown by Category")
                    income_by_subcat = income_df.groupby("Subcategory")["Amount (₹)"].sum().reset_index()
                    income_by_subcat = income_by_subcat.sort_values("Amount (₹)", ascending=False)
                    
                    # Add formatted labels for better readability
                    income_by_subcat['Amount_Label'] = income_by_subcat['Amount (₹)'].apply(format_amount)
                    
                    fig_inc = px.bar(income_by_subcat, 
                                   x="Subcategory", 
                                   y="Amount (₹)",
                                   title="Income Breakdown",
                                   text="Amount_Label")
                    fig_inc.update_layout(
                        height=400, 
                        xaxis_tickangle=-45, 
                        showlegend=False,
                        font=dict(size=12),
                        title_font_size=16,
                        title_x=0.3,
                        yaxis_title=None
                    )
                    fig_inc.update_traces(textposition='outside', marker_color='#28a745')
                    # Adjust y-axis to accommodate labels
                    max_value = income_by_subcat['Amount (₹)'].max()
                    fig_inc.update_yaxes(range=[0, max_value * 1.2])
                    
                    st.plotly_chart(fig_inc, use_container_width=True, config={'staticPlot': True})


                    # Monthly trend line chart
                    trend_exp = get_monthly_trend(df, "Income", months=6)
                    trend_exp["Amount_Label"] = trend_exp["Amount (₹)"].apply(format_amount)

                    if not trend_exp.empty:
                        # st.markdown("6 Months Trend")
                        fig_line_exp = px.line(
                            trend_exp,
                            x="YearMonth",
                            y="Amount (₹)",
                            text="Amount_Label",  # 👈 Use your formatted labels
                            markers=True,
                            line_shape="linear",
                            title="6 Months Trend"
                        )

                        fig_line_exp.update_traces(
                            line_color='#28a745',
                            textposition="top center"
                        )

                        fig_line_exp.update_layout(
                            yaxis_title="Amount (₹)",
                            xaxis_title="Month",
                            font=dict(size=12),
                            height=300,
                            title_font_size=16,
                            title_x=0.32,
                            xaxis_type='category',
                            margin=dict(t=80)
                        )


                        # Generate custom y-axis tick labels
                        y_max = trend_exp["Amount (₹)"].max()
                        y_pad = y_max * 0.2  # 20% padding
                        fig_line_exp.update_yaxes(range=[0, y_max + y_pad])
                        tick_step = y_max / 5  # Or use a fixed step like 50000
                        tick_vals = [round(i) for i in list(range(0, int(y_max * 1.1), int(tick_step)))]

                        fig_line_exp.update_yaxes(
                            range=[0, y_max + y_max * 0.2],
                            tickvals=tick_vals,
                            ticktext=[format_amount(v) for v in tick_vals]
                        )

                        st.plotly_chart(fig_line_exp, use_container_width=True, config={'staticPlot': True})

                    
                    # Income summary
                    # st.subheader("💰 Income Summary")
                    # for _, row in income_by_subcat.iterrows():
                    #     st.write(f"**{row['Subcategory']}**: ₹{row['Amount (₹)']:,.0f}")
                else:
                    st.info("No income data for selected period")

    else:
        # Empty state
        st.subheader(f"📅 {datetime.now().strftime('%B %Y')}")
        grid_html = f"""
        <div class="custom-grid">
            {create_custom_metric_card("💰 Income", "₹0", "income")}
            {create_custom_metric_card("💸 Expense", "₹0", "expense")}
            {create_custom_metric_card("📈 Investment", "₹0", "investment")}
            {create_custom_metric_card("💵 Balance", "₹0", "balance")}
        """
        st.markdown(grid_html, unsafe_allow_html=True)
        st.info("No transactions recorded yet. Add your first transaction in the 'Add Transaction' tab!")


# -------------------------
# TAB 3: Leave
# -------------------------
with tab3:
    st.header("🏠 Leave Tracker")
    
    if not df.empty:
        # Month and Year selection
        col1, col2 = st.columns(2)
        
        with col1:
            available_years = sorted(df["Date"].dt.year.unique(), reverse=True)
            default_year = datetime.now().year if datetime.now().year in available_years else available_years[0]
            Leave_selected_year = st.selectbox("Year", available_years, 
                                               index=available_years.index(default_year), 
                                               key="Leave_year")
        
        with col2:
            # Get months available for the selected year
            year_data = df[df["Date"].dt.year == Leave_selected_year]
            available_months = sorted(year_data["Date"].dt.month.unique())
            
            # Set default to current month if available
            current_month = datetime.now().month
            default_month = current_month if (current_month in available_months and 
                                           Leave_selected_year == datetime.now().year) else available_months[0] if available_months else current_month
            
            month_options = [(month, calendar.month_name[month]) for month in range(1, 13)]
            try:
                default_index = [month for month, _ in month_options].index(default_month)
            except ValueError:
                default_index = current_month - 1
                
            selected_month_name = st.selectbox(
                "Month", 
                options=[name for _, name in month_options],
                index=default_index,
                key="Leave_month"
            )
            
            # Get the month number
            Leave_selected_month = next(month for month, name in month_options if name == selected_month_name)
        
        # Filter Leave data for selected month
        Leave_data = df[(df["Date"].dt.year == Leave_selected_year) & 
                        (df["Date"].dt.month == Leave_selected_month) & 
                        (df["Category"] == "Leave")]
        
        # Monthly summary cards
        maid_Leave = len(Leave_data[Leave_data["Subcategory"] == "Maid"])
        cook_Leave = len(Leave_data[Leave_data["Subcategory"] == "Cook"])
        
        # Custom grid for Leave summary
        Leave_grid_html = f"""
            <div class="leave-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; width: 100%; margin: 1rem 0;">
                <div class="custom-metric" style="background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 50%, #f48fb1 100%);
                    border: 0px solid #e91e63; box-shadow: 0 2px 10px rgba(233, 30, 99, 0.15);">
                    <div class="metric-label">👩‍🍳 Maid Leaves</div>
                    <div class="metric-value">{maid_Leave} days</div>
                </div>
                <div class="custom-metric" style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%);
                    border: 0px solid #2196f3; box-shadow: 0 2px 10px rgba(33, 150, 243, 0.15);">
                    <div class="metric-label">👨‍🍳 Cook Leaves</div>
                    <div class="metric-value">{cook_Leave} days</div>
                </div>
            </div>
        """
        st.markdown(Leave_grid_html, unsafe_allow_html=True)
        
        # Generate and display Leave calendar
        Leave_calendar_html = create_Leave_calendar_view(df, Leave_selected_year, Leave_selected_month)
        st.markdown(Leave_calendar_html, unsafe_allow_html=True)
        
        # Add legend
        # st.markdown("""
        # <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
        #     <span style="background: #fce4ec; color: #e91e63; padding: 0.2rem 0.5rem; border-radius: 8px; font-size: 0.8rem; border: 1px solid #f8bbd9;">👩‍🍳 Maid Leave</span>
        #     <span style="background: #e3f2fd; color: #2196f3; padding: 0.2rem 0.5rem; border-radius: 8px; font-size: 0.8rem; border: 1px solid #bbdefb;">👨‍🍳 Cook Leave</span>
        # </div>
        # """, unsafe_allow_html=True)
        
        # Show recent Leave
        # if not Leave_data.empty:
        #     st.markdown("---")
        #     st.subheader("📋 This Month's Leave")
            
        #     for _, row in Leave_data.sort_values("Date", ascending=False).iterrows():
        #         date_str = row["Date"].strftime("%d %b")
        #         person = row["Subcategory"]
        #         color = "#e91e63" if person == "Maid" else "#2196f3"
        #         icon = "👩‍🍳" if person == "Maid" else "👨‍🍳"
                
        #         st.markdown(f"""
        #         <div class="recent-entry">
        #             <span class="entry-date">{date_str}</span> | 
        #             <span class="entry-category" style="color: {color};">{icon} {person}</span>
        #             <br><small>{row["Description"] if row["Description"] else "Leave"}</small>
        #         </div>
        #         """, unsafe_allow_html=True)
        
    else:
        # Empty state
        st.subheader(f"📅 {datetime.now().strftime('%B %Y')}")
        
        # Empty summary cards
        Leave_grid_html = f"""
        
        <div class="leave-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; width: 100%; margin: 1rem 0;">
            <div class="custom-metric" style="background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 50%, #f48fb1 100%); border: 0px solid #e91e63; box-shadow: 0 2px 10px rgba(233, 30, 99, 0.15);">
                <div class="metric-label">👩‍🍳 Maid Leave</div>
                <div class="metric-value">0 days</div>
            </div>
            <div class="custom-metric" style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%); border: 0px solid #2196f3; box-shadow: 0 2px 10px rgba(33, 150, 243, 0.15);">
                <div class="metric-label">👨‍🍳 Cook Leave</div>
                <div class="metric-value">0 days</div>
            </div>
        </div>
        """
        st.markdown(Leave_grid_html, unsafe_allow_html=True)
        
        st.info("No Leave recorded yet. Add leave entries in the 'Add Transaction' tab using 'Leave' category!")
        
        # Show empty calendar for current month
        current_year = datetime.now().year
        current_month = datetime.now().month
        empty_calendar = create_Leave_calendar_view(pd.DataFrame(), current_year, current_month)
        st.markdown(empty_calendar, unsafe_allow_html=True)

# # -------------------------
# # TAB 3: CALENDAR VIEW
# # -------------------------
# with tab3:
#     st.header("📅 Monthly Calendar")
    
#     if not df.empty:
#         # Month and Year selection for calendar
#         col1, col2 = st.columns(2)
        
#         with col1:
#             available_years = sorted(df["Date"].dt.year.unique(), reverse=True)
#             default_year = datetime.now().year if datetime.now().year in available_years else available_years[0]
#             cal_selected_year = st.selectbox("Year", available_years, 
#                                            index=available_years.index(default_year), 
#                                            key="calendar_year")
        
#         with col2:
#             # Get months available for the selected year
#             year_data = df[df["Date"].dt.year == cal_selected_year]
#             available_months = sorted(year_data["Date"].dt.month.unique())
            
#             # Set default to current month if available
#             current_month = datetime.now().month
#             default_month = current_month if (current_month in available_months and 
#                                            cal_selected_year == datetime.now().year) else available_months[0]
            
#             month_options = [(month, calendar.month_name[month]) for month in available_months]
#             selected_month_name = st.selectbox(
#                 "Month", 
#                 options=[name for _, name in month_options],
#                 index=[name for month, name in month_options].index(calendar.month_name[default_month]),
#                 key="calendar_month"
#             )
            
#             # Get the month number
#             cal_selected_month = next(month for month, name in month_options if name == selected_month_name)
        
#         # Generate and display calendar
#         calendar_html = create_calendar_view(df, cal_selected_year, cal_selected_month)
#         st.markdown(calendar_html, unsafe_allow_html=True)
        
#         # Add legend
#         # st.markdown("""
#         # <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
#         #     <span style="background: #ffe6e6; color: #dc3545; padding: 0.2rem 0.5rem; border-radius: 8px; font-size: 0.8rem;">💸 Expenses</span>
#         #     <span style="background: #e6ffe6; color: #28a745; padding: 0.2rem 0.5rem; border-radius: 8px; font-size: 0.8rem;">💰 Income</span>
#         #     <span style="background: #fffde6; color: #c8b002; padding: 0.2rem 0.5rem; border-radius: 8px; font-size: 0.8rem;">📈 Investments</span>
#         # </div>
#         # """, unsafe_allow_html=True)
        
#         # Show monthly summary below calendar
#         st.markdown("---")
#         month_data = df[(df["Date"].dt.year == cal_selected_year) & 
#                        (df["Date"].dt.month == cal_selected_month)]
        
#         if not month_data.empty:
#             col1, col2, col3 = st.columns(3)
            
#             total_income = month_data[month_data["Category"] == "Income"]["Amount (₹)"].sum()
#             total_expense = month_data[month_data["Category"] == "Expense"]["Amount (₹)"].sum()
#             total_investment = month_data[month_data["Category"] == "Investment"]["Amount (₹)"].sum()
            
#             col1.metric("💰 Income", f"₹{total_income:,.0f}")
#             col2.metric("💸 Expenses", f"₹{total_expense:,.0f}")
#             col3.metric("📈 Investments", f"₹{total_investment:,.0f}")
            
#             # Daily breakdown (expandable)
#             # with st.expander("📋 Daily Breakdown"):
#             #     daily_transactions = month_data.groupby(month_data["Date"].dt.day).agg({
#             #         "Amount (₹)": ["count", "sum"],
#             #         "Category": lambda x: x.value_counts().to_dict()
#             #     }).reset_index()
                
#             #     for _, row in daily_transactions.iterrows():
#             #         day = row["Date"]
#             #         count = row[("Amount (₹)", "count")]
#             #         total = row[("Amount (₹)", "sum")]
#             #         categories = row[("Category", "<lambda>")]
                    
#             #         st.write(f"**Day {day}**: {count} transactions, Total: ₹{total:,.0f}")
#             #         category_text = ", ".join([f"{cat}: {cnt}" for cat, cnt in categories.items()])
#             #         st.write(f"   ↳ {category_text}")
        
#     else:
#         st.info("No transactions recorded yet. Add your first transaction to see the calendar view!")
        
#         # Show empty calendar for current month
#         current_year = datetime.now().year
#         current_month = datetime.now().month
#         empty_calendar = create_calendar_view(pd.DataFrame(), current_year, current_month)
#         st.markdown(empty_calendar, unsafe_allow_html=True)
        
# Debug section at the bottom
if DEBUG_MODE:
    st.markdown("---")
    st.subheader("🔧 Debug Panel")
    
    if st.button("🧪 Test Google Sheets Connection"):
        ws = get_worksheet()
        
        if ws:
            try:
                headers = ws.row_values(1)
                st.success(f"✅ Connection successful! Headers: {headers}")
                
                # Test write permissions by attempting to read last row
                all_values = ws.get_all_values()
                st.info(f"📊 Sheet has {len(all_values)} rows (including header)")
                
            except Exception as e:
                st.error(f"❌ Connection test failed: {e}")
        else:
            st.error("❌ Connection failed")
    
    if st.button("🔄 Clear All Caches"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.last_transaction_time = None
        st.success("✅ All caches cleared!")
        st.rerun()
    
    # Toggle debug mode
    if st.button("🔍 Turn Off Debug Mode"):
        DEBUG_MODE = False
        st.rerun()
