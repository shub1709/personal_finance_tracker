import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# MUST BE FIRST - Set page config
st.set_page_config(page_title="💰 Finance Tracker", layout="centered", initial_sidebar_state="collapsed")

# Mobile-optimized CSS
st.markdown("""
<style>    
    .main .block-container {
        padding: 1rem 0.5rem;
        max-width: 100%;
    }
    
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
    
    .metric-income { background: linear-gradient(135deg, #d4edda, #a8e6a3) !important; }
    .metric-expense { background: linear-gradient(135deg, #f8d7da, #f5b7b1) !important; }
    .metric-investment { background: linear-gradient(135deg, #d1ecf1, #a3d5db) !important; }
    .metric-balance { background: linear-gradient(135deg, #fff3cd, #ffeaa7) !important; }
    
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
    
    @media (max-width: 768px) {
        .main .block-container { padding: 0.5rem 0.25rem; }
        .custom-grid { gap: 0.25rem !important; }
        .custom-metric { padding: 0.6rem; min-height: 70px; }
        .custom-metric .metric-value { font-size: 1rem; }
    }
    
    h1 { font-size: 1.4rem; margin: 0.5rem 0; }
    h2 { font-size: 1.2rem; margin: 0.4rem 0; }
    h3 { font-size: 1rem; margin: 0.3rem 0; }
    
    .stSelectbox label, .stDateInput label, .stTextInput label, .stNumberInput label {
        font-size: 0.85rem;
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

# Load data with caching
@st.cache_data(ttl=60)  # Cache for 1 minute
def load_data():
    client = get_gsheet_connection()
    sheet = client.open("MyFinanceTracker")
    ws = sheet.worksheet("Tracker")
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date", ascending=False)  # Sort by date descending
    return df, ws

# Initialize session state for form reset
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

st.title("💸 Finance Tracker")

# Load data
df, ws = load_data()

# -------------------------
# Monthly Summary Cards
# -------------------------
st.header("📊 Monthly Summary")

if not df.empty:
    # Current month data
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_month_df = df[(df["Date"].dt.month == current_month) & (df["Date"].dt.year == current_year)]
    
    # Calculate totals
    total_income = current_month_df[current_month_df["Category"] == "Income"]["Amount (₹)"].sum()
    total_expense = current_month_df[current_month_df["Category"] == "Expense"]["Amount (₹)"].sum()
    total_investment = current_month_df[current_month_df["Category"] == "Investment"]["Amount (₹)"].sum()
    net_savings = total_income - total_expense - total_investment
    
    # Display current month
    st.subheader(f"📅 {datetime.now().strftime('%B %Y')}")
    
    # Custom grid
    grid_html = f"""
    <div class="custom-grid">
        {create_custom_metric_card("💰 Income", f"₹{total_income:,.0f}", "income")}
        {create_custom_metric_card("💸 Expense", f"₹{total_expense:,.0f}", "expense")}
        {create_custom_metric_card("📈 Investment", f"₹{total_investment:,.0f}", "investment")}
        {create_custom_metric_card("💵 Balance", f"₹{net_savings:,.0f}", "balance")}
    </div>
    """
    st.markdown(grid_html, unsafe_allow_html=True)
    
    # -------------------------
    # Recent Transactions
    # -------------------------
    st.header("🕒 Last 5 Transactions")
    
    recent_df = df.head(5)
    for _, row in recent_df.iterrows():
        date_str = row["Date"].strftime("%d %b")
        category_color = {"Income": "#28a745", "Expense": "#dc3545", "Investment": "#007bff", "Other": "#6c757d"}
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
    # Charts Section
    # -------------------------
    st.header("📈 Analytics")
    
    # Chart tabs
    chart_tab1, chart_tab2 = st.tabs(["💸 Expenses", "📈 Investments"])
    
    with chart_tab1:
        expense_df = current_month_df[current_month_df["Category"] == "Expense"]
        if not expense_df.empty:
            expense_by_subcat = expense_df.groupby("Subcategory")["Amount (₹)"].sum().reset_index()
            expense_by_subcat = expense_by_subcat.sort_values("Amount (₹)", ascending=False)
            
            fig_exp = px.pie(expense_by_subcat, 
                           values="Amount (₹)", 
                           names="Subcategory",
                           title="Expense Breakdown",
                           color_discrete_sequence=px.colors.qualitative.Set3)
            fig_exp.update_layout(height=400, showlegend=False)
            fig_exp.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_exp, use_container_width=True)
            
            # Top expenses
            st.subheader("🔝 Top Expenses")
            for _, row in expense_by_subcat.head(3).iterrows():
                st.write(f"**{row['Subcategory']}**: ₹{row['Amount (₹)']:,.0f}")
        else:
            st.info("No expense data for current month")
    
    with chart_tab2:
        investment_df = current_month_df[current_month_df["Category"] == "Investment"]
        if not investment_df.empty:
            investment_by_subcat = investment_df.groupby("Subcategory")["Amount (₹)"].sum().reset_index()
            investment_by_subcat = investment_by_subcat.sort_values("Amount (₹)", ascending=False)
            
            fig_inv = px.bar(investment_by_subcat, 
                           x="Subcategory", 
                           y="Amount (₹)",
                           title="Investment Breakdown",
                           color="Amount (₹)",
                           color_continuous_scale="Blues")
            fig_inv.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_inv, use_container_width=True)
            
            # Investment summary
            st.subheader("💼 Investment Summary")
            for _, row in investment_by_subcat.iterrows():
                st.write(f"**{row['Subcategory']}**: ₹{row['Amount (₹)']:,.0f}")
        else:
            st.info("No investment data for current month")

else:
    # Empty state
    st.subheader(f"📅 {datetime.now().strftime('%B %Y')}")
    grid_html = f"""
    <div class="custom-grid">
        {create_custom_metric_card("💰 Income", "₹0", "income")}
        {create_custom_metric_card("💸 Expense", "₹0", "expense")}
        {create_custom_metric_card("📈 Investment", "₹0", "investment")}
        {create_custom_metric_card("💵 Balance", "₹0", "balance")}
    </div>
    """
    st.markdown(grid_html, unsafe_allow_html=True)
    st.info("No transactions recorded yet. Add your first transaction below!")

st.markdown("---")

# -------------------------
# Entry Form
# -------------------------
st.header("📝 Add Transaction")

# Form with dynamic key for reset
with st.form(key=f"entry_form_{st.session_state.form_key}"):
    col1, col2 = st.columns(2)
    date = col1.date_input("Date", datetime.today())
    category = col2.selectbox("Category", ["Income", "Expense", "Investment", "Other"])
    
    subcategory_options = SUBCATEGORIES.get(category, [])
    subcategory = st.selectbox("Subcategory", subcategory_options)
    
    description = st.text_input("Description")
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    
    submitted = st.form_submit_button("💾 Add Transaction", use_container_width=True)

    if submitted and amount > 0:
        new_row = [str(date), category, subcategory, description, amount]
        ws.append_row(new_row)
        
        # Clear cache to refresh data
        st.cache_data.clear()
        
        # Increment form key to reset form
        st.session_state.form_key += 1
        
        st.success("✅ Transaction added successfully!")
        st.balloons()
        
        # Auto-refresh the page
        st.rerun()
    elif submitted and amount <= 0:
        st.error("Please enter a valid amount greater than 0")

# Add refresh button
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
