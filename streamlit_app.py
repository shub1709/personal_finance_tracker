import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# MUST BE FIRST - Set page config before any other Streamlit commands
st.set_page_config(page_title="💰 Personal Finance Tracker", layout="centered")

# Simple mobile-optimized CSS
st.markdown("""
<style>
    /* Force mobile-friendly container */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Ensure columns stack properly on mobile */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        /* Force 2x2 grid on mobile */
        div[data-testid="column"] {
            width: 50% !important;
            flex: 0 0 50% !important;
            max-width: 50% !important;
            padding: 0.25rem !important;
        }
        
        .row-widget.stHorizontal {
            gap: 0 !important;
        }
    }
    
    /* Style metric containers */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Metric label */
    div[data-testid="metric-container"] div[data-testid="metric-label"] {
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    /* Metric value */
    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    /* Color coding for different metrics */
    div[data-testid="metric-container"]:has(div[data-testid="metric-label"]:contains("Income")) {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border-color: #28a745;
    }
    
    div[data-testid="metric-container"]:has(div[data-testid="metric-label"]:contains("Expense")) {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        border-color: #dc3545;
    }
    
    div[data-testid="metric-container"]:has(div[data-testid="metric-label"]:contains("Investment")) {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        border-color: #17a2b8;
    }
    
    div[data-testid="metric-container"]:has(div[data-testid="metric-label"]:contains("Balance")) {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border-color: #ffc107;
    }
    
    /* Reduce header sizes */
    h1 { font-size: 1.5rem; }
    h2 { font-size: 1.25rem; }
    h3 { font-size: 1.1rem; }
    
    /* Form styling */
    .stSelectbox label, .stDateInput label, .stTextInput label, .stNumberInput label {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Connect to Google Sheets
@st.cache_resource
def get_gsheet_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

# Define subcategories for each category
SUBCATEGORIES = {
    "Income": [
        "Salary",
        "Freelancing",
        "Business Income",
        "Rental Income",
        "Interest/Dividends",
        "Bonus",
        "Gift/Inheritance",
        "Other Income"
    ],
    "Expense": [
        "Food & Dining",
        "Groceries",
        "Transportation",
        "Utilities",
        "Rent/EMI",
        "Healthcare",
        "Entertainment",
        "Shopping",
        "Education",
        "Insurance",
        "Travel",
        "Personal Care",
        "Other Expense"
    ],
    "Investment": [
        "Mutual Funds",
        "Stocks",
        "Fixed Deposits",
        "PPF",
        "EPF",
        "Gold",
        "Real Estate",
        "Crypto",
        "Bonds",
        "Other Investment"
    ],
    "Other": [
        "Transfer",
        "Loan Given",
        "Loan Received",
        "Tax Payment",
        "Miscellaneous"
    ]
}

# Load worksheet
client = get_gsheet_connection()
sheet = client.open("MyFinanceTracker")  # CHANGE to your Sheet name
ws = sheet.worksheet("Tracker")          # Single tab name

st.title("💸 Daily Expense & Investment Tracker")

# -------------------------
# Monthly Summary Cards
# -------------------------
st.header("📊 Monthly Summary")

# Load data
data = ws.get_all_records()
df = pd.DataFrame(data)
if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Month and Year selection
    col1, col2 = st.columns(2)
    
    with col1:
        available_years = sorted(df["Date"].dt.year.unique(), reverse=True)
        default_year = datetime.now().year if datetime.now().year in available_years else available_years[-1]
        selected_year = st.selectbox("Select Year", available_years, index=available_years.index(default_year))
    
    with col2:
        # Get months available for the selected year
        year_data = df[df["Date"].dt.year == selected_year]
        available_months = sorted(year_data["Date"].dt.month.unique())
        month_names = [datetime(2000, month, 1).strftime('%B') for month in available_months]
        
        # Set default to current month if available, otherwise first available month
        current_month = datetime.now().month
        if current_month in available_months and selected_year == datetime.now().year:
            default_month_index = available_months.index(current_month)
        else:
            default_month_index = -1
        
        selected_month_name = st.selectbox("Select Month", month_names, index=default_month_index)
        selected_month = datetime.strptime(selected_month_name, '%B').month
    
    # Filter for selected month and year
    selected_month_df = df[(df["Date"].dt.month == selected_month) & (df["Date"].dt.year == selected_year)]
    
    # Calculate totals for selected month
    total_income = selected_month_df[selected_month_df["Category"] == "Income"]["Amount (₹)"].sum()
    total_expense = selected_month_df[selected_month_df["Category"] == "Expense"]["Amount (₹)"].sum()
    total_investment = selected_month_df[selected_month_df["Category"] == "Investment"]["Amount (₹)"].sum()
    net_savings = total_income - total_expense - total_investment
    
    # Display selected month/year in the cards section
    st.subheader(f"📅 {selected_month_name} {selected_year}")
    
    # Display summary cards in 2x2 grid - simplified without wrapper divs
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row1_col1:
        st.metric(
            label="💰 Income",
            value=f"₹{total_income:,.0f}"
        )
    
    with row1_col2:
        st.metric(
            label="💸 Expense",
            value=f"₹{total_expense:,.0f}"
        )
    
    with row2_col1:
        st.metric(
            label="📈 Investment",
            value=f"₹{total_investment:,.0f}"
        )
    
    with row2_col2:
        st.metric(
            label="💵 Balance",
            value=f"₹{net_savings:,.0f}"
        )
        
else:
    # Show empty cards if no data in 2x2 grid
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row1_col1:
        st.metric(label="💰 Income", value="₹0")
    with row1_col2:
        st.metric(label="💸 Expense", value="₹0") 
    with row2_col1:
        st.metric(label="📈 Investment", value="₹0")
    with row2_col2:
        st.metric(label="💵 Balance", value="₹0")

# Add spacing
st.markdown("---")

# -------------------------
# Entry Form
# -------------------------
st.header("📝 Add New Transaction")

# Category selection outside the form to enable dynamic updates
col1, col2 = st.columns(2)
date = col1.date_input("Date", datetime.today())
category = col2.selectbox("Category", ["Income", "Expense", "Investment", "Other"])

# Dynamic subcategory dropdown based on selected category
subcategory_options = SUBCATEGORIES.get(category, [])
subcategory = st.selectbox("Subcategory", subcategory_options)

with st.form("entry_form"):
    description = st.text_input("Description")
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    
    submitted = st.form_submit_button("Submit Entry")

    if submitted:
        new_row = [str(date), category, subcategory, description, amount]
        ws.append_row(new_row)
        st.success("Entry added successfully!")
