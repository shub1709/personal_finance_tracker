import streamlit as st
import calendar
from datetime import datetime
from src.components.metrics_display import MetricsDisplay
from src.utils.calendar_generator import CalendarGenerator

class LeaveTracker:
    """Component for tracking domestic help leave"""
    
    def __init__(self, data_service):
        self.data_service = data_service
        self.metrics_display = MetricsDisplay()
        self.calendar_generator = CalendarGenerator()
    
    def render_month_year_selector(self, df) -> tuple[int, int]:
        """Render month and year selector for leave tracking"""
        col1, col2 = st.columns(2)
        
        with col1:
            available_years = sorted(df["Date"].dt.year.unique(), reverse=True)
            default_year = datetime.now().year if datetime.now().year in available_years else available_years[0]
            leave_selected_year = st.selectbox(
                "Year", 
                available_years, 
                index=available_years.index(default_year), 
                key="leave_year"
            )
        
        with col2:
            # Set default to current month
            current_month = datetime.now().month
            month_options = [(month, calendar.month_name[month]) for month in range(1, 13)]
            
            try:
                default_index = [month for month, _ in month_options].index(current_month)
            except ValueError:
                default_index = current_month - 1
                
            selected_month_name = st.selectbox(
                "Month", 
                options=[name for _, name in month_options],
                index=default_index,
                key="leave_month"
            )
            
            # Get the month number
            leave_selected_month = next(month for month, name in month_options if name == selected_month_name)
        
        return leave_selected_year, leave_selected_month
    
    def render(self, df):
        """Render the complete leave tracking interface"""
        st.header("🏠 Leave Tracker")
        
        if df.empty:
            self.render_empty_state()
            return
        
        # Month and Year selection
        leave_selected_year, leave_selected_month = self.render_month_year_selector(df)
        
        # Get leave summary
        leave_summary = self.data_service.get_leave_summary(df, leave_selected_year, leave_selected_month)
        
        # Display leave metrics
        self.metrics_display.display_leave_metrics(
            leave_summary['maid_leaves'], 
            leave_summary['cook_leaves']
        )
        
        # Generate and display leave calendar
        leave_calendar_html = self.calendar_generator.create_leave_calendar_view(
            df, leave_selected_year, leave_selected_month
        )
        st.markdown(leave_calendar_html, unsafe_allow_html=True)
    
    def render_empty_state(self):
        """Render empty state when no data is available"""
        st.subheader(f"📅 {datetime.now().strftime('%B %Y')}")
        
        # Empty summary cards
        self.metrics_display.display_leave_metrics(0, 0)
        
        st.info("No leave recorded yet. Add leave entries in the 'Add Transaction' tab using 'Leave' category!")
        
        # Show empty calendar for current month
        current_year = datetime.now().year
        current_month = datetime.now().month
        empty_calendar = self.calendar_generator.create_leave_calendar_view(
            pd.DataFrame(), current_year, current_month
        )
        st.markdown(empty_calendar, unsafe_allow_html=True)