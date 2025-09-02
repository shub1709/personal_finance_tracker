import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import calendar
from src.utils.formatters import format_amount
from src.utils.calendar_generator import CalendarGenerator
from config.config import Config

class SummaryDashboard:
    """Component for displaying summary dashboard with analytics"""
    
    def __init__(self, data_service):
        self.data_service = data_service
    
    def render_month_year_selector(self, df: pd.DataFrame) -> tuple[int, list]:
        """Render month and year selector and return selected values"""
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
            # Always ensure selected_months is a list
            selected_months = list(selected_months) if isinstance(selected_months, (list, tuple)) else [selected_months]

        
        with col3:
            analysis_period = f"{', '.join(selected_month_names)} {selected_year}" if selected_month_names else "No months selected"
            st.write("")  # Spacer
            st.write("")  # Spacer
        
        return selected_year, selected_months

    def create_category_chart(self, df: pd.DataFrame, category: str, theme_color: str) -> None:
        """Create bar chart for a specific category (grouped on x-axis)"""
        category_df = df[df["Category"] == category]

        if category_df.empty:
            st.info(f"No {category.lower()} data for selected period")
            return

        # ✅ Apply mapping for x-axis grouping
        category_df["ChartGroup"] = category_df["Subcategory"].map(
            Config.CATEGORY_GROUPING
        ).fillna(category_df["Subcategory"])  # fallback to original if not mapped

        # Group by the new axis label, but keep sum of amounts
        category_by_group = category_df.groupby("ChartGroup")["Amount (₹)"].sum().reset_index()
        category_by_group = category_by_group.sort_values("Amount (₹)", ascending=False)
        category_by_group['Amount_Label'] = category_by_group['Amount (₹)'].apply(format_amount)

        fig = px.bar(
            category_by_group,
            x="ChartGroup",
            y="Amount (₹)",
            title=f"{category} Breakdown",
            text="Amount_Label"
        )

        fig.update_layout(
            height=400,
            xaxis_tickangle=-45,
            showlegend=False,
            font=dict(size=12),
            title_x=0.3,
            title_font_size=16,
            yaxis_title=None
        )
        fig.update_traces(textposition='outside', marker_color=theme_color)

        max_value = category_by_group['Amount (₹)'].max()
        fig.update_yaxes(range=[0, max_value * 1.2])

        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})


    def create_trend_chart(self, df: pd.DataFrame, category: str, theme_color: str) -> None:
        """Create trend chart for a category"""
        trend_data = self.data_service.get_monthly_trend(df, category, months=6)
        trend_data["Amount_Label"] = trend_data["Amount (₹)"].apply(format_amount)

        if trend_data.empty:
            return

        fig_line = px.line(
            trend_data,
            x="YearMonth",
            y="Amount (₹)",
            text="Amount_Label",
            markers=True,
            line_shape="linear",
            title="6 Months Trend"
        )

        fig_line.update_traces(
            line_color=theme_color,
            textposition="top center"
        )

        fig_line.update_layout(
            yaxis_title="Amount (₹)",
            xaxis_title="Month",
            font=dict(size=12),
            height=300,
            title_font_size=16,
            title_x=0.32,
            xaxis_type='category',
            margin=dict(t=80)
        )

        # Generate custom y-axis tick labels
        y_max = trend_data["Amount (₹)"].max()
        y_pad = y_max * 0.2
        fig_line.update_yaxes(range=[0, y_max + y_pad])
        tick_step = y_max / 5
        tick_vals = [round(i) for i in list(range(0, int(y_max * 1.1), int(tick_step)))]

        fig_line.update_yaxes(
            range=[0, y_max + y_max * 0.2],
            tickvals=tick_vals,
            ticktext=[format_amount(v) for v in tick_vals]
        )

        st.plotly_chart(fig_line, use_container_width=True, config={'staticPlot': True})


    def render_category_tab(self, df: pd.DataFrame, category: str, theme_color: str, 
                            calendar_year: int, calendar_months, calendar_theme: str):
        """Render a complete category tab with calendar, charts, and trends"""

        # 🔒 Robust normalization of calendar_months to always be a list
        if calendar_months is None:
            calendar_months = []
        elif isinstance(calendar_months, (int, np.integer)):  # Handle both int and numpy int types
            calendar_months = [calendar_months]
        elif not isinstance(calendar_months, (list, tuple)):
            # Handle other iterables or convert single values
            try:
                calendar_months = list(calendar_months)
            except (TypeError, ValueError):
                calendar_months = [calendar_months]
        
        # Ensure it's a list (in case it was a tuple)
        calendar_months = list(calendar_months)

        # ✅ Safe filtering with list (only if we have months to filter by)
        if calendar_months:
            df_filtered_for_chart = df[
                (df["Date"].dt.year == calendar_year) &
                (df["Date"].dt.month.isin(calendar_months))
            ]
        else:
            # If no months selected, show empty results
            df_filtered_for_chart = df[df["Category"] == category].iloc[0:0]  # Empty DataFrame with same structure

        # Calendar View
        if calendar_months:
            calendar_html = CalendarGenerator.create_calendar_view(
                df, calendar_year, calendar_months[0], category, calendar_theme
            )
            st.markdown(calendar_html, unsafe_allow_html=True)

        # Charts
        self.create_category_chart(df_filtered_for_chart, category, theme_color)
        self.create_trend_chart(df, category, theme_color)