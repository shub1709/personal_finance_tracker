import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Daily Expense Tracker", page_icon="💰", layout="centered")

# Add custom CSS for mobile optimization
st.markdown("""
<style>
    /* Mobile-first responsive design */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Compact metric styling with colors */
    [data-testid="metric-container"] {
        padding: 0.3rem !important;
        border-radius: 0.4rem !important;
        margin: 0.15rem 0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
        border: 1px solid !important;
    }
    
    [data-testid="metric-container"] > div {
        width: fit-content !important;
        margin: auto !important;
        text-align: center !important;
    }
    
    /* Label styling - smaller font */
    [data-testid="metric-container"] label {
        font-size: 0.65rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.1rem !important;
        display: block !important;
    }
    
    /* Value styling - much smaller numbers */
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 0.35rem !important;
        font-weight: 400 !important;
        line-height: 1.1 !important;
    }
    
    /* Delta styling */
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        font-size: 0.55rem !important;
    }
    
    /* Color coding by position - Income (first metric) */
    [data-testid="metric-container"]:nth-of-type(1) {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        border-color: #28a745 !important;
    }
    
    /* Expense (second metric) */
    [data-testid="metric-container"]:nth-of-type(2) {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        border-color: #dc3545 !important;
    }
    
    /* Investment (third metric) */
    [data-testid="metric-container"]:nth-of-type(3) {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%) !important;
        border-color: #17a2b8 !important;
    }
    
    /* Balance (fourth metric) */
    [data-testid="metric-container"]:nth-of-type(4) {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%) !important;
        border-color: #ffc107 !important;
    }
    
    /* Compact headers */
    h4, h6, h7 {
        margin-bottom: 0.5rem !important;
        margin-top: 0.5rem !important;
    }
    
    /* Form spacing */
    .stForm {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 0.5rem;
    }
    
    /* Selectbox and input styling */
    .stSelectbox > div > div {
        font-size: 0.9rem;
    }
    
    .stTextInput > div > div {
        font-size: 0.9rem;
    }
    
    .stNumberInput > div > div {
        font-size: 0.9rem;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        font-size: 0.9rem;
    }
    
    /* Divider spacing */
    hr {
        margin: 1rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Google Sheets Connection
# ------------------------------
@st.cache_resource
def get_gsheet_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

# ------------------------------
# Subcategory Definitions
# ------------------------------
SUBCATEGORIES = {
    "Income": ["Salary", "Freelancing", "Business Income", "Rental Income", "Interest/Dividends", "Bonus", "Gift/Inheritance", "Other Income"],
    "Expense": ["Food & Dining", "Groceries", "Transportation", "Utilities", "Rent/EMI", "Healthcare", "Entertainment", "Shopping", "Education", "Insurance", "Travel", "Personal Care", "Other Expense"],
    "Investment": ["Mutual Funds", "Stocks", "Fixed Deposits", "PPF", "EPF", "Gold", "Real Estate", "Crypto", "Bonds", "Other Investment"],
    "Other": ["Transfer", "Loan Given", "Loan Received", "Tax Payment", "Miscellaneous"]
}

client = get_gsheet_connection()
sheet = client.open("MyFinanceTracker")
ws = sheet.worksheet("Tracker")

# ------------------------------
# Title and Monthly Summary
# ------------------------------
st.markdown("<h4 style='text-align: center; font-size: 1.3rem;'>💸 Daily Tracker</h4>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center; font-size: 1rem;'>📊 Monthly Summary</h6>", unsafe_allow_html=True)

# Load data
data = ws.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

    # Compact year/month selection
    col1, col2 = st.columns(2)
    with col1:
        years = sorted(df["Date"].dt.year.unique(), reverse=True)
        selected_year = st.selectbox("Year", years, index=0)
    with col2:
        year_df = df[df["Date"].dt.year == selected_year]
        months = sorted(year_df["Date"].dt.month.unique())
        month_names = [datetime(2000, m, 1).strftime('%B') for m in months]
        selected_month_name = st.selectbox("Month", month_names, index=len(month_names)-1)
        selected_month = datetime.strptime(selected_month_name, "%B").month

    month_df = df[(df["Date"].dt.year == selected_year) & (df["Date"].dt.month == selected_month)]

    # Calculate metrics
    income = month_df[month_df["Category"] == "Income"]["Amount (₹)"].sum()
    expense = month_df[month_df["Category"] == "Expense"]["Amount (₹)"].sum()
    invest = month_df[month_df["Category"] == "Investment"]["Amount (₹)"].sum()
    savings = income - expense - invest

    st.markdown(f"<div style='text-align: center; font-size: 0.9rem; margin: 0.5rem 0;'>📅 {selected_month_name} {selected_year}</div>", unsafe_allow_html=True)

    # True 2x2 grid layout for metrics
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row1_col1:
        st.metric("💰 Income", f"₹{income:,.0f}")
        
    with row1_col2:
        st.metric("💸 Expense", f"₹{expense:,.0f}")
        
    with row2_col1:
        st.metric("📈 Investment", f"₹{invest:,.0f}")
        
    with row2_col2:
        st.metric("💵 Balance", f"₹{savings:,.0f}", delta_color="inverse" if savings < 0 else "normal")

else:
    # Empty state with 2x2 grid
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row1_col1:
        st.metric("💰 Income", "₹0")
        
    with row1_col2:
        st.metric("💸 Expense", "₹0")
        
    with row2_col1:
        st.metric("📈 Investment", "₹0")
        
    with row2_col2:
        st.metric("💵 Balance", "₹0")

st.markdown("---")

# ------------------------------
# Transaction Entry Form
# ------------------------------
st.markdown("<h6 style='text-align: center; font-size: 1rem;'>📝 Add New Entry</h6>", unsafe_allow_html=True)

# Initialize form state
if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

if st.session_state["form_submitted"]:
    st.session_state["description"] = ""
    st.session_state["amount"] = 0.0
    st.session_state["form_submitted"] = False

# Compact form layout
col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Date", datetime.today())
with col2:
    category = st.selectbox("Category", list(SUBCATEGORIES.keys()))

subcategory = st.selectbox("Subcategory", SUBCATEGORIES[category])

with st.form("entry_form"):
    description = st.text_input("Description", key="description")
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f", key="amount")

    submitted = st.form_submit_button("Submit Entry")
    if submitted:
        ws.append_row([str(date), category, subcategory, description, amount])
        st.success("✅ Entry added!")
        st.session_state["form_submitted"] = True
        st.rerun()
