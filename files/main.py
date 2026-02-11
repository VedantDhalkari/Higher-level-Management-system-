"""
Main Application Entry Point
Boutique Management System with Premium Light Theme
"""

import customtkinter as ctk
from tkinter import messagebox
import config
from database import DatabaseManager
from invoice_generator import InvoiceGenerator
from auth import LoginScreen
from dashboard import Dashboard
from billing import BillingModule
from stock import StockManagementModule
from new_stock import NewStockModule
from search import GlobalSearchModule
from reports import ReportsModule
from settings import SettingsModule


class BoutiqueManagementApp(ctk.CTk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(f"{config.APP_NAME} - {config.APP_SUBTITLE}")
        self.geometry(f"{config.WINDOW_DEFAULT_WIDTH}x{config.WINDOW_DEFAULT_HEIGHT}")
        self.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        
        # Set theme to light mode
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Initialize database
        self.db = DatabaseManager(config.DB_NAME)
        self.invoice_generator = InvoiceGenerator(self.db)
        
        # Current user
        self.current_user = None
        
        # Dashboard reference
        self.dashboard = None
        
        # Initialize UI
        self.show_login_screen()
    
    def show_login_screen(self):
        """Display login screen"""
        self.clear_window()
        
        login_screen = LoginScreen(
            self,
            on_login_success=self._on_login_success,
            db_manager=self.db
        )
        login_screen.pack(fill="both", expand=True)
    
    def _on_login_success(self, user: dict):
        """Handle successful login"""
        self.current_user = user
        self.show_dashboard()
    
    def show_dashboard(self):
        """Display main dashboard with sidebar"""
        self.clear_window()
        
        # Create dashboard
        self.dashboard = Dashboard(
            self,
            current_user=self.current_user,
            db_manager=self.db,
            on_navigate=self._handle_navigation
        )
        self.dashboard.pack(fill="both", expand=True)
    
    def _handle_navigation(self, screen: str):
        """Handle navigation from dashboard sidebar"""
        if screen == "logout":
            self._logout()
            return
        
        # Clear current content
        for widget in self.dashboard.content_frame.winfo_children():
            widget.destroy()
            
        if screen == "dashboard":
            # Reload dashboard content
            self.dashboard.load_dashboard_content()
        elif screen == "billing":
            BillingModule(
                self.dashboard.content_frame,
                db_manager=self.db,
                invoice_generator=self.invoice_generator,
                current_user=self.current_user
            ).pack(fill="both", expand=True)
        elif screen == "stock":
            StockManagementModule(
                self.dashboard.content_frame,
                db_manager=self.db
            ).pack(fill="both", expand=True)
        elif screen == "new_stock":
            NewStockModule(
                self.dashboard.content_frame,
                db_manager=self.db
            ).pack(fill="both", expand=True)
        elif screen == "search":
            GlobalSearchModule(
                self.dashboard.content_frame,
                db_manager=self.db
            ).pack(fill="both", expand=True)
        elif screen == "reports":
            ReportsModule(
                self.dashboard.content_frame,
                db_manager=self.db
            ).pack(fill="both", expand=True)
        elif screen == "settings":
            SettingsModule(
                self.dashboard.content_frame,
                db_manager=self.db
            ).pack(fill="both", expand=True)
    
    def _logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.dashboard = None
            self.show_login_screen()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.winfo_children():
            widget.destroy()


# Main Entry Point
if __name__ == "__main__":
    app = BoutiqueManagementApp()
    app.mainloop()
