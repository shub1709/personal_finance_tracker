from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    """Transaction data model"""
    date: datetime
    category: str
    subcategory: str
    description: str
    amount: float
    paid_by: str
    
    def to_row(self) -> list:
        """Convert transaction to spreadsheet row format"""
        date_str = self.date.strftime("%Y-%m-%d")
        return [date_str, self.category, self.subcategory, 
                self.description.strip().title(), float(self.amount), self.paid_by]
    
    @classmethod
    def from_row(cls, row: dict) -> 'Transaction':
        """Create transaction from spreadsheet row"""
        return cls(
            date=datetime.strptime(row['Date'], "%Y-%m-%d"),
            category=row['Category'],
            subcategory=row['Subcategory'],
            description=row['Description'],
            amount=float(row['Amount (₹)']),
            paid_by=row.get('Paid by', '')
        )
    
    def is_leave(self) -> bool:
        """Check if transaction is a leave record"""
        return self.category == "Leave"
    
    def is_expense(self) -> bool:
        """Check if transaction is an expense"""
        return self.category == "Expense"
    
    def is_income(self) -> bool:
        """Check if transaction is income"""
        return self.category == "Income"
    
    def is_investment(self) -> bool:
        """Check if transaction is an investment"""
        return self.category == "Investment"