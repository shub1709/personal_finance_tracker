import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import time
from io import BytesIO
import gspread

# Import custom modules
from config.config import Config
from src.services.data_service import DataService
from src.components.metrics_display import MetricsDisplay
from src.components.transaction_form import TransactionForm
from src.components.summary_dashboard import SummaryDashboard
from src.components.leave_tracker import LeaveTracker
from src.utils.calendar_generator import CalendarGenerator
from src.styles.css_styles import get_main_css

class FinanceTrackerApp:
    """Main Finance Tracker Application"""
    
    def __init__(self):
        self.setup_page_config()
        self.data_service = DataService()
        self.metrics_display = MetricsDisplay()
        self.transaction_form = TransactionForm()
        self.summary_dashboard = SummaryDashboard(self.data_service)
        self.leave_tracker = LeaveTracker(self.data_service)
        
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=Config.APP_TITLE, 
            layout=Config.PAGE_LAYOUT, 
            initial_sidebar_state="collapsed"
        )
        
        # Apply custom CSS
        st.markdown(get_main_css(), unsafe_allow_html=True)
        
        # Set title
        st.title("💸 Daily Tracker")
    
    def render_transaction_tab(self, df: pd.DataFrame):
        """Render the transaction input tab"""
        st.header("📝 Add New Transaction")
        
        # Render transaction form
        submitted, transaction = self.transaction_form.render_form()
        
        if submitted and transaction:
            # Handle duplicate leave logic
            if transaction.is_leave():
                duplicate_exists = self.data_service.check_duplicate_leave(
                    df, transaction.date, transaction.subcategory
                )
                
                if duplicate_exists:
                    st.error(f"❌ Leave already recorded for {transaction.subcategory} on {transaction.date.strftime('%d %b %Y')}")
                    time.sleep(3)
                    st.rerun()
                    return
            
            # Add transaction
            success, message = self.data_service.add_transaction(transaction)
            
            if success:
                st.success("✅ Transaction successfully recorded!")
                st.balloons()
                time.sleep(2)
                self.transaction_form.reset_form()
                st.rerun()
            else:
                st.error("❌ " + message)
                st.info("💡 **Troubleshooting Tips:**\n"
                       "- Check if the Google Sheet is accessible\n"
                       "- Verify the service account has edit permissions\n"
                       "- Try refreshing the page\n"
                       "- Check your internet connection")
        
        # Show recent transactions
        self.metrics_display.display_recent_transactions(df)
        
        # Download section
        self.render_download_section(df)
    
    def render_download_section(self, df: pd.DataFrame):
        """Render the download section"""
        st.markdown("---")
        
        if not df.empty:
            # Convert datetime to string for Excel compatibility
            df_download = df.copy()
            df_download["Date"] = df_download["Date"].dt.strftime("%Y-%m-%d")
            
            # Convert to Excel bytes
            excel_buffer = BytesIO()
            df_download.to_excel(excel_buffer, index=False, sheet_name="Finance_Data")
            excel_buffer.seek(0)
            
            # Download button
            st.download_button(
                label="📊 Download as Excel",
                data=excel_buffer.getvalue(),
                file_name=f"finance_tracker_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxlsx",
                use_container_width=True
            )
        else:
            st.info("No data available to download")
    
    def render_summary_tab(self, df: pd.DataFrame):
        """Render the summary and analytics tab"""
        st.header("📊 Monthly Summary")
        
        if df.empty:
            # Empty state
            st.subheader(f"📅 {datetime.now().strftime('%B %Y')}")
            self.metrics_display.display_empty_metrics()
            st.info("No transactions recorded yet. Add your first transaction in the 'Add Transaction' tab!")
            return
        
        # Month and Year selection
        selected_year, selected_months = self.summary_dashboard.render_month_year_selector(df)
        
        if not selected_months:
            st.warning("Please select at least one month to view summary")
            return
        
        # Filter data for selected period
        selected_period_df = self.data_service.get_monthly_data(df, selected_year, selected_months)
        
        # Calculate totals
        totals = self.data_service.get_category_totals(selected_period_df)
        total_investment_alltime = self.data_service.get_category_totals(df)['investment']
        
        # Display period
        selected_month_names = [datetime(2000, month, 1).strftime('%B') for month in selected_months]
        analysis_period = f"{', '.join(selected_month_names)} {selected_year}"
        st.subheader(f"📅 {analysis_period}")
        
        # Display metrics
        self.metrics_display.display_summary_metrics(totals, total_investment_alltime)
        
        # Charts Section
        if not selected_period_df.empty:
            # For calendar display, use the first selected month
            calendar_year = selected_year
            calendar_month = selected_months[0] if selected_months else None
            
            if len(selected_months) > 1:
                st.info(f"📅 Calendar shows daily breakdown for {datetime(2000, selected_months[0], 1).strftime('%B')} {calendar_year} (first selected month)")
            
            # Chart tabs
            chart_tab1, chart_tab2, chart_tab3 = st.tabs(["💸 Expenses", "📈 Investments", "💰 Income"])
            
            with chart_tab1:
                self.summary_dashboard.render_category_tab(
                    df, "Expense", Config.CATEGORY_COLORS["Expense"], 
                    calendar_year, selected_months, "expense"
                )
            
            with chart_tab2:
                self.summary_dashboard.render_category_tab(
                    df, "Investment", Config.CATEGORY_COLORS["Investment"], 
                    calendar_year, selected_months, "investment"
                )
            
            with chart_tab3:
                self.summary_dashboard.render_category_tab(
                    df, "Income", Config.CATEGORY_COLORS["Income"], 
                    calendar_year, selected_months, "income"
                )
    
    def render_leave_tab(self, df: pd.DataFrame):
        """Render the leave tracking tab"""
        self.leave_tracker.render(df)
    
    def render_debug_section(self):
        """Render debug panel if debug mode is enabled"""
        if not Config.get_debug_mode():
            return
        
        st.markdown("---")
        st.subheader("🔧 Debug Panel")
        
        if st.button("🧪 Test Google Sheets Connection"):
            success, message = self.data_service.sheets_service.test_connection()
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
        
        if st.button("🔄 Clear All Caches"):
            self.data_service.clear_cache()
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("✅ All caches cleared!")
            st.rerun()
    
    def run(self):
        """Main application runner"""
        # Load data
        df = self.data_service.load_data()
        
        # Check connection if no data
        if df.empty:
            test_ws = self.data_service.sheets_service.get_worksheet()
            if test_ws is None:
                st.error("❌ Could not connect to Google Sheets. Please check your credentials and sheet permissions.")
                st.info("💡 Common issues:\n- Check if 'MyFinanceTracker' spreadsheet exists\n- Verify the service account has edit permissions\n- Ensure 'Tracker' worksheet exists\n- Check your secrets configuration")
                st.stop()
        
        # Create main tabs
        tab1, tab2, tab3 = st.tabs(["📝 Transactions", "📊 Summary", "🏠 Leave"])
        
        with tab1:
            self.render_transaction_tab(df)
        
        with tab2:
            self.render_summary_tab(df)
        
        with tab3:
            self.render_leave_tab(df)
        
        # Debug section
        self.render_debug_section()

def main():
    """Application entry point"""
    app = FinanceTrackerApp()
    app.run()

if __name__ == "__main__":
    main()