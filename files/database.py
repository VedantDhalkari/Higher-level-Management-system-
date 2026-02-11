"""
Database Manager Module
Handles all SQLite database operations for the boutique management system
"""

import sqlite3
import hashlib
from typing import Optional, List, Tuple, Any
import config


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_name: str):
        """
        Initialize database manager
        
        Args:
            db_name: Name of the SQLite database file
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.initialize_database()
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def initialize_database(self):
        """Create all necessary tables and default data"""
        self.connect()
        
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inventory/Stock table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku_code TEXT UNIQUE NOT NULL,
                saree_type TEXT NOT NULL,
                material TEXT NOT NULL,
                color TEXT NOT NULL,
                design TEXT,
                quantity INTEGER NOT NULL,
                purchase_price REAL NOT NULL,
                selling_price REAL NOT NULL,
                supplier_name TEXT,
                category TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sales/Bills table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_number TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                customer_phone TEXT,
                total_amount REAL NOT NULL,
                discount_percent REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                gst_amount REAL NOT NULL,
                final_amount REAL NOT NULL,
                payment_method TEXT,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        ''')
        
        # Sale Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                sku_code TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
                FOREIGN KEY (item_id) REFERENCES inventory(item_id)
            )
        ''')
        
        # Settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            )
        ''')
        
        # Create default admin user
        try:
            password_hash = hashlib.sha256(config.DEFAULT_PASSWORD.encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (config.DEFAULT_USERNAME, password_hash, "admin")
            )
        except sqlite3.IntegrityError:
            pass  # User already exists
        
        # Initialize default settings
        self._initialize_settings()
        
        self.conn.commit()
        self.disconnect()
    
    def _initialize_settings(self):
        """Initialize default settings"""
        default_settings = {
            config.SETTING_SHOP_NAME: config.DEFAULT_SHOP_NAME,
            config.SETTING_SHOP_ADDRESS: config.DEFAULT_SHOP_ADDRESS,
            config.SETTING_SHOP_PHONE: config.DEFAULT_SHOP_PHONE,
            config.SETTING_SHOP_EMAIL: config.DEFAULT_SHOP_EMAIL,
            config.SETTING_GST_NUMBER: config.DEFAULT_GST_NUMBER,
            config.SETTING_BILL_PREFIX: config.BILL_PREFIX,
            config.SETTING_THEME_MODE: "light"
        }
        
        for key, value in default_settings.items():
            try:
                self.cursor.execute(
                    "INSERT INTO settings (setting_key, setting_value) VALUES (?, ?)",
                    (key, value)
                )
            except sqlite3.IntegrityError:
                pass  # Setting already exists
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Tuple]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            List of result tuples
        """
        self.connect()
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        self.conn.commit()
        self.disconnect()
        return results
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT query and return the last row ID
        
        Args:
            query: SQL INSERT query string
            params: Query parameters tuple
            
        Returns:
            Last inserted row ID
        """
        self.connect()
        self.cursor.execute(query, params)
        last_id = self.cursor.lastrowid
        self.conn.commit()
        self.disconnect()
        return last_id
    
    def get_setting(self, key: str) -> Optional[str]:
        """
        Get a setting value by key
        
        Args:
            key: Setting key
            
        Returns:
            Setting value or None if not found
        """
        result = self.execute_query(
            "SELECT setting_value FROM settings WHERE setting_key = ?",
            (key,)
        )
        return result[0][0] if result else None
    
    def update_setting(self, key: str, value: str):
        """
        Update a setting value
        
        Args:
            key: Setting key
            value: New value
        """
        self.execute_query(
            "UPDATE settings SET setting_value = ? WHERE setting_key = ?",
            (value, key)
        )
    
    def verify_user(self, username: str, password: str) -> Optional[dict]:
        """
        Verify user credentials
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User dict with id, username, role or None if invalid
        """
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        result = self.execute_query(
            "SELECT user_id, username, role FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        if result:
            return {
                "id": result[0][0],
                "username": result[0][1],
                "role": result[0][2]
            }
        return None
    
    def get_dashboard_metrics(self) -> dict:
        """
        Get dashboard metrics
        
        Returns:
            Dictionary with today_sales, month_sales, low_stock_count, total_items
        """
        from datetime import datetime
        
        today = datetime.now().strftime("%Y-%m-%d")
        month_start = datetime.now().strftime("%Y-%m-01")
        
        # Today's sales
        today_result = self.execute_query(
            """SELECT COUNT(*), COALESCE(SUM(final_amount), 0) 
               FROM sales WHERE DATE(sale_date) = ?""",
            (today,)
        )
        
        # This month's sales
        month_result = self.execute_query(
            """SELECT COUNT(*), COALESCE(SUM(final_amount), 0) 
               FROM sales WHERE DATE(sale_date) >= ?""",
            (month_start,)
        )
        
        # Low stock count
        low_stock = self.execute_query(
            "SELECT COUNT(*) FROM inventory WHERE quantity <= ?",
            (config.LOW_STOCK_THRESHOLD,)
        )
        
        # Total items
        total_items = self.execute_query("SELECT COUNT(*) FROM inventory")
        
        return {
            "today_sales_count": today_result[0][0],
            "today_sales_amount": today_result[0][1],
            "month_sales_count": month_result[0][0],
            "month_sales_amount": month_result[0][1],
            "low_stock_count": low_stock[0][0],
            "total_items": total_items[0][0]
        }
    
    def get_recent_transactions(self, limit: int = 10) -> List[Tuple]:
        """
        Get recent transactions
        
        Args:
            limit: Number of transactions to retrieve
            
        Returns:
            List of transaction tuples
        """
        return self.execute_query(
            """SELECT bill_number, customer_name, final_amount, sale_date
               FROM sales ORDER BY sale_date DESC LIMIT ?""",
            (limit,)
        )
    
    def get_top_categories(self, limit: int = 5) -> List[Tuple]:
        """
        Get top selling categories
        
        Args:
            limit: Number of categories to retrieve
            
        Returns:
            List of (category, total_sales) tuples
        """
        return self.execute_query(
            """SELECT i.category, SUM(si.total_price) as total_sales
               FROM sale_items si
               JOIN inventory i ON si.item_id = i.item_id
               WHERE i.category IS NOT NULL
               GROUP BY i.category
               ORDER BY total_sales DESC
               LIMIT ?""",
            (limit,)
        )
    
    def get_sales_by_period(self, period: str = "today") -> List[Tuple]:
        """
        Get sales data for a specific period
        
        Args:
            period: "today", "week", or "month"
            
        Returns:
            List of (date, amount) tuples
        """
        from datetime import datetime, timedelta
        
        if period == "today":
            today = datetime.now().strftime("%Y-%m-%d")
            return self.execute_query(
                """SELECT strftime('%H:00', sale_date) as hour, SUM(final_amount)
                   FROM sales WHERE DATE(sale_date) = ?
                   GROUP BY hour ORDER BY hour""",
                (today,)
            )
        elif period == "week":
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            return self.execute_query(
                """SELECT DATE(sale_date) as day, SUM(final_amount)
                   FROM sales WHERE DATE(sale_date) >= ?
                   GROUP BY day ORDER BY day""",
                (week_ago,)
            )
        else:  # month
            month_start = datetime.now().strftime("%Y-%m-01")
            return self.execute_query(
                """SELECT DATE(sale_date) as day, SUM(final_amount)
                   FROM sales WHERE DATE(sale_date) >= ?
                   GROUP BY day ORDER BY day""",
                (month_start,)
            )
