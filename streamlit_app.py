import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# MUST BE FIRST - Set page config before any other Streamlit commands
st.set_page_config(page_title="💰 Personal Finance Tracker", layout="centered")

# Aggressive mobile-optimized CSS with multiple fallback strategies
st.markdown("""
<style>
    /* Reset and base styles */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
        max-width: 100%;
    }
    
    /* Custom grid container - override Streamlit's flex behavior */
    .custom-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        grid-template-rows: auto auto !important;
        gap: 0.5rem !important;
        width: 100% !important;
        margin: 1rem 0 !important;
    }
    
    .custom-grid > div {
        width: 100% !important;
        min-width: 0 !important;
        flex: none !important;
    }
    
    /* Force override Streamlit's column behavior */
    .stHorizontal {
        display: none !important;
    }
    
    /* Hide default Streamlit columns when we use custom grid */
    .custom-grid-active div[data-testid="column"] {
        display: none !important;
    }
    
    /* Style metric containers */
    .custom-metric {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 2px solid #e0e0e0;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .custom-metric:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .custom-metric .metric-label {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #6c757d;
    }
    
    .custom-metric .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #333;
    }
    
    /* Color coding for different metrics */
    .metric-income {
        background: linear-gradient(135deg, #d4edda, #c3e6cb) !important;
        border-color: #28a745 !important;
    }
    
    .metric-expense {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb) !important;
        border-color: #dc3545 !important;
    }
    
    .metric-investment {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb) !important;
        border-color: #17a2b8 !important;
    }
    
    .metric-balance {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7) !important;
        border-color: #ffc107 !important;
    }
    
    /* Mobile specific - even more aggressive */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.25rem;
            padding-right: 0.25rem;
        }
        
        .custom-grid {
            gap: 0.25rem !important;
        }
        
        .custom-metric {
            padding: 0.75rem;
            min-height: 90px;
        }
        
        .custom-metric .metric-value {
            font-size: 1.2rem;
        }
    }
    
    /* Reduce header sizes */
    h1 { font-size: 1.5rem; margin: 0.5rem 0; }
    h2 { font-size: 1.25rem; margin: 0.5rem 0; }
    h3 { font-size: 1.1rem; margin: 0.5rem 0; }
    
    /* Form styling */
    .stSelectbox label, .stDateInput label, .stTextInput label, .stNumberInput label {
        font-size: 0.9rem;
    }
    
    /* Custom selector grid - similar to metrics grid */
    .selector-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 0.5rem !important;
        width: 100% !important;
        margin: 0.5rem 0 !important;
    }
    
    .selector-grid > div {
        width: 100% !important;
        min-width: 0 !important;
    }
    
    .custom-selector {
        width: 100% !important;
    }
    
    .custom-selector label {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.25rem !important;
        display: block !important;
        color: #333 !important;
    }
    
    .custom-selector select {
        width: 100% !important;
        padding: 0.5rem !important;
        border: 1px solid #ccc !important;
        border-radius: 6px !important;
        font-size: 0.9rem !important;
        background-color: white !important;
    }
    
    /* Mobile specific for selectors */
    @media (max-width: 768px) {
        .selector-grid {
            gap: 0.25rem !important;
        }
        
        .custom-selector select {
            padding: 0.4rem !important;
            font-size: 0.85rem !important;
        }
    }
    
    /* Hide original Streamlit selectors when using custom grid */
    .selector-grid-active .stSelectbox {
        display: none !important;
    }
    
    /* Hide any potential Streamlit column containers in grid section */
    .grid-section .stHorizontal,
    .grid-section div[data-testid="column"] {
        display: none !important;
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

# Custom metric component function
def create_custom_metric_card(label, value, metric_type):
    return f"""
    <div class="custom-metric metric-{metric_type}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

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
    
    # Month and Year selection with aggressive mobile CSS
    st.markdown("""
    <style>
        .year-month-container {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 0.5rem !important;
            width: 50% !important;
        }
        
        .year-month-container > div {
            width: 50% !important;
            min-width: 0 !important;
        }
        
        /* Override ALL Streamlit responsive behavior for this section */
        .year-month-container .stHorizontal,
        .year-month-container .row-widget {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 0.5rem !important;
            width: 50% !important;
        }
        
        .year-month-container div[data-testid="column"] {
            width: 50% !important;
            flex: none !important;
            min-width: 0 !important;
            max-width: none !important;
        }
        
        /* Force on mobile - most aggressive approach */
        @media (max-width: 768px) {
            .year-month-container .stHorizontal,
            .year-month-container .row-widget {
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 0.25rem !important;
            }
            
            .year-month-container div[data-testid="column"] {
                width: 50% !important;
                display: block !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="year-month-container">', unsafe_allow_html=True)
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filter for selected month and year
    selected_month_df = df[(df["Date"].dt.month == selected_month) & (df["Date"].dt.year == selected_year)]
    
    # Calculate totals for selected month
    total_income = selected_month_df[selected_month_df["Category"] == "Income"]["Amount (₹)"].sum()
    total_expense = selected_month_df[selected_month_df["Category"] == "Expense"]["Amount (₹)"].sum()
    total_investment = selected_month_df[selected_month_df["Category"] == "Investment"]["Amount (₹)"].sum()
    net_savings = total_income - total_expense - total_investment
    
    # Display selected month/year
    st.subheader(f"📅 {selected_month_name} {selected_year}")
    
    # Create custom 2x2 grid using HTML - completely bypass Streamlit columns
    grid_html = f"""
    <div class="custom-grid">
        {create_custom_metric_card("💰 Income", f"₹{total_income:,.0f}", "income")}
        {create_custom_metric_card("💸 Expense", f"₹{total_expense:,.0f}", "expense")}
        {create_custom_metric_card("📈 Investment", f"₹{total_investment:,.0f}", "investment")}
        {create_custom_metric_card("💵 Balance", f"₹{net_savings:,.0f}", "balance")}
    </div>
    """
    
    st.markdown(grid_html, unsafe_allow_html=True)
        
else:
    # Show empty cards if no data
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

# Add JavaScript to ensure grid stays intact
st.markdown("""
<script>
function enforceCustomGrid() {
    // Hide any Streamlit columns that might interfere
    const columns = document.querySelectorAll('div[data-testid="column"]');
    columns.forEach(col => {
        const parent = col.closest('.custom-grid');
        if (!parent) {
            // Only hide columns that are not part of our custom grid
            const hasGridSibling = col.parentElement && col.parentElement.querySelector('.custom-grid');
            if (hasGridSibling) {
                col.style.display = 'none';
            }
        }
    });
    
    // Ensure our custom grid maintains its structure
    const grids = document.querySelectorAll('.custom-grid');
    grids.forEach(grid => {
        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = '1fr 1fr';
        grid.style.gridTemplateRows = 'auto auto';
    });
}

// Run immediately and on any DOM changes
enforceCustomGrid();
const observer = new MutationObserver(enforceCustomGrid);
observer.observe(document.body, { childList: true, subtree: true });

// Also run on resize
window.addEventListener('resize', enforceCustomGrid);

// Additional function to enforce year-month row layout
function enforceYearMonthLayout() {
    const container = document.querySelector('.year-month-container');
    if (container) {
        // Force the container to be a grid
        container.style.display = 'grid';
        container.style.gridTemplateColumns = '1fr 1fr';
        container.style.gap = '0.5rem';
        container.style.width = '50%';
        
        // Find and force the horizontal container
        const horizontalContainer = container.querySelector('.stHorizontal, .row-widget');
        if (horizontalContainer) {
            horizontalContainer.style.display = 'grid';
            horizontalContainer.style.gridTemplateColumns = '1fr 1fr';
            horizontalContainer.style.gap = '0.5rem';
            horizontalContainer.style.width = '100%';
        }
        
        // Force columns to stay side by side
        const columns = container.querySelectorAll('[data-testid="column"]');
        columns.forEach(col => {
            col.style.width = '100%';
            col.style.flex = 'none';
            col.style.minWidth = '0';
            col.style.maxWidth = 'none';
            col.style.display = 'block';
        });
    }
}

// Run both functions more frequently for mobile
setInterval(() => {
    enforceCustomGrid();
    enforceYearMonthLayout();
}, 50);  // More frequent checks
</script>
""", unsafe_allow_html=True)

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
