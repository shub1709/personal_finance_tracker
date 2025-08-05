def format_amount(value: float) -> str:
    """Format amount with K/L/M abbreviations"""
    if value >= 1000000:
        return f"₹{value/1000000:.1f}M"
    elif value >= 100000:
        return f"₹{value/100000:.1f}L"
    elif value >= 1000:
        return f"₹{value/1000:.1f}K"
    else:
        return f"₹{value:.0f}"

def format_currency(value: float, show_decimals: bool = False) -> str:
    """Format currency with proper formatting"""
    if show_decimals:
        return f"₹{value:,.2f}"
    else:
        return f"₹{value:,.0f}"

def format_date_display(date) -> str:
    """Format date for display"""
    if hasattr(date, 'strftime'):
        return date.strftime("%d %b %Y")
    return str(date)

def format_month_year(date) -> str:
    """Format date as Month Year"""
    if hasattr(date, 'strftime'):
        return date.strftime("%B %Y")
    return str(date)