"""
Global search module
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
import json
from config import Colors
from utils import Formatters

class GlobalSearch(ctk.CTkFrame):
    """Global search interface"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = parent.db
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup search UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔍 Global Search",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Search across bills, customers, and stock items",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.pack(anchor="w")
        
        # Search controls
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Search type
        type_label = ctk.CTkLabel(controls_frame, text="Search In:")
        type_label.grid(row=0, column=0, padx=(0, 10))
        
        self.search_type_var = ctk.StringVar(value="All")
        type_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.search_type_var,
            values=["All", "Bills", "Customers", "Stock"],
            width=120
        )
        type_dropdown.grid(row=0, column=1, padx=(0, 10), sticky="w")
        
        # Search entry
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="Enter search term...",
            textvariable=self.search_var
        )
        search_entry.grid(row=0, column=2, sticky="ew", padx=(0, 10))
        controls_frame.grid_columnconfigure(2, weight=1)
        
        # Search button
        search_btn = ctk.CTkButton(
            controls_frame,
            text="Search",
            command=self.perform_search,
            width=100,
            fg_color=Colors.PRIMARY
        )
        search_btn.grid(row=0, column=3, padx=(0, 10))
        
        # Clear button
        clear_btn = ctk.CTkButton(
            controls_frame,
            text="Clear",
            command=self.clear_search,
            width=100
        )
        clear_btn.grid(row=0, column=4)
        
        # Results frame
        results_frame = ctk.CTkFrame(self)
        results_frame.grid(row=2, column=0, sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        self.tree_scroll_y = ctk.CTkScrollbar(results_frame)
        self.tree_scroll_y.grid(row=0, column=1, sticky="ns")
        
        self.tree_scroll_x = ctk.CTkScrollbar(results_frame, orientation="horizontal")
        self.tree_scroll_x.grid(row=1, column=0, sticky="ew")
        
        self.results_tree = ttk.Treeview(
            results_frame,
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set,
            selectmode="browse",
            height=20
        )
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        
        self.tree_scroll_y.configure(command=self.results_tree.yview)
        self.tree_scroll_x.configure(command=self.results_tree.xview)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Enter search term and press Search",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=3, column=0, sticky="w", pady=(10, 0))
    
    def perform_search(self):
        """Perform search based on criteria"""
        search_term = self.search_var.get().strip()
        search_type = self.search_type_var.get()
        
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term!")
            return
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Configure treeview columns based on search type
        if search_type == "All" or search_type == "Bills":
            self.search_bills(search_term)
        
        if search_type == "All" or search_type == "Customers":
            self.search_customers(search_term)
        
        if search_type == "All" or search_type == "Stock":
            self.search_stock(search_term)
        
        # Update status
        result_count = len(self.results_tree.get_children())
        self.status_label.configure(
            text=f"Found {result_count} result(s) for '{search_term}' in {search_type}"
        )
    
    def search_bills(self, search_term):
        """Search in sales/bills"""
        query = '''
            SELECT invoice_number, customer_name, customer_phone, 
                   total_amount, created_at, items
            FROM sales 
            WHERE invoice_number LIKE ? 
               OR customer_name LIKE ? 
               OR customer_phone LIKE ?
            ORDER BY created_at DESC
        '''
        
        pattern = f'%{search_term}%'
        results = self.db.execute_query(
            query, (pattern, pattern, pattern), fetch_all=True
        )
        
        # Add header for bills section
        if results:
            self.results_tree.insert("", "end", values=("", "", "", "", "", ""), tags=('header',))
            self.results_tree.insert("", "end", 
                values=("📄 BILLS", "", "", "", "", ""), tags=('section',))
            
            for result in results:
                result = dict(result)
                # Parse items to get count
                items = json.loads(result['items']) if result['items'] else []
                item_count = len(items)
                
                self.results_tree.insert("", "end", values=(
                    result['invoice_number'],
                    result['customer_name'],
                    result['customer_phone'] or "",
                    Formatters.format_currency(result['total_amount']),
                    Formatters.format_date(result['created_at']),
                    f"{item_count} items"
                ), tags=('bill',))
    
    def search_customers(self, search_term):
        """Search in customers"""
        query = '''
            SELECT name, phone, email, total_purchases, last_purchase_date
            FROM customers 
            WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
            ORDER BY name
        '''
        
        pattern = f'%{search_term}%'
        results = self.db.execute_query(
            query, (pattern, pattern, pattern), fetch_all=True
        )
        
        # Add header for customers section
        if results:
            self.results_tree.insert("", "end", values=("", "", "", "", "", ""), tags=('header',))
            self.results_tree.insert("", "end", 
                values=("👥 CUSTOMERS", "", "", "", "", ""), tags=('section',))
            
            for result in results:
                result = dict(result)
                self.results_tree.insert("", "end", values=(
                    result['name'],
                    result['phone'] or "",
                    result['email'] or "",
                    Formatters.format_currency(result['total_purchases'] or 0),
                    Formatters.format_date(result['last_purchase_date']),
                    ""
                ), tags=('customer',))
    
    def search_stock(self, search_term):
        """Search in stock"""
        query = '''
            SELECT sku, name, category, material, color, quantity, selling_price
            FROM stock 
            WHERE is_active = 1 
              AND (sku LIKE ? OR name LIKE ? OR category LIKE ? OR material LIKE ?)
            ORDER BY name
        '''
        
        pattern = f'%{search_term}%'
        results = self.db.execute_query(
            query, (pattern, pattern, pattern, pattern), fetch_all=True
        )
        
        # Configure columns for stock
        self.results_tree['columns'] = ("SKU", "Name", "Category", "Material", "Color", "Qty", "Price")
        for col in self.results_tree['columns']:
            self.results_tree.column(col, width=100)
            self.results_tree.heading(col, text=col, anchor="w")
        
        # Add header for stock section
        if results:
            self.results_tree.insert("", "end", values=("", "", "", "", "", "", ""), tags=('header',))
            self.results_tree.insert("", "end", 
                values=("📦 STOCK ITEMS", "", "", "", "", "", ""), tags=('section',))
            
            for result in results:
                result = dict(result)
                self.results_tree.insert("", "end", values=(
                    result['sku'],
                    result['name'],
                    result['category'],
                    result['material'] or "",
                    result['color'] or "",
                    result['quantity'],
                    Formatters.format_currency(result['selling_price'])
                ), tags=('stock',))
        
        # Configure tags for styling
        self.results_tree.tag_configure('header', background='#f8f9fa')
        self.results_tree.tag_configure('section', background=Colors.PRIMARY, 
                                       foreground='white', font=('Arial', 10, 'bold'))
        self.results_tree.tag_configure('bill', background='#e8f5e8')
        self.results_tree.tag_configure('customer', background='#e3f2fd')
        self.results_tree.tag_configure('stock', background='#fff3cd')
    
    def clear_search(self):
        """Clear search results"""
        self.search_var.set("")
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.status_label.configure(text="Enter search term and press Search")