import streamlit as st
from datetime import datetime
from src.models.transaction import Transaction
from config.config import Config

class TransactionForm:
    """Component for transaction input form"""
    
    def __init__(self):
        self.form_key = self._get_form_key()
        
    def _get_form_key(self) -> int:
        """Get or initialize form key for resetting form"""
        if 'form_key' not in st.session_state:
            st.session_state.form_key = 0
        return st.session_state.form_key
    
    def _get_form_category(self) -> str:
        """Get or initialize form category"""
        if 'form_category' not in st.session_state:
            st.session_state.form_category = "Expense"
        return st.session_state.form_category
    
    def render_form(self) -> tuple[bool, Transaction]:
        """Render the transaction form and return submission status and transaction"""
        
        col1, col2 = st.columns(2)
        
        # Date input
        date = col1.date_input(
            "Date", 
            datetime.today(), 
            key=f"date_{self.form_key}"
        )
        
        # Category selection
        current_category = self._get_form_category()
        category_options = list(Config.SUBCATEGORIES.keys())
        
        category = col2.selectbox(
            "Category", 
            category_options,
            index=category_options.index(current_category),
            key=f"category_select_{self.form_key}"
        )
        
        # Update session state when category changes
        if category != current_category:
            st.session_state.form_category = category
        
        # Dynamic subcategory based on selected category
        subcategory_options = Config.SUBCATEGORIES.get(category, [])
        subcategory = st.selectbox(
            "Subcategory", 
            subcategory_options, 
            key=f"subcategory_{self.form_key}"
        )
        
        # Conditional fields based on category
        if category != "Leave":
            description = st.text_input(
                "Description", 
                placeholder="Enter transaction description", 
                key=f"description_{self.form_key}"
            )
            amount = st.number_input(
                "Amount (₹)", 
                min_value=0.0, 
                format="%.0f", 
                step=1.0, 
                key=f"amount_{self.form_key}"
            )
            paid_by = st.selectbox(
                "Paid By", 
                ["Shubham", "Yashika"], 
                key=f"paidby_{self.form_key}"
            )
        else:
            description = ""
            amount = 0.0
            paid_by = ""
        
        # Debug information
        if Config.get_debug_mode():
            st.write("🔍 **Current Form Values:**")
            st.write(f"- Date: {date}")
            st.write(f"- Category: {category}")
            st.write(f"- Subcategory: {subcategory}")
            st.write(f"- Description: '{description}'")
            st.write(f"- Amount: {amount}")
        
        # Submit button
        submitted = st.button("💾 Add Transaction", use_container_width=True)
        
        if submitted:
            # Validation
            errors = self._validate_form(category, amount, description, subcategory)
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
                return False, None
            
            # Create transaction object
            transaction = Transaction(
                date=datetime.combine(date, datetime.min.time()),
                # date=datetime.now(),
                category=category,
                subcategory=subcategory,
                description=description,
                amount=amount,
                paid_by=paid_by
            )
            
            return True, transaction
        
        return False, None
    
    def _validate_form(self, category: str, amount: float, description: str, subcategory: str) -> list:
        """Validate form inputs"""
        errors = []
        
        if category != "Leave":
            if amount <= 0:
                errors.append("Amount must be greater than 0")
            if not description.strip():
                errors.append("Description cannot be empty")
        
        if not subcategory:
            errors.append("Please select a subcategory")
        
        return errors
    
    def reset_form(self):
        """Reset the form by incrementing form key"""
        st.session_state.form_key += 1
        st.session_state.form_category = "Expense"
        self.form_key = st.session_state.form_key