import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# MUST BE FIRST - Set page config
st.set_page_config(page_title="💰 Finance Tracker", layout="centered", initial_sidebar_state="collapsed")

# Mobile-optimized CSS with reduced font sizes
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
    
    /* Reduced font sizes for headings */
    h1 { font-size: 1.1rem !important; margin: 0.4rem 0 !important; }
    h2 { font-size: 0.95rem !important; margin: 0.3rem 0 !important; }
    h3 { font-size: 0.85rem !important; margin: 0.25rem 0 !important; }
    
    /* Reduced label font sizes */
    .stSelectbox label, .stDateInput label, .stTextInput label, .stNumberInput label {
        font-size: 0.8rem !important;
    }
    
    /* Tab font sizes */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.85rem !important;
    }
    
    /* Form button */
    .stButton button {
        font-size: 0.85rem !important;
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
        # Add row index for getting last 5 entries
        df = df.reset_index(drop=True)
    return df, ws

st.title("💸 Finance Tracker")

# Load data
df, ws = load_data()

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

# Initialize session state for form reset
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

# Initialize session state for form data
if 'form_category' not in st.session_state:
    st.session_state.form_category = "Expense"

# CREATE TABS HERE
tab1, tab2 = st.tabs(["📝 Add Transaction", "📊 Summary & Analytics"])

# -------------------------
# TAB 1: ADD TRANSACTION
# -------------------------
with tab1:
    st.header("📝 Add New Transaction")
    
    # Form inputs OUTSIDE the form to enable dynamic updates
    col1, col2 = st.columns(2)
    date = col1.date_input("Date", datetime.today())
    
    # Category selection with callback to update subcategories
    category = col2.selectbox(
        "Category", 
        ["Expense", "Income", "Investment", "Other"],
        index=["Expense", "Income", "Investment", "Other"].index(st.session_state.form_category),
        key="category_select"
    )
    
    # Update session state when category changes
    if category != st.session_state.form_category:
        st.session_state.form_category = category
    
    # Dynamic subcategory based on selected category
    subcategory_options = SUBCATEGORIES.get(category, [])
    subcategory = st.selectbox("Subcategory", subcategory_options)
    
    description = st.text_input("Description")
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.0f")
    
    # Submit button outside form for immediate response
    if st.button("💾 Add Transaction", use_container_width=True):
        if amount > 0:
            new_row = [str(date), category, subcategory, description, amount]
            ws.append_row(new_row)
            
            # Clear cache to refresh data
            st.cache_data.clear()
            
            # Increment form key to reset form
            st.session_state.form_key += 1
            
            st.success("✅ Transaction added successfully!")
            st.balloons()
            
            # Auto-refresh the page after successful entry
            st.rerun()
        else:
            st.error("Please enter a valid amount greater than 0")
    
    # Show recent transactions in the add transaction tab for reference
    if not df.empty:
        st.markdown("---")
        st.subheader("🕒 Last 5 Transactions")
        
        # Get last 5 rows from the dataframe (most recent entries by index)
        recent_df = df.tail(5).iloc[::-1]  # Get last 5 and reverse order to show newest first
        
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
            total_investment = selected_period_df[selected_period_df["Category"] == "Investment"]["Amount (₹)"].sum()
            net_savings = total_income - total_expense - total_investment
            
            # Display selected period
            st.subheader(f"📅 {analysis_period}")
            
            # Custom grid
            grid_html = f"""
            <div class="custom-grid">
                {create_custom_metric_card("💰 Income", f"₹{total_income:,.0f}", "income")}
                {create_custom_metric_card("💸 Expense", f"₹{total_expense:,.0f}", "expense")}
                {create_custom_metric_card("📈 Investment", f"₹{total_investment:,.0f}", "investment")}
                {create_custom_metric_card("💵 Balance", f"₹{net_savings:,.0f}", "balance")}
            
            """
            st.markdown(grid_html, unsafe_allow_html=True)
        else:
            st.warning("Please select at least one month to view summary")
            selected_period_df = pd.DataFrame()  # Empty dataframe for charts section
        

        
        # -------------------------
        # Charts Section (Bar charts for all categories)
        # -------------------------
        if selected_months and not selected_period_df.empty:
            st.header("📈 Analytics")
            
            # Chart tabs for Income, Expenses, and Investments
            chart_tab1, chart_tab2, chart_tab3 = st.tabs(["💸 Expenses", "💰 Income", "📈 Investments"])

            with chart_tab1:
                expense_df = selected_period_df[selected_period_df["Category"] == "Expense"]
                if not expense_df.empty:
                    expense_by_subcat = expense_df.groupby("Subcategory")["Amount (₹)"].sum().reset_index()
                    expense_by_subcat = expense_by_subcat.sort_values("Amount (₹)", ascending=False)
                    
                    # Add formatted labels for better readability
                    expense_by_subcat['Amount_Label'] = expense_by_subcat['Amount (₹)'].apply(format_amount)
                    
                    fig_exp = px.bar(expense_by_subcat, 
                                   x="Subcategory", 
                                   y="Amount (₹)",
                                   title="Expense Breakdown",
                                   text="Amount_Label")
                    fig_exp.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
                    fig_exp.update_traces(textposition='outside', marker_color='#dc3545')
                    # Adjust y-axis to accommodate labels
                    max_value = expense_by_subcat['Amount (₹)'].max()
                    fig_exp.update_yaxes(range=[0, max_value * 1.15])
                    st.plotly_chart(fig_exp, use_container_width=True)
                    
                    # Top expenses
                    st.subheader("🔝 Top Expenses")
                    for _, row in expense_by_subcat.head(5).iterrows():
                        st.write(f"**{row['Subcategory']}**: ₹{row['Amount (₹)']:,.0f}")
                else:
                    st.info("No expense data for selected period")


            with chart_tab2:
                income_df = selected_period_df[selected_period_df["Category"] == "Income"]
                if not income_df.empty:
                    income_by_subcat = income_df.groupby("Subcategory")["Amount (₹)"].sum().reset_index()
                    income_by_subcat = income_by_subcat.sort_values("Amount (₹)", ascending=False)
                    
                    # Add formatted labels for better readability
                    income_by_subcat['Amount_Label'] = income_by_subcat['Amount (₹)'].apply(format_amount)
                    
                    fig_inc = px.bar(income_by_subcat, 
                                   x="Subcategory", 
                                   y="Amount (₹)",
                                   title="Income Breakdown",
                                   text="Amount_Label")
                    fig_inc.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
                    fig_inc.update_traces(textposition='outside', marker_color='#28a745')
                    # Adjust y-axis to accommodate labels
                    max_value = income_by_subcat['Amount (₹)'].max()
                    fig_inc.update_yaxes(range=[0, max_value * 1.15])
                    st.plotly_chart(fig_inc, use_container_width=True)
                    
                    # Income summary
                    st.subheader("💰 Income Summary")
                    for _, row in income_by_subcat.iterrows():
                        st.write(f"**{row['Subcategory']}**: ₹{row['Amount (₹)']:,.0f}")
                else:
                    st.info("No income data for selected period")
            

            
            with chart_tab3:
                investment_df = selected_period_df[selected_period_df["Category"] == "Investment"]
                if not investment_df.empty:
                    investment_by_subcat = investment_df.groupby("Subcategory")["Amount (₹)"].sum().reset_index()
                    investment_by_subcat = investment_by_subcat.sort_values("Amount (₹)", ascending=False)
                    
                    # Add formatted labels for better readability
                    investment_by_subcat['Amount_Label'] = investment_by_subcat['Amount (₹)'].apply(format_amount)
                    
                    fig_inv = px.bar(investment_by_subcat, 
                                   x="Subcategory", 
                                   y="Amount (₹)",
                                   title="Investment Breakdown",
                                   text="Amount_Label")
                    fig_inv.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
                    fig_inv.update_traces(textposition='outside', marker_color='#007bff')
                    # Adjust y-axis to accommodate labels
                    max_value = investment_by_subcat['Amount (₹)'].max()
                    fig_inv.update_yaxes(range=[0, max_value * 1.15])
                    st.plotly_chart(fig_inv, use_container_width=True)
                    
                    # Investment summary
                    st.subheader("💼 Investment Summary")
                    for _, row in investment_by_subcat.iterrows():
                        st.write(f"**{row['Subcategory']}**: ₹{row['Amount (₹)']:,.0f}")
                else:
                    st.info("No investment data for selected period")

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
        st.info("No transactions recorded yet. Add your first transaction in the 'Add Transaction' tab!")
