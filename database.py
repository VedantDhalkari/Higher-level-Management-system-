"""
Database setup and connection management
"""
import sqlite3
import logging
from datetime import datetime
from contextlib import contextmanager
import json
from config import AppConfig

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name=AppConfig.DB_NAME):
        self.db_name = db_name
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'staff',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Stock items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sku TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    material TEXT,
                    color TEXT,
                    size TEXT,
                    quantity INTEGER DEFAULT 0,
                    purchase_price REAL NOT NULL,
                    selling_price REAL NOT NULL,
                    supplier_name TEXT,
                    supplier_contact TEXT,
                    arrival_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    min_stock_level INTEGER DEFAULT 5,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE,
                    email TEXT,
                    address TEXT,
                    total_purchases REAL DEFAULT 0,
                    last_purchase_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sales transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    customer_id INTEGER,
                    customer_name TEXT,
                    customer_phone TEXT,
                    items TEXT NOT NULL, -- JSON string of items
                    subtotal REAL NOT NULL,
                    discount REAL DEFAULT 0,
                    gst_amount REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    payment_method TEXT DEFAULT 'Cash',
                    payment_status TEXT DEFAULT 'Completed',
                    sold_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            # Suppliers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    products_supplied TEXT,
                    rating INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default admin user if not exists
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', ('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin'))  # password: admin
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_sku ON stock(sku)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_category ON stock(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_invoice ON sales(invoice_number)')
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a query with optional fetching"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            return cursor.lastrowid
    
    def get_low_stock_items(self, threshold=5):
        """Get items with stock below threshold"""
        query = '''
            SELECT * FROM stock 
            WHERE quantity <= min_stock_level 
            AND is_active = 1
            ORDER BY quantity ASC
        '''
        return self.execute_query(query, fetch_all=True)
    
    def get_today_sales(self):
        """Get total sales for today"""
        query = '''
            SELECT SUM(total_amount) as total_sales, COUNT(*) as transaction_count
            FROM sales 
            WHERE DATE(created_at) = DATE('now')
        '''
        return self.execute_query(query, fetch_one=True)
    
    def get_recent_transactions(self, limit=10):
        """Get recent sales transactions"""
        query = '''
            SELECT invoice_number, customer_name, total_amount, created_at
            FROM sales 
            ORDER BY created_at DESC 
            LIMIT ?
        '''
        return self.execute_query(query, (limit,), fetch_all=True)

# Global database instance
db = Database()