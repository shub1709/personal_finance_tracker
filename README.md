# 💰 Finance Tracker

A comprehensive personal finance tracking application built with Streamlit and Google Sheets integration.

## Features

- 📝 **Transaction Management**: Add and track income, expenses, investments, and leave records
- 📊 **Analytics Dashboard**: Visual insights with charts and trends
- 📅 **Calendar View**: Monthly calendar showing daily transaction summaries
- 🏠 **Leave Tracking**: Special module for tracking domestic help leave
- 📱 **Responsive Design**: Mobile-friendly interface
- ☁️ **Cloud Integration**: Real-time sync with Google Sheets

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/shub1709/finance-tracker.git
cd finance-tracker
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Google Sheets Setup
1. Create a new Google Sheet named "MyFinanceTracker"
2. Create a worksheet named "Tracker" with headers: Date, Category, Subcategory, Description, Amount (₹), Paid by
3. Set up Google Service Account credentials
4. Share your sheet with the service account email

### 4. Configuration
1. Copy `.streamlit/secrets.toml.template` to `.streamlit/secrets.toml`
2. Fill in your Google Service Account credentials
3. Modify `config/config.py` if needed

### 5. Run the Application
```bash
streamlit run app.py
```

## Project Structure

```
finance-tracker/
├── config/           # Configuration files
├── src/             # Source code
│   ├── models/      # Data models
│   ├── services/    # Business logic
│   ├── utils/       # Utility functions
│   ├── components/  # UI components
│   └── styles/      # CSS styling
├── main.py          # Main application entry
└── app.py          # Streamlit app runner
```

## Usage

1. **Add Transactions**: Use the "Transactions" tab to record income, expenses, investments, or leave
2. **View Analytics**: Check the "Summary" tab for insights and trends
3. **Track Leave**: Use the "Leave" tab to monitor domestic help attendance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details
```

This structure provides:
1. **Clear separation of concerns** with different modules
2. **Configuration management** for easy customization
3. **Professional project structure** ready for GitHub
4. **Comprehensive documentation** 
5. **Security best practices** with secrets management