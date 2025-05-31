import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# MUST BE FIRST - Set page config before any other Streamlit commands
st.set_page_config(page_title="💰 Personal Finance Tracker", layout="centered")

# Mobile-optimized CSS
st.markdown("""
<style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            max-width: 100%;
        }
    }
    
    /* Target metric containers - Updated selectors for newer Streamlit */
    [data-testid="metric-container"] {
        background-color: #f8f9fa !important;
        border: 2px solid #dee2e6 !important;
        padding: 1rem !important;
        border-radius: 0.75rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
    }
    
    /* Metric label styling */
    [data-testid="metric-container"] [data-testid="metric-label"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #495057 !important;
    }
    
    /* Metric value styling */
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: #212529 !important;
    }
    
    /* Income card - Green */
    .income-card [data-testid="metric-container"] {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        border-color: #28a745 !important;
    }
    
    .income-card [data-testid="metric-value"] {
        color: #155724 !important;
    }
    
    /* Expense card - Red */
    .expense-card [data-testid="metric-container"] {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        border-color: #dc3545 !important;
    }
    
    .expense-card [data-testid="metric-value"] {
        color: #721c24 !important;
    }
    
    /* Investment card - Blue */
    .investment-card [data-testid="metric-container"] {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%) !important;
        border-color: #17a2b8 !important;
    }
    
    .investment-card [data-testid="metric-value"] {
        color: #0c5460 !important;
    }
    
    /* Balance card - Yellow/Orange */
    .balance-card [data-testid="metric-container"] {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%) !important;
        border-color: #ffc107 !important;
    }
    
    .balance-card [data-testid="metric-value"] {
        color: #856404 !important;
    }
    
    /* Negative balance - Red theme */
    .balance-negative [data-testid="metric-container"] {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        border-color: #dc3545 !important;
    }
    
    .balance-negative [data-testid="metric-value"] {
        color: #721c24 !important;
    }
    
    /* Headers */
    h1 {
        font-size: 1.75rem !important;
        margin-bottom: 1rem !important;
    }
    
    h2 {
        font-size: 1.25rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    h3 {
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Form elements */
    .stSelectbox label, .stDateInput label, .stTextInput label, .stNumberInput label {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    .stButton button {
        font-size: 1rem !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
    }
    
    /* Column spacing for mobile */
    @media (max-width: 768px) {
        .row-widget.stHorizontal {
            gap: 0.5rem !important;
        }
        
        [data-testid="column"] {
            padding: 0.25rem !important;
        }
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
    
    # Display summary cards in 2x2 grid with proper CSS classes
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown('<div class="income-card">', unsafe_allow_html=True)
        st.metric(
            label="💰 Income",
            value=f"₹{total_income:,.0f}",
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with row1_col2:
        st.markdown('<div class="expense-card">', unsafe_allow_html=True)
        st.metric(
            label="💸 Expense",
            value=f"₹{total_expense:,.0f}",
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with row2_col1:
        st.markdown('<div class="investment-card">', unsafe_allow_html=True)
        st.metric(
            label="📈 Investment",
            value=f"₹{total_investment:,.0f}",
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with row2_col2:
        balance_class = "balance-card" if net_savings >= 0 else "balance-negative"
        st.markdown(f'<div class="{balance_class}">', unsafe_allow_html=True)
        st.metric(
            label="💵 Balance",
            value=f"₹{net_savings:,.0f}",
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
else:
    # Show empty cards if no data in 2x2 grid with colors
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown('<div class="income-card">', unsafe_allow_html=True)
        st.metric(label="💰 Income", value="₹0")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with row1_col2:
        st.markdown('<div class="expense-card">', unsafe_allow_html=True)
        st.metric(label="💸 Expense", value="₹0")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with row2_col1:
        st.markdown('<div class="investment-card">', unsafe_allow_html=True)
        st.metric(label="📈 Investment", value="₹0")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with row2_col2:
        st.markdown('<div class="balance-card">', unsafe_allow_html=True)
        st.metric(label="💵 Balance", value="₹0")
        st.markdown('</div>', unsafe_allow_html=True)

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
