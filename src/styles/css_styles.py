def get_main_css() -> str:
    """Get main CSS styles for the application"""
    return """
    <style>
    /* Hide Streamlit UI elements */
    #MainMenu, footer, header, [data-testid="stToolbarActions"] {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* REMOVE ALL TOP SPACING */
    section.main > div { 
        padding-top: 0rem !important;
    }
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 1rem !important;
    }

    /* Tighten the h1 title itself */
    h1 {
        text-align: center !important;
        margin-top: 0rem !important;
        margin-bottom: 0.8rem !important;
        font-size: 1.2rem !important;
    }

    /* Custom grid layout for metrics */
    .custom-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr !important;
        gap: 0.5rem !important;
        margin: 1rem 0 !important;
    }

    .custom-metric {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 2px solid #e0e0e0;
        padding: 0.8rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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

    .metric-income { 
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #a7f3d0 100%) !important;
        border: 0px solid #10b981 !important;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.15) !important;
    }
    .metric-expense { 
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 50%, #fecaca 100%) !important;
        border: 0px solid #ef4444 !important;
        box-shadow: 0 2px 10px rgba(239, 68, 68, 0.15) !important;
    }
    .metric-investment { 
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 50%, #fde68a 100%) !important;
        border: 0px solid #f59e0b !important;
        box-shadow: 0 2px 10px rgba(245, 158, 11, 0.15) !important;
    }
    .metric-balance { 
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 50%, #93c5fd 100%) !important;
        border: 0px solid #3b82f6 !important;
        box-shadow: 0 2px 10px rgba(59, 130, 246, 0.15) !important;
    }

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

    /* Custom grid layout for leave */
    .leave-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 0.5rem !important;
        margin: 1rem 0 !important;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container { padding: 0.5rem 0.25rem !important; }
        .custom-grid { gap: 0.25rem !important; }
        .custom-metric { padding: 0.6rem; min-height: 70px; }
        .custom-metric .metric-value { font-size: 1rem; }
    }

    /* Evenly distribute tabs horizontally */
    .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        justify-content: space-evenly !important;
    }

    .stTabs [data-baseweb="tab"] {
        flex-grow: 1 !important;
        text-align: center !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 0.25rem !important;
    }
    </style>
    """

def get_calendar_css(theme: str) -> str:
    """Get CSS for calendar display based on theme"""
    from config.config import Config
    
    theme_config = Config.CALENDAR_THEMES.get(theme, Config.CALENDAR_THEMES["expense"])
    
    return f"""
    <style>
    .calendar-container-{theme} {{
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 0 auto;
        max-width: 100%;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        overflow: hidden;
    }}
    
    .calendar-header-{theme} {{
        background: linear-gradient(135deg, {theme_config["color"]} 0%, {theme_config["color"]}dd 100%);
        color: white;
        text-align: center;
        padding: 0.8rem;
        font-size: 0.95rem;
        font-weight: 600;
    }}
    
    .calendar-grid-{theme} {{
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 1px;
        background: #e9ecef;
    }}
    
    .day-header-{theme} {{
        background: #f8f9fa;
        padding: 0.4rem 0.2rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.75rem;
        color: #6c757d;
        border-bottom: 1px solid #dee2e6;
    }}
    
    .calendar-day-{theme} {{
        background: white;
        min-height: 70px;
        padding: 0.25rem;
        display: flex;
        flex-direction: column;
        position: relative;
        border: 1px solid #f0f0f0;
    }}
    
    .calendar-day-{theme}.other-month {{
        background: #f8f9fa;
        color: #adb5bd;
    }}
    
    .calendar-day-{theme}.today {{
        background: #fff3cd;
        border: 2px solid #ffc107;
    }}
    
    .day-number-{theme} {{
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.2rem;
        color: #495057;
    }}
    
    .amount-{theme} {{
        font-size: 0.65rem;
        font-weight: 600;
        color: {theme_config["color"]};
        background: {theme_config["bg"]};
        padding: 0.1rem 0.25rem;
        border-radius: 6px;
        margin: 0.05rem 0;
        text-align: center;
        border: 1px solid {theme_config["border"]};
    }}
    
    @media (max-width: 768px) {{
        .calendar-day-{theme} {{
            min-height: 60px;
            padding: 0.2rem;
        }}
        .day-number-{theme} {{
            font-size: 0.75rem;
        }}
        .amount-{theme} {{
            font-size: 0.6rem;
            padding: 0.05rem 0.2rem;
        }}
    }}
    </style>
    """