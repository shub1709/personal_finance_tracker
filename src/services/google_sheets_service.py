import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional, List, Dict, Any
import time
from config.config import Config

class GoogleSheetsService:
    """Service for managing Google Sheets operations"""
    
    def __init__(self):
        self.client = None
        self.worksheet = None
        self._connect()
    
    @st.cache_resource(ttl=Config.CACHE_TTL_HOURS * 3600)
    def _get_client(_self) -> Optional[gspread.Client]:
        """Get authenticated Google Sheets client"""
        try:
            creds_dict = st.secrets["gcp_service_account"]
            
            creds = Credentials.from_service_account_info(
                creds_dict, 
                scopes=Config.GOOGLE_SHEETS_SCOPES
            )
            
            client = gspread.authorize(creds)
            
            if Config.get_debug_mode():
                st.write("🔍 Debug: Google Sheets client authorized successfully")
            
            return client
            
        except KeyError as e:
            st.error(f"❌ Missing secret key: {str(e)}. Please check your secrets configuration.")
            return None
        except Exception as e:
            st.error(f"❌ Error connecting to Google Sheets: {str(e)}")
            return None
    
    def _connect(self) -> None:
        """Establish connection to Google Sheets"""
        self.client = self._get_client()
    
    def get_worksheet(self) -> Optional[gspread.Worksheet]:
        """Get worksheet instance"""
        try:
            if self.client is None:
                return None
            
            sheet = self.client.open(Config.SPREADSHEET_NAME)
            ws = sheet.worksheet(Config.WORKSHEET_NAME)
            
            if Config.get_debug_mode():
                st.write("🔍 Debug: Successfully connected to spreadsheet and worksheet")
            
            return ws
            
        except gspread.SpreadsheetNotFound:
            st.error(f"❌ Spreadsheet '{Config.SPREADSHEET_NAME}' not found. Please check the name and sharing permissions.")
            return None
        except gspread.WorksheetNotFound:
            st.error(f"❌ Worksheet '{Config.WORKSHEET_NAME}' not found. Please check the worksheet name.")
            return None
        except Exception as e:
            st.error(f"❌ Error accessing worksheet: {str(e)}")
            return None
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        """Get all records from the worksheet"""
        try:
            ws = self.get_worksheet()
            if ws is None:
                return []
            
            data = ws.get_all_records()
            
            if Config.get_debug_mode():
                st.write(f"🔍 Debug: Loaded {len(data)} records from sheet")
            
            return data
            
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            return []
    
    def add_record(self, row_data: List[Any], max_retries: int = 3) -> tuple[bool, str]:
        """Add a new record to the worksheet"""
        try:
            ws = self.get_worksheet()
            if ws is None:
                return False, "Could not connect to worksheet"
            
            if Config.get_debug_mode():
                st.write(f"🔍 Debug: Row data prepared: {row_data}")
            
            # Retry logic for robust insertion
            for attempt in range(max_retries):
                try:
                    if Config.get_debug_mode():
                        st.write(f"🔍 Debug: Attempt {attempt + 1} to add row...")
                    
                    result = ws.append_row(row_data, value_input_option='USER_ENTERED')
                    
                    if Config.get_debug_mode():
                        st.write(f"🔍 Debug: Sheet response: {result}")
                    
                    return True, "Transaction added successfully!"
                    
                except Exception as retry_error:
                    if Config.get_debug_mode():
                        st.write(f"🔍 Debug: Attempt {attempt + 1} failed: {str(retry_error)}")
                    
                    if attempt == max_retries - 1:
                        raise retry_error
                    
                    time.sleep(1)
            
            return False, "Failed after all retry attempts"
            
        except gspread.exceptions.APIError as e:
            error_msg = f"Google Sheets API Error: {str(e)}"
            return False, error_msg
        except ValueError as e:
            error_msg = f"Value Error (check amount format): {str(e)}"
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return False, error_msg
    
    def test_connection(self) -> tuple[bool, str]:
        """Test the Google Sheets connection"""
        try:
            ws = self.get_worksheet()
            if not ws:
                return False, "Connection failed"
            
            headers = ws.row_values(1)
            all_values = ws.get_all_values()
            
            return True, f"Connection successful! Headers: {headers}, Rows: {len(all_values)}"
            
        except Exception as e:
            return False, f"Connection test failed: {e}"