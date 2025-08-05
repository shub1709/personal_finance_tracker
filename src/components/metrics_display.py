import streamlit as st
from src.utils.formatters import format_amount, format_currency

class MetricsDisplay:
    """Component for displaying financial metrics"""
    
    @staticmethod
    def create_custom_metric_card(label: str, value: str, metric_type: str) -> str:
        """Create a custom metric card HTML"""
        return f"""
        <div class="custom-metric metric-{metric_type}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """
    
    @staticmethod
    def display_summary_metrics(totals: dict, total_investment_alltime: float = 0):
        """Display summary metrics in a grid layout"""
        
        # Format expense breakdown
        expense_breakdown = f"""₹{totals['expense']:,.0f}<br>
                            <small style='font-size: 0.7rem;'>
                                <span style='color: #2196f3'>{format_amount(totals['expense_shubham'])}</span> &nbsp;|&nbsp;
                                <span style='color: #e91e63;'>{format_amount(totals['expense_yashika'])}</span>
                            </small>"""
        
        # Format investment with total
        investment_display = f"₹{totals['investment']:,.0f}"
        if total_investment_alltime > 0:
            investment_display += f"<br><small style='font-size: 0.7rem; color: #666;'>Total: ₹{total_investment_alltime:,.0f}</small>"
        
        grid_html = f"""
        <div class="custom-grid">
            {MetricsDisplay.create_custom_metric_card("💸 Expense", expense_breakdown, "expense")}
            {MetricsDisplay.create_custom_metric_card("📈 Investment", investment_display, "investment")}            
            {MetricsDisplay.create_custom_metric_card("💰 Income", f"₹{totals['income']:,.0f}", "income")}
        </div>
        """
        st.markdown(grid_html, unsafe_allow_html=True)
    
    @staticmethod
    def display_leave_metrics(maid_leaves: int, cook_leaves: int):
        """Display leave metrics for domestic help"""
        leave_grid_html = f"""
        <div class="leave-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; width: 100%; margin: 1rem 0;">
            <div class="custom-metric" style="background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 50%, #f48fb1 100%);
                border: 0px solid #e91e63; box-shadow: 0 2px 10px rgba(233, 30, 99, 0.15);">
                <div class="metric-label">👩‍🍳 Maid Leaves</div>
                <div class="metric-value">{maid_leaves} days</div>
            </div>
            <div class="custom-metric" style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%);
                border: 0px solid #2196f3; box-shadow: 0 2px 10px rgba(33, 150, 243, 0.15);">
                <div class="metric-label">👨‍🍳 Cook Leaves</div>
                <div class="metric-value">{cook_leaves} days</div>
            </div>
        </div>
        """
        st.markdown(leave_grid_html, unsafe_allow_html=True)
    
    @staticmethod
    def display_empty_metrics():
        """Display empty metrics when no data is available"""
        grid_html = f"""
        <div class="custom-grid">
            {MetricsDisplay.create_custom_metric_card("💰 Income", "₹0", "income")}
            {MetricsDisplay.create_custom_metric_card("💸 Expense", "₹0", "expense")}
            {MetricsDisplay.create_custom_metric_card("📈 Investment", "₹0", "investment")}
        </div>
        """
        st.markdown(grid_html, unsafe_allow_html=True)

    @staticmethod
    def display_recent_transactions(df, count: int = 5):
        """Display recent transactions"""
        if df.empty:
            return
        
        st.markdown("---")
        st.subheader("🕒 Last 5 Transactions")
        
        # Get last 5 rows from the dataframe (most recent entries by index)
        recent_df = df[df["Category"] != "Leave"].tail(count).iloc[::-1]  # Get last 5 and reverse order
        
        from config.config import Config
        
        for _, row in recent_df.iterrows():
            date_str = row["Date"].strftime("%d %b")
            color = Config.CATEGORY_COLORS.get(row["Category"], "#6c757d")
            
            st.markdown(f"""
            <div class="recent-entry">
                <span class="entry-date">{date_str}</span> | 
                <span class="entry-category" style="color: {color};">{row["Category"]}</span> - {row["Subcategory"]}
                <span class="entry-amount" style="color: {color};">₹{row["Amount (₹)"]:,.0f}</span>
                <br><small style="color: black;">{row["Description"]}</small>
            </div>
            """, unsafe_allow_html=True)