import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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

st.set_page_config(page_title="💰 Personal Finance Tracker", layout="centered")

# ------------------------------
# Title and Monthly Summary
# ------------------------------
st.markdown("<h2 style='text-align: center;'>💸 Daily Tracker</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>📊 Monthly Summary</h4>", unsafe_allow_html=True)

# Load data
data = ws.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

    col1, col2 = st.columns(2)
    with col1:
        years = sorted(df["Date"].dt.year.unique(), reverse=True)
        selected_year = st.selectbox("Select Year", years, index=0)
    with col2:
        year_df = df[df["Date"].dt.year == selected_year]
        months = sorted(year_df["Date"].dt.month.unique())
        month_names = [datetime(2000, m, 1).strftime('%B') for m in months]
        selected_month_name = st.selectbox("Select Month", month_names, index=len(month_names)-1)
        selected_month = datetime.strptime(selected_month_name, "%B").month

    month_df = df[(df["Date"].dt.year == selected_year) & (df["Date"].dt.month == selected_month)]

    # Calculate metrics
    income = month_df[month_df["Category"] == "Income"]["Amount (₹)"].sum()
    expense = month_df[month_df["Category"] == "Expense"]["Amount (₹)"].sum()
    invest = month_df[month_df["Category"] == "Investment"]["Amount (₹)"].sum()
    savings = income - expense - invest

    st.markdown(f"<h5 style='text-align: center;'>📅 {selected_month_name} {selected_year}</h5>", unsafe_allow_html=True)

    # Responsive 2x2 metric layout
    row1, row2 = st.columns(2)
    with row1:
        st.metric("💰 Income", f"₹{income:,.0f}")
    with row2:
        st.metric("💸 Expense", f"₹{expense:,.0f}")

    row3, row4 = st.columns(2)
    with row3:
        st.metric("📈 Investment", f"₹{invest:,.0f}")
    with row4:
        st.metric("💵 Balance", f"₹{savings:,.0f}", delta_color="inverse" if savings < 0 else "normal")

else:
    for label in ["💰 Income", "💸 Expense", "📈 Investment", "💵 Balance"]:
        st.metric(label, "₹0")

st.markdown("---")

# ------------------------------
# Transaction Entry Form
# ------------------------------
st.markdown("<h4 style='text-align: center;'>📝 Add New Entry</h4>", unsafe_allow_html=True)

# Initialize form state
if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

if st.session_state["form_submitted"]:
    st.session_state["description"] = ""
    st.session_state["amount"] = 0.0
    st.session_state["form_submitted"] = False

# Outside form - for dynamic subcategory
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
        st.experimental_rerun()
