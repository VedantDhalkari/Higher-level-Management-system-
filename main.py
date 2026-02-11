"""
Main application file - Boutique Management System
"""
import customtkinter as ctk
import sys
import logging
from config import Colors, AppConfig
from database import Database
from auth import LoginWindow, AuthManager
from dashboard import Dashboard
from billing import BillingSystem
from stock import StockManagement
from new_stock import NewStockEntry
from search import GlobalSearch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('boutique_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BoutiqueManagementSystem(ctk.CTk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Setup directories
        AppConfig.setup_directories()
        
        # Initialize database
        self.db = Database()
        self.auth = AuthManager(self.db)
        
        # Configure window
        self.title(AppConfig.APP_NAME)
        self.geometry("1600x900")
        self.minsize(1400, 800)
        
        # Set theme to light for premium design
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize frames dictionary
        self.frames = {}
        
        # Show login screen initially
        self.show_login()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_login(self):
        """Show login screen"""
        self.clear_frames()
        
        login_frame = LoginWindow(self, self.on_login_success)
        login_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["login"] = login_frame
    
    def on_login_success(self, user_info):
        """Handle successful login"""
        logger.info(f"User {user_info['username']} logged in successfully")
        self.user_info = user_info
        self.show_dashboard()
    
    def show_dashboard(self):
        """Show dashboard"""
        self.clear_frames()
        
        dashboard = Dashboard(self, self.switch_frame, self.user_info)
        dashboard.grid(row=0, column=0, sticky="nsew")
        self.frames["dashboard"] = dashboard
    
    def switch_frame(self, frame_name):
        """Switch between frames"""
        self.clear_frames()
        
        if frame_name == "dashboard":
            self.show_dashboard()
        elif frame_name == "billing":
            billing_frame = BillingSystem(self)
            billing_frame.grid(row=0, column=0, sticky="nsew")
            self.frames["billing"] = billing_frame
        elif frame_name == "stock":
            stock_frame = StockManagement(self)
            stock_frame.grid(row=0, column=0, sticky="nsew")
            self.frames["stock"] = stock_frame
        elif frame_name == "new_stock":
            new_stock_frame = NewStockEntry(self)
            new_stock_frame.grid(row=0, column=0, sticky="nsew")
            self.frames["new_stock"] = new_stock_frame
        elif frame_name == "search":
            search_frame = GlobalSearch(self)
            search_frame.grid(row=0, column=0, sticky="nsew")
            self.frames["search"] = search_frame
    
    def clear_frames(self):
        """Clear all frames"""
        for frame in self.frames.values():
            frame.destroy()
        self.frames.clear()
    
    def logout(self):
        """Handle logout"""
        self.auth.current_user = None
        self.show_login()
    
    def on_closing(self):
        """Handle window closing"""
        # Database connections are handled by context manager, no cleanup needed
        self.destroy()
        sys.exit(0)

def main():
    """Main entry point"""
    try:
        app = BoutiqueManagementSystem()
        app.mainloop()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")

if __name__ == "__main__":
    main()