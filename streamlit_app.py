import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import json
from google.oauth2.service_account import Credentials
import calendar

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

    /* Interactive Metric Cards Grid */
    .interactive-metrics-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 0.75rem !important;
        margin: 1rem 0 !important;
    }

    .interactive-metric-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 2px solid #e0e0e0;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        min-height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        user-select: none;
        position: relative;
    }

    .interactive-metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-color: #bbb;
    }

    .interactive-metric-card:active {
        transform: translateY(0px);
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }

    .interactive-metric-card.selected {
        border-color: #007bff;
        box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
    }

    .metric-card-label {
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
        color: #6c757d;
    }

    .metric-card-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #333;
    }

    /* Card type specific colors */
    .metric-income { 
        background: linear-gradient(135deg, #d4edda, #a8e6a3) !important; 
    }
    .metric-expense { 
        background: linear-gradient(135deg, #f8d7da, #e57366) !important; 
    }
    .metric-investment { 
        background: linear-gradient(135deg, #fff3cd, #ffeaa7) !important; 
    }
    .metric-balance { 
        background: linear-gradient(135deg, #d1ecf1, #a3d5db) !important; 
    }

    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .interactive-metrics-grid {
            gap: 0.5rem !important;
        }
        
        .interactive-metric-card {
            padding: 0.8rem;
            min-height: 80px;
        }
        
        .metric-card-label {
            font-size: 0.8rem;
        }
        
        .metric-card-value {
            font-size: 1.1rem;
        }
    }

    /* Original styles for other components */
    .custom-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 0.5rem !important;
        margin: 1rem 0 !important;
    }

    .custom-metric {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 2px solid #e0e0e0;
        padding: 0.8rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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

    /* Calendar Integration Styles */
    .calendar-analytics-container {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1rem;
    }

    @media (min-width: 1024px) {
        .calendar-analytics-container {
            grid-template-columns: 1fr 1fr;
        }
    }

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

    /* Make buttons look like cards */
    .stButton > button {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.2rem;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        height: 100px;
        width: 100%;
        white-space: pre-line;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        transition: all 0.2s ease-in-out;
    }

    .stButton > button:hover {
        transform: scale(1.02);
        border-color: #bbb;
    }

    button.custom-metric {
        all: unset;
        cursor: pointer;
        width: 100%;
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
    "Other": ["Transfer", "Loan Given", "Loan Received", "Tax Payment", "Miscellaneous"]
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

def create_calendar_view(df, selected_year, selected_month, filter_category="All"):
    """Create a mobile-friendly calendar view showing daily amounts for selected category"""
    import calendar
    
    # Filter data for selected month/year
    month_data = df[(df["Date"].dt.year == selected_year) & 
                   (df["Date"].dt.month == selected_month)]
    
    # Apply category filter
    if filter_category != "All":
        month_data = month_data[month_data["Category"] == filter_category]
    
    # Group by date and calculate daily totals
    if not month_data.empty:
        if filter_category == "All":
            # Show all categories with different colors
            daily_summary = month_data.groupby([month_data["Date"].dt.day, "Category"])["Amount (₹)"].sum().reset_index()
            daily_summary = daily_summary.pivot(index='Date', columns='Category', values='Amount (₹)').fillna(0)
        else:
            # Show only the selected category
            daily_summary = month_data.groupby(month_data["Date"].dt.day)["Amount (₹)"].sum().reset_index()
            daily_summary.set_index('Date', inplace=True)
    else:
        daily_summary = pd.DataFrame()
    
    # Get calendar layout
    cal = calendar.monthcalendar(selected_year, selected_month)
    month_name = calendar.month_name[selected_month]
    
    # Category colors and labels
    category_styles = {
        "Expense": {"color": "#dc3545", "bg": "#ffe6e6", "label": "💸"},
        "Income": {"color": "#28a745", "bg": "#e6ffe6", "label": "💰"},
        "Investment": {"color": "#c8b002", "bg": "#fffde6", "label": "📈"},
        "Other": {"color": "#6c757d", "bg": "#f0f0f0", "label": "📋"}
    }
    
    # Create HTML calendar
    calendar_html = f"""
    <style>
    .calendar-container {{
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 0 auto;
        max-width: 100%;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        overflow: hidden;
    }}
    
    .calendar-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        padding: 1rem;
        font-size: 1rem;
        font-weight: 600;
    }}
    
    .calendar-grid {{
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 1px;
        background: #e9ecef;
    }}
    
    .day-header {{
        background: #f8f9fa;
        padding: 0.5rem 0.2rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.8rem;
        color: #6c757d;
        border-bottom: 1px solid #dee2e6;
    }}
    
    .calendar-day {{
        background: white;
        min-height: 80px;
        padding: 0.3rem;
        display: flex;
        flex-direction: column;
        position: relative;
        border: 1px solid #f0f0f0;
    }}
    
    .calendar-day.other-month {{
        background: #f8f9fa;
        color: #adb5bd;
    }}
    
    .calendar-day.today {{
        background: #fff3cd;
        border: 2px solid #ffc107;
    }}
    
    .day-number {{
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.2rem;
        color: #495057;
    }}
    
    .amount-display {{
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.1rem 0.3rem;
        border-radius: 8px;
        margin: 0.1rem 0;
        text-align: center;
    }}
    
    @media (max-width: 768px) {{
        .calendar-day {{
            min-height: 70px;
            padding: 0.2rem;
        }}
        .day-number {{
            font-size: 0.8rem;
        }}
        .amount-display {{
            font-size: 0.6rem;
            padding: 0.05rem 0.2rem;
        }}
    }}
    </style>
    
    <div class="calendar-container">
        <div class="calendar-header">
            {month_name} {selected_year} - {filter_category}
        </div>
        <div class="calendar-grid">
            <!-- Day headers -->
            <div class="day-header">Sun</div>
            <div class="day-header">Mon</div>
            <div class="day-header">Tue</div>
            <div class="day-header">Wed</div>
            <div class="day-header">Thu</div>
            <div class="day-header">Fri</div>
            <div class="day-header">Sat</div>
    """
    
    # Get today's date for highlighting
    today = datetime.today()
    is_current_month = (today.year == selected_year and today.month == selected_month)
    
    # Generate calendar days
    for week in cal:
        for day in week:
            if day == 0:
                calendar_html += '<div class="calendar-day other-month"></div>'
            else:
                # Check if this is today
                is_today = is_current_month and day == today.day
                today_class = " today" if is_today else ""
                
                calendar_html += f'<div class="calendar-day{today_class}">'
                calendar_html += f'<div class="day-number">{day}</div>'
                
                # Add transaction amounts for this day
                if not daily_summary.empty and day in daily_summary.index:
                    if filter_category == "All":
                        # Show all categories
                        day_data = daily_summary.loc[day]
                        for category in ["Expense", "Income", "Investment", "Other"]:
                            if day_data.get(category, 0) > 0:
                                style = category_styles[category]
                                amount_str = f"₹{day_data[category]:,.0f}"
                                if day_data[category] >= 1000:
                                    amount_str = f"₹{day_data[category]/1000:.1f}K"
                                calendar_html += f'<div class="amount-display" style="color: {style["color"]}; background: {style["bg"]};">{style["label"]}{amount_str}</div>'
                    else:
                        # Show only selected category
                        amount = daily_summary.loc[day]['Amount (₹)'] if 'Amount (₹)' in daily_summary.columns else daily_summary.loc[day]
                        if amount > 0:
                            style = category_styles.get(filter_category, category_styles["Other"])
                            amount_str = f"₹{amount:,.0f}"
                            if amount >= 1000:
                                amount_str = f"₹{amount/1000:.1f}K"
                            calendar_html += f'<div class="amount-display" style="color: {style["color"]}; background: {style["bg"]};">{style["label"]}{amount_str}</div>'
                
                calendar_html += '</div>'
    
    calendar_html += """
        </div>
    </div>
    """
    
    return calendar_html

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
        new_row = [date_str, category, subcategory, description.strip().title(), float(amount)]
        
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

st.title("💸 Finance Tracker")

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

# CREATE TABS HERE - Only 2 tabs now
tab1, tab2 = st.tabs(["📝 Add Transaction", "📊 Analytics & Calendar"])


# -------------------------
# TAB 1: ADD TRANSACTION
# -------------------------
with tab1:
    st.header("📝 Add New Transaction")
    
    # Form inputs OUTSIDE the form to enable dynamic updates
    col1, col2 = st.columns(2)
    date = col1.date_input("Date", datetime.today(), key=f"date_{st.session_state.form_key}")

    # Category selection with callback to update subcategories
    category = col2.selectbox(
        "Category", 
        ["Expense", "Income", "Investment", "Other"],
        index=["Expense", "Income", "Investment", "Other"].index(st.session_state.form_category),
        key=f"category_select_{st.session_state.form_key}"
    )

    # Update session state when category changes
    if category != st.session_state.form_category:
        st.session_state.form_category = category

    # Dynamic subcategory based on selected category
    subcategory_options = SUBCATEGORIES.get(category, [])
    subcategory = st.selectbox("Subcategory", subcategory_options, key=f"subcategory_{st.session_state.form_key}")

    description = st.text_input("Description", placeholder="Enter transaction description", key=f"description_{st.session_state.form_key}")
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f", step=1.0, key=f"amount_{st.session_state.form_key}")
    
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
        # Enhanced validation
        errors = []
        
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
            if DEBUG_MODE:
                st.write("🔍 Debug: All validations passed, attempting to add transaction...")
            
            # Add transaction with error handling
            success, message = add_transaction(date, category, subcategory, description.strip(), amount)
            
            if success:
                # Clear the data cache to refresh data
                load_data_cached.clear()
                
                # Show success message and balloons BEFORE rerun
                st.success("✅ Transaction successfully recorded!")
                st.balloons()
                
                # Small delay to show the message
                import time
                time.sleep(2)
                
                # Reset form state
                st.session_state.form_key += 1
                st.session_state.form_category = "Expense"  # Reset to default
                
                # Auto-refresh the page after successful entry
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
        recent_df = df.tail(5).iloc[::-1]  # Get last 5 and reverse order to show newest first
        
        for _, row in recent_df.iterrows():
            date_str = row["Date"].strftime("%d %b")
            category_color = {"Income": "#28a745", "Expense": "#dc3545", "Investment": "#c8b002", "Other": "#6c757d"}
            color = category_color.get(row["Category"], "#6c757d")
            
            st.markdown(f"""
            <div class="recent-entry">
                <span class="entry-date">{date_str}</span> | 
                <span class="entry-category" style="color: {color};">{row["Category"]}</span> - {row["Subcategory"]}
                <span class="entry-amount" style="color: {color};">₹{row["Amount (₹)"]:,.0f}</span>
                <br><small>{row["Description"]}</small>
            </div>
            """, unsafe_allow_html=True)

# -------------------------
# TAB 2: INTEGRATED ANALYTICS & CALENDAR
# -------------------------
with tab2:
    st.header("📊 Analytics & Calendar")

    if not df.empty:
        # Year and Month selectors
        col1, col2 = st.columns(2)

        with col1:
            available_years = sorted(df["Date"].dt.year.unique(), reverse=True)
            default_year = datetime.now().year if datetime.now().year in available_years else available_years[0]
            selected_year = st.selectbox("Year", available_years, index=available_years.index(default_year))

        with col2:
            year_data = df[df["Date"].dt.year == selected_year]
            available_months = sorted(year_data["Date"].dt.month.unique())
            month_names = [(month, datetime(2000, month, 1).strftime('%B')) for month in available_months]

            current_month = datetime.now().month
            default_months = [current_month] if current_month in available_months and selected_year == datetime.now().year else [available_months[0]] if available_months else []

            selected_month_names = st.multiselect(
                "Month(s) for Summary",
                options=[name for _, name in month_names],
                default=[datetime(2000, month, 1).strftime('%B') for month in default_months],
                help="Select one or multiple months for summary"
            )

        selected_months = [month for month, name in month_names if name in selected_month_names]

        # Initialize session state for calendar filter
        if 'calendar_view_category' not in st.session_state:
            st.session_state.calendar_view_category = "All"

        if selected_months:
            selected_period_df = df[(df["Date"].dt.month.isin(selected_months)) & (df["Date"].dt.year == selected_year)]

            total_income = selected_period_df[selected_period_df["Category"] == "Income"]["Amount (₹)"].sum()
            total_expense = selected_period_df[selected_period_df["Category"] == "Expense"]["Amount (₹)"].sum()
            total_investment = selected_period_df[selected_period_df["Category"] == "Investment"]["Amount (₹)"].sum()
            net_savings = total_income - total_expense - total_investment

            st.markdown("### 📅 Monthly Summary")
            st.markdown("<p style='font-size: 0.9rem; color: #6c757d; margin-bottom: 1rem;'>Tap a card to filter calendar view</p>", unsafe_allow_html=True)

            # Create interactive metric cards using HTML and JavaScript
            metrics_data = [
                {"label": "💰 Income", "value": total_income, "type": "Income", "class": "metric-income"},
                {"label": "💸 Expense", "value": total_expense, "type": "Expense", "class": "metric-expense"},
                {"label": "📈 Investment", "value": total_investment, "type": "Investment", "class": "metric-investment"},
                {"label": "💵 Balance", "value": net_savings, "type": "All", "class": "metric-balance"},
            ]

            # Generate unique IDs for this session
            import uuid
            session_id = str(uuid.uuid4())[:8]

            metrics_html = f"""
            <div class="interactive-metrics-grid" id="metrics-grid-{session_id}">
            """

            for i, metric in enumerate(metrics_data):
                selected_class = " selected" if st.session_state.calendar_view_category == metric['type'] else ""
                metrics_html += f"""
                <div class="interactive-metric-card {metric['class']}{selected_class}" 
                     data-category="{metric['type']}" 
                     onclick="selectMetric_{session_id}('{metric['type']}', this)">
                    <div class="metric-card-label">{metric['label']}</div>
                    <div class="metric-card-value">₹{metric['value']:,.0f}</div>
                </div>
                """

            metrics_html += f"""
            </div>

            <script>
            function selectMetric_{session_id}(category, element) {{
                // Remove selected class from all cards
                document.querySelectorAll('#metrics-grid-{session_id} .interactive-metric-card').forEach(card => {{
                    card.classList.remove('selected');
                }});
                
                // Add selected class to clicked card
                element.classList.add('selected');
                
                // Store the selection in a hidden input that Streamlit can read
                let hiddenInput = document.getElementById('selected-category-{session_id}');
                if (!hiddenInput) {{
                    hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.id = 'selected-category-{session_id}';
                    hiddenInput.name = 'selected_category';
                    document.body.appendChild(hiddenInput);
                }}
                hiddenInput.value = category;
                
                // Trigger a custom event that we can listen to
                window.parent.postMessage({{
                    type: 'metric-selected',
                    category: category,
                    sessionId: '{session_id}'
                }}, '*');
                
                // Alternative: Use Streamlit's component communication
                if (window.parent.streamlitRerun) {{
                    window.parent.streamlitRerun();
                }}
            }}
            
            // Listen for messages from the parent window
            window.addEventListener('message', function(event) {{
                if (event.data.type === 'metric-selected' && event.data.sessionId === '{session_id}') {{
                    // This will be handled by Streamlit
                    console.log('Metric selected:', event.data.category);
                }}
            }});
            </script>
            """

            st.markdown(metrics_html, unsafe_allow_html=True)

            # Use columns with buttons as a fallback method for interaction
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # Create invisible buttons that can be triggered
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📊", key=f"income_btn_{session_id}", help="Filter by Income"):
                    st.session_state.calendar_view_category = "Income"
                    st.rerun()
            
            with col2:
                if st.button("💸", key=f"expense_btn_{session_id}", help="Filter by Expense"):
                    st.session_state.calendar_view_category = "Expense"
                    st.rerun()
            
            with col3:
                if st.button("📈", key=f"investment_btn_{session_id}", help="Filter by Investment"):
                    st.session_state.calendar_view_category = "Investment"
                    st.rerun()
            
            with col4:
                if st.button("💵", key=f"all_btn_{session_id}", help="Show All"):
                    st.session_state.calendar_view_category = "All"
                    st.rerun()

            # Show current filter
            if st.session_state.calendar_view_category != "All":
                st.info(f"📍 Calendar filtered by: **{st.session_state.calendar_view_category}**")

            # Render calendar for first selected month
            cal_month = selected_months[0]
            filter_category = st.session_state.calendar_view_category

            st.markdown("---")
            calendar_html = create_calendar_view(df, selected_year, cal_month, filter_category=filter_category)
            st.markdown(calendar_html, unsafe_allow_html=True)

        else:
            st.warning("Please select at least one month to view summary and calendar.")

    else:
        st.info("No transactions recorded yet. Add your first transaction to see analytics and calendar.")
