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
    
    /* Year-Month selector grid - COMPLETELY CUSTOM */
    .year-month-selector {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 0.5rem !important;
        width: 100% !important;
        margin: 1rem 0 !important;
        max-width: 400px !important;
    }
    
    .year-month-selector > div {
        width: 100% !important;
        min-width: 0 !important;
    }
    
    .custom-select-container {
        width: 100% !important;
    }
    
    .custom-select-container label {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.25rem !important;
        display: block !important;
        color: #333 !important;
    }
    
    .custom-select {
        width: 100% !important;
        padding: 0.5rem !important;
        border: 1px solid #ccc !important;
        border-radius: 6px !important;
        font-size: 0.9rem !important;
        background-color: white !important;
        appearance: none !important;
        background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e") !important;
        background-position: right 0.5rem center !important;
        background-repeat: no-repeat !important;
        background-size: 1rem !important;
        padding-right: 2rem !important;
    }
    
    .custom-select:focus {
        outline: none !important;
        border-color: #007bff !important;
        box-shadow: 0 0 0 2px rgba(0,123,255,0.25) !important;
    }
    
    /* Mobile specific for selectors */
    @media (max-width: 768px) {
        .year-month-selector {
            gap: 0.25rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .custom-select {
            padding: 0.4rem !important;
            font-size: 0.85rem !important;
            padding-right: 1.75rem !important;
        }
    }
    
    /* Hide ALL Streamlit columns and horizontal containers in selector area */
    .selector-area .stHorizontal,
    .selector-area div[data-testid="column"],
    .selector-area .row-widget {
        display: none !important;
    }
    
    /* Additional form styling for entry section */
    .entry-form-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 0.5rem !important;
        width: 100% !important;
        margin: 0.5rem 0 !important;
    }
    
    .entry-form-grid > div {
        width: 100% !important;
        min-width: 0 !important;
    }
    
    @media (max-width: 768px) {
        .entry-form-grid {
            gap: 0.25rem !important;
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

st.title("💸 Daily Tracker")

# -------------------------
# Monthly Summary Cards
# -------------------------
st.header("📊 Monthly Summary")

# Load data
data = ws.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Create year and month options for HTML selects
    available_years = sorted(df["Date"].dt.year.unique(), reverse=True)
    default_year = datetime.now().year if datetime.now().year in available_years else available_years[-1]
    
    # Get months available for the default year
    year_data = df[df["Date"].dt.year == default_year]
    available_months = sorted(year_data["Date"].dt.month.unique())
    month_names = [datetime(2000, month, 1).strftime('%B') for month in available_months]
    
    # Set default to current month if available, otherwise first available month
    current_month = datetime.now().month
    if current_month in available_months and default_year == datetime.now().year:
        default_month_index = available_months.index(current_month)
    else:
        default_month_index = 0 if available_months else 0
    
    # Create year options HTML
    year_options = ""
    for year in available_years:
        selected = "selected" if year == default_year else ""
        year_options += f'<option value="{year}" {selected}>{year}</option>'
    
    # Create month options HTML
    month_options = ""
    for i, month_name in enumerate(month_names):
        selected = "selected" if i == default_month_index else ""
        month_options += f'<option value="{month_name}" {selected}>{month_name}</option>'
    
    # Create pure HTML selector grid
    selector_html = f"""
    <div class="selector-area">
        <div class="year-month-selector">
            <div class="custom-select-container">
                <label for="year-select">Select Year</label>
                <select id="year-select" class="custom-select" onchange="updateMonths()">
                    {year_options}
                </select>
            </div>
            <div class="custom-select-container">
                <label for="month-select">Select Month</label>
                <select id="month-select" class="custom-select" onchange="updateSummary()">
                    {month_options}
                </select>
            </div>
        </div>
    </div>
    """
    
    st.markdown(selector_html, unsafe_allow_html=True)
    
    # Get initial selected values for summary
    selected_year = default_year
    selected_month = available_months[default_month_index] if available_months else datetime.now().month
    selected_month_name = month_names[default_month_index] if month_names else datetime.now().strftime('%B')
    
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
    
    # Show empty selector
    empty_selector_html = f"""
    <div class="selector-area">
        <div class="year-month-selector">
            <div class="custom-select-container">
                <label for="year-select">Select Year</label>
                <select id="year-select" class="custom-select" disabled>
                    <option>{datetime.now().year}</option>
                </select>
            </div>
            <div class="custom-select-container">
                <label for="month-select">Select Month</label>
                <select id="month-select" class="custom-select" disabled>
                    <option>{datetime.now().strftime('%B')}</option>
                </select>
            </div>
        </div>
    </div>
    """
    
    st.markdown(empty_selector_html, unsafe_allow_html=True)
    
    grid_html = f"""
    <div class="custom-grid">
        {create_custom_metric_card("💰 Income", "₹0", "income")}
        {create_custom_metric_card("💸 Expense", "₹0", "expense")}
        {create_custom_metric_card("📈 Investment", "₹0", "investment")}
        {create_custom_metric_card("💵 Balance", "₹0", "balance")}
    </div>
    """
    
    st.markdown(grid_html, unsafe_allow_html=True)

# Add JavaScript for dynamic updates and grid enforcement
st.markdown("""
<script>
// Data for JavaScript (passed from Python)
const dfData = """ + (df.to_json(orient='records', date_format='iso') if not df.empty else "[]") + """;

function updateMonths() {
    const yearSelect = document.getElementById('year-select');
    const monthSelect = document.getElementById('month-select');
    const selectedYear = parseInt(yearSelect.value);
    
    // Filter data for selected year
    const yearData = dfData.filter(row => new Date(row.Date).getFullYear() === selectedYear);
    
    // Get unique months for the year
    const months = [...new Set(yearData.map(row => new Date(row.Date).getMonth() + 1))].sort();
    const monthNames = months.map(month => new Date(2000, month - 1, 1).toLocaleDateString('en-US', { month: 'long' }));
    
    // Update month dropdown
    monthSelect.innerHTML = '';
    monthNames.forEach((monthName, index) => {
        const option = document.createElement('option');
        option.value = monthName;
        option.textContent = monthName;
        if (index === 0) option.selected = true;
        monthSelect.appendChild(option);
    });
    
    updateSummary();
}

function updateSummary() {
    const yearSelect = document.getElementById('year-select');
    const monthSelect = document.getElementById('month-select');
    
    if (!yearSelect || !monthSelect) return;
    
    const selectedYear = parseInt(yearSelect.value);
    const selectedMonthName = monthSelect.value;
    const selectedMonth = new Date(selectedMonthName + ' 1, 2000').getMonth() + 1;
    
    // Filter data for selected month and year
    const monthData = dfData.filter(row => {
        const date = new Date(row.Date);
        return date.getFullYear() === selectedYear && date.getMonth() + 1 === selectedMonth;
    });
    
    // Calculate totals
    const totalIncome = monthData.filter(row => row.Category === 'Income')
        .reduce((sum, row) => sum + parseFloat(row['Amount (₹)'] || 0), 0);
    const totalExpense = monthData.filter(row => row.Category === 'Expense')
        .reduce((sum, row) => sum + parseFloat(row['Amount (₹)'] || 0), 0);
    const totalInvestment = monthData.filter(row => row.Category === 'Investment')
        .reduce((sum, row) => sum + parseFloat(row['Amount (₹)'] || 0), 0);
    const netSavings = totalIncome - totalExpense - totalInvestment;
    
    // Update the display (this would require Streamlit rerun for actual update)
    // For now, we'll just update the title
    const titleElement = document.querySelector('h3');
    if (titleElement && titleElement.textContent.includes('📅')) {
        titleElement.textContent = `📅 ${selectedMonthName} ${selectedYear}`;
    }
}

function enforceCustomGrid() {
    // Hide any Streamlit columns that might interfere
    const columns = document.querySelectorAll('div[data-testid="column"]');
    columns.forEach(col => {
        const parent = col.closest('.custom-grid, .year-month-selector, .selector-area');
        if (parent) {
            col.style.display = 'none';
        }
    });
    
    // Hide horizontal containers in selector area
    const selectorArea = document.querySelector('.selector-area');
    if (selectorArea) {
        const horizontalDivs = selectorArea.querySelectorAll('.stHorizontal, .row-widget');
        horizontalDivs.forEach(div => {
            div.style.display = 'none';
        });
    }
    
    // Ensure our custom grids maintain their structure
    const grids = document.querySelectorAll('.custom-grid, .year-month-selector');
    grids.forEach(grid => {
        if (grid.classList.contains('custom-grid')) {
            grid.style.display = 'grid';
            grid.style.gridTemplateColumns = '1fr 1fr';
            grid.style.gridTemplateRows = 'auto auto';
        } else if (grid.classList.contains('year-month-selector')) {
            grid.style.display = 'grid';
            grid.style.gridTemplateColumns = '1fr 1fr';
            grid.style.gap = window.innerWidth <= 768 ? '0.25rem' : '0.5rem';
        }
    });
}

// Run immediately and on any DOM changes
enforceCustomGrid();
const observer = new MutationObserver(enforceCustomGrid);
observer.observe(document.body, { childList: true, subtree: true });

// Also run on resize
window.addEventListener('resize', enforceCustomGrid);

// More frequent checks for mobile
setInterval(enforceCustomGrid, 100);
</script>
""", unsafe_allow_html=True)

# Add spacing
st.markdown("---")

# -------------------------
# Entry Form
# -------------------------
st.header("📝 Add New Transaction")

# Create HTML grid for date and category selection - NO st.columns!
st.markdown('<div class="entry-form-grid">', unsafe_allow_html=True)

# Date input (left side)
date = st.date_input("Date", datetime.today())

# Category selection (right side) 
category = st.selectbox("Category", ["Income", "Expense", "Investment", "Other"])

st.markdown('</div>', unsafe_allow_html=True)

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
