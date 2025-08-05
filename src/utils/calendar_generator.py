import calendar
from datetime import datetime
import pandas as pd
from src.utils.formatters import format_amount

class CalendarGenerator:
    """Utility class for generating calendar views"""
    
    # @staticmethod
    # def create_calendar_view(df: pd.DataFrame, selected_year: int, selected_month: int, 
    #                        category_filter: str = None, calendar_theme: str = "expense") -> str:
    #     """Create a category-filtered calendar view showing daily amounts"""
        
    #     # Filter data for selected month/year and category
    #     month_data = df[(df["Date"].dt.year == selected_year) & 
    #                    (df["Date"].dt.month == selected_month)]
        
    #     if category_filter:
    #         month_data = month_data[month_data["Category"] == category_filter]
        
    #     # Group by date and calculate daily totals
    #     daily_summary = month_data.groupby(month_data["Date"].dt.day)["Amount (₹)"].sum()

    #     calendar.setfirstweekday(calendar.SUNDAY)
        
    #     # Get calendar layout
    #     cal = calendar.monthcalendar(selected_year, selected_month)
    #     month_name = calendar.month_name[selected_month]
        
    #     # Get CSS for calendar
    #     from src.styles.css_styles import get_calendar_css
    #     calendar_css = get_calendar_css(calendar_theme)
        
    #     # Create HTML calendar
    #     calendar_html = f"""
    #     {calendar_css}
        
    #     <div class="calendar-container-{calendar_theme}">
    #         <div class="calendar-header-{calendar_theme}">
    #             {month_name} {selected_year} - Daily {category_filter if category_filter else 'Totals'}
    #         </div>
    #         <div class="calendar-grid-{calendar_theme}">
    #             <!-- Day headers -->
    #             <div class="day-header-{calendar_theme}">Sun</div>
    #             <div class="day-header-{calendar_theme}">Mon</div>
    #             <div class="day-header-{calendar_theme}">Tue</div>
    #             <div class="day-header-{calendar_theme}">Wed</div>
    #             <div class="day-header-{calendar_theme}">Thu</div>
    #             <div class="day-header-{calendar_theme}">Fri</div>
    #             <div class="day-header-{calendar_theme}">Sat</div>
    #     """
        
    #     # Get today's date for highlighting
    #     today = datetime.today()
    #     is_current_month = (today.year == selected_year and today.month == selected_month)
        
    #     # Generate calendar days
    #     for week in cal:
    #         for day in week:
    #             if day == 0:
    #                 calendar_html += f'<div class="calendar-day-{calendar_theme} other-month"></div>'
    #             else:
    #                 # Check if this is today
    #                 is_today = is_current_month and day == today.day
    #                 today_class = " today" if is_today else ""
                    
    #                 calendar_html += f'<div class="calendar-day-{calendar_theme}{today_class}">'
    #                 calendar_html += f'<div class="day-number-{calendar_theme}">{day}</div>'
                    
    #                 # Add transaction amount for this day
    #                 if day in daily_summary.index:
    #                     amount = daily_summary[day]
    #                     if amount > 0:
    #                         formatted_amount = format_amount(amount)
    #                         calendar_html += f'<div class="amount-{calendar_theme}">{formatted_amount}</div>'

    #                 calendar_html += '</div>'
        
    #     calendar_html += """
    #         </div>
    #     </div>
    #     """
        
    #     return calendar_html
    
    # Updated create_calendar_view function
    @staticmethod
    def create_calendar_view(df, selected_year, selected_month, category_filter=None, calendar_theme="expense"):
        """Create a category-filtered calendar view showing daily amounts"""
        import calendar
        
        # Filter data for selected month/year and category
        month_data = df[(df["Date"].dt.year == selected_year) & 
                    (df["Date"].dt.month == selected_month)]
        
        if category_filter:
            month_data = month_data[month_data["Category"] == category_filter]
        
        # Group by date and calculate daily totals
        daily_summary = month_data.groupby(month_data["Date"].dt.day)["Amount (₹)"].sum()

        calendar.setfirstweekday(calendar.SUNDAY)

        # Get calendar layout
        cal = calendar.monthcalendar(selected_year, selected_month)
        month_name = calendar.month_name[selected_month]
        
        # Theme-based styling
        theme_colors = {
            "expense": {"bg": "#fffde6", "color": "#dc3545", "border": "#f5c6cb"},
            "income": {"bg": "#fffde6", "color": "#28a745", "border": "#c3e6cb"},
            "investment": {"bg": "#fffde6", "color": "#c8b002", "border": "#ffeaa7"}
        }
        
        theme = theme_colors.get(calendar_theme, theme_colors["expense"])
        
        # Create HTML calendar
        calendar_html = f"""
        <style>
        .calendar-container-{calendar_theme} {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0 auto;
            max-width: 100%;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .calendar-header-{calendar_theme} {{
            background: linear-gradient(135deg, {theme["color"]} 0%, {theme["color"]}dd 100%);
            color: white;
            text-align: center;
            padding: 0.8rem;
            font-size: 0.95rem;
            font-weight: 600;
        }}
        
        .calendar-grid-{calendar_theme} {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 1px;
            background: #e9ecef;
        }}
        
        .day-header-{calendar_theme} {{
            background: #f8f9fa;
            padding: 0.4rem 0.2rem;
            text-align: center;
            font-weight: 600;
            font-size: 0.75rem;
            color: #6c757d;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .calendar-day-{calendar_theme} {{
            background: white;
            min-height: 70px;
            padding: 0.25rem;
            display: flex;
            flex-direction: column;
            position: relative;
            border: 1px solid #f0f0f0;
        }}
        
        .calendar-day-{calendar_theme}.other-month {{
            background: #f8f9fa;
            color: #adb5bd;
        }}
        
        .calendar-day-{calendar_theme}.today {{
            background: #fff3cd;
            border: 2px solid #ffc107;
        }}
        
        .day-number-{calendar_theme} {{
            font-weight: 600;
            font-size: 0.85rem;
            margin-bottom: 0.2rem;
            color: #495057;
        }}
        
        .amount-{calendar_theme} {{
            font-size: 0.65rem;
            font-weight: 600;
            color: {theme["color"]};
            background: {theme["bg"]};
            padding: 0.1rem 0.25rem;
            border-radius: 6px;
            margin: 0.05rem 0;
            text-align: center;
            border: 1px solid {theme["border"]};
        }}
        
        @media (max-width: 768px) {{
            .calendar-day-{calendar_theme} {{
                min-height: 60px;
                padding: 0.2rem;
            }}
            .day-number-{calendar_theme} {{
                font-size: 0.75rem;
            }}
            .amount-{calendar_theme} {{
                font-size: 0.6rem;
                padding: 0.05rem 0.2rem;
            }}
        }}
        </style>
        
        <div class="calendar-container-{calendar_theme}">
            <div class="calendar-header-{calendar_theme}">
                {month_name} {selected_year} - Daily {category_filter if category_filter else 'Totals'}
            </div>
            <div class="calendar-grid-{calendar_theme}">
                <!-- Day headers -->
                <div class="day-header-{calendar_theme}">Sun</div>
                <div class="day-header-{calendar_theme}">Mon</div>
                <div class="day-header-{calendar_theme}">Tue</div>
                <div class="day-header-{calendar_theme}">Wed</div>
                <div class="day-header-{calendar_theme}">Thu</div>
                <div class="day-header-{calendar_theme}">Fri</div>
                <div class="day-header-{calendar_theme}">Sat</div>
        """
        
        # Get today's date for highlighting
        today = datetime.today()
        is_current_month = (today.year == selected_year and today.month == selected_month)
        
        # Generate calendar days
        for week in cal:
            for day in week:
                if day == 0:
                    calendar_html += f'<div class="calendar-day-{calendar_theme} other-month"></div>'
                else:
                    # Check if this is today
                    is_today = is_current_month and day == today.day
                    today_class = " today" if is_today else ""
                    
                    calendar_html += f'<div class="calendar-day-{calendar_theme}{today_class}">'
                    calendar_html += f'<div class="day-number-{calendar_theme}">{day}</div>'
                    
                    # Add transaction amount for this day
                    if day in daily_summary.index:
                        amount = daily_summary[day]
                        if amount > 0:
                            formatted_amount = format_amount(amount)
                            calendar_html += f'<div class="amount-{calendar_theme}">{formatted_amount}</div>'

                    calendar_html += '</div>'
        
        calendar_html += """
            </div>
        </div>
        """
        
        return calendar_html

    @staticmethod
    def create_leave_calendar_view(df: pd.DataFrame, selected_year: int, selected_month: int) -> str:
        """Create a calendar view showing leave for both maid and cook"""
        
        # Filter data for selected month/year and Leave category
        month_data = df[(df["Date"].dt.year == selected_year) & 
                       (df["Date"].dt.month == selected_month) & 
                       (df["Category"] == "Leave")]
        
        # Group by date and person
        daily_leave = {}
        for _, row in month_data.iterrows():
            day = row["Date"].day
            person = row["Subcategory"]
            if day not in daily_leave:
                daily_leave[day] = []
            daily_leave[day].append(person)

        calendar.setfirstweekday(calendar.SUNDAY)
        
        # Get calendar layout
        cal = calendar.monthcalendar(selected_year, selected_month)
        month_name = calendar.month_name[selected_month]
        
        # Create HTML calendar
        calendar_html = f"""
        <style>
        .leave-calendar-container {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0 auto;
            max-width: 100%;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .leave-calendar-header {{
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            text-align: center;
            padding: 0.8rem;
            font-size: 0.95rem;
            font-weight: 600;
        }}
        
        .leave-calendar-grid {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 1px;
            background: #e9ecef;
        }}
        
        .leave-day-header {{
            background: #f8f9fa;
            padding: 0.4rem 0.2rem;
            text-align: center;
            font-weight: 600;
            font-size: 0.75rem;
            color: #6c757d;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .leave-calendar-day {{
            background: white;
            min-height: 70px;
            padding: 0.25rem;
            display: flex;
            flex-direction: column;
            position: relative;
            border: 1px solid #f0f0f0;
        }}
        
        .leave-calendar-day.other-month {{
            background: #f8f9fa;
            color: #adb5bd;
        }}
        
        .leave-calendar-day.today {{
            background: #fff3cd;
            border: 2px solid #ffc107;
        }}
        
        .leave-day-number {{
            font-weight: 600;
            font-size: 0.85rem;
            margin-bottom: 0.2rem;
            color: #495057;
        }}
        
        .leave-indicator {{
            font-size: 0.6rem;
            font-weight: 600;
            padding: 0.1rem 0.25rem;
            border-radius: 6px;
            margin: 0.05rem 0;
            text-align: center;
            border: 1px solid;
        }}
        
        .leave-maid {{
            background: #fce4ec;
            color: #e91e63;
            border-color: #f8bbd9;
        }}
        
        .leave-cook {{
            background: #e3f2fd;
            color: #2196f3;
            border-color: #bbdefb;
        }}
        
        @media (max-width: 768px) {{
            .leave-calendar-day {{
                min-height: 60px;
                padding: 0.2rem;
            }}
            .leave-day-number {{
                font-size: 0.75rem;
            }}
            .leave-indicator {{
                font-size: 0.55rem;
                padding: 0.05rem 0.2rem;
            }}
        }}
        </style>
        
        <div class="leave-calendar-container">
            <div class="leave-calendar-header">
                {month_name} {selected_year} - Leave Calendar
            </div>
            <div class="leave-calendar-grid">
                <!-- Day headers -->
                <div class="leave-day-header">Sun</div>
                <div class="leave-day-header">Mon</div>
                <div class="leave-day-header">Tue</div>
                <div class="leave-day-header">Wed</div>
                <div class="leave-day-header">Thu</div>
                <div class="leave-day-header">Fri</div>
                <div class="leave-day-header">Sat</div>
        """
        
        # Get today's date for highlighting
        today = datetime.today()
        is_current_month = (today.year == selected_year and today.month == selected_month)
        
        # Generate calendar days
        for week in cal:
            for day in week:
                if day == 0:
                    calendar_html += f'<div class="leave-calendar-day other-month"></div>'
                else:
                    # Check if this is today
                    is_today = is_current_month and day == today.day
                    today_class = " today" if is_today else ""
                    
                    calendar_html += f'<div class="leave-calendar-day{today_class}">'
                    calendar_html += f'<div class="leave-day-number">{day}</div>'
                    
                    # Add leave indicators for this day
                    if day in daily_leave:
                        for person in daily_leave[day]:
                            if person == "Maid":
                                calendar_html += f'<div class="leave-indicator leave-maid">Maid</div>'
                            elif person == "Cook":
                                calendar_html += f'<div class="leave-indicator leave-cook">Cook</div>'

                    calendar_html += '</div>'
        
        calendar_html += """
            </div>
        </div>
        """
        
        return calendar_html