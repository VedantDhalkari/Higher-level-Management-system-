"""
Premium Dashboard with Modern Design
Features: Greeting card, stat cards, charts, and elegant data tables
"""
import customtkinter as ctk
from datetime import datetime
import threading
from tkinter import messagebox
from config import Colors, AppConfig
from utils import Formatters
from ui_components import (
    StatCard, GreetingCard, ModernTable, 
    StatusBadge, AnimatedButton
)
from charts import EarningsBarChart, TrendLineChart


class Dashboard(ctk.CTkFrame):
    """Premium dashboard with light purple theme"""
    
    def __init__(self, parent, switch_frame_callback, user_info):
        super().__init__(parent, fg_color=Colors.BG_LIGHT)
        self.parent = parent
        self.db = parent.db
        self.switch_frame = switch_frame_callback
        self.user_info = user_info
        
        self.setup_ui()
        self.load_metrics()
    
    def setup_ui(self):
        """Setup premium dashboard UI"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.setup_sidebar()
        
        # Main content area with scrolling
        self.main_container = ctk.CTkFrame(self, fg_color=Colors.BG_LIGHT)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Scrollable main content
        self.main_content = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color=Colors.BG_LIGHT
        )
        self.main_content.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        # Build dashboard sections
        self.setup_greeting_section()
        self.setup_metrics_section()
        self.setup_analytics_section()
        self.setup_recent_section()
    
    def setup_sidebar(self):
        """Setup modern sidebar with light theme"""
        sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, 
                              fg_color=Colors.SIDEBAR_BG)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Logo/Brand section
        brand_frame = ctk.CTkFrame(sidebar, fg_color=Colors.PRIMARY, 
                                  height=120, corner_radius=0)
        brand_frame.grid(row=0, column=0, sticky="ew")
        brand_frame.grid_propagate(False)
        
        # App logo/icon
        logo_icon = ctk.CTkLabel(
            brand_frame,
            text="💎",
            font=ctk.CTkFont(size=40)
        )
        logo_icon.pack(pady=(20, 5))
        
        brand_name = ctk.CTkLabel(
            brand_frame,
            text="Boutique Manager",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.TEXT_WHITE
        )
        brand_name.pack()
        
        brand_subtitle = ctk.CTkLabel(
            brand_frame,
            text="Pro Edition",
            font=ctk.CTkFont(size=11),
            text_color=Colors.TEXT_WHITE
        )
        brand_subtitle.pack()
        
        # Navigation section
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.grid(row=1, column=0, sticky="nsew", pady=20)
        sidebar.grid_rowconfigure(1, weight=1)
        
        # Navigation buttons
        nav_items = [
            ("📊", "Dashboard", self.show_dashboard, True),
            ("💰", "New Bill", lambda: self.switch_frame("billing"), False),
            ("📦", "Stock Management", lambda: self.verify_and_switch("stock"), False),
            ("📥", "New Stock", lambda: self.verify_and_switch("new_stock"), False),
            ("🔍", "Global Search", lambda: self.switch_frame("search"), False),
            ("📈", "Reports", self.show_reports, False),
            ("⚙️", "Settings", self.show_settings, False),
        ]
        
        for icon, text, command, is_active in nav_items:
            self.create_nav_button(nav_frame, icon, text, command, is_active)
        
        # Bottom section - User info
        bottom_frame = ctk.CTkFrame(sidebar, fg_color=Colors.BG_LIGHT, 
                                   corner_radius=15, height=100)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        bottom_frame.grid_propagate(False)
        
        # User avatar circle
        avatar_frame = ctk.CTkFrame(bottom_frame, fg_color=Colors.PRIMARY,
                                   width=45, height=45, corner_radius=23)
        avatar_frame.pack(pady=(15, 8))
        avatar_frame.pack_propagate(False)
        
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=self.user_info['username'][0].upper(),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=Colors.TEXT_WHITE
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        
        user_label = ctk.CTkLabel(
            bottom_frame,
            text=self.user_info['username'],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        user_label.pack()
        
        role_label = ctk.CTkLabel(
            bottom_frame,
            text="Administrator",
            font=ctk.CTkFont(size=11),
            text_color=Colors.TEXT_SECONDARY
        )
        role_label.pack()
        
        # Logout button
        logout_btn = ctk.CTkButton(
            sidebar,
            text="Logout",
            command=self.parent.logout,
            height=38,
            corner_radius=10,
            fg_color=Colors.DANGER,
            hover_color=Colors.DANGER,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        logout_btn.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
    
    def create_nav_button(self, parent, icon, text, command, is_active=False):
        """Create a navigation button"""
        btn_frame = ctk.CTkFrame(
            parent,
            fg_color=Colors.PRIMARY if is_active else "transparent",
            corner_radius=10,
            height=48
        )
        btn_frame.pack(fill="x", padx=15, pady=3)
        
        btn = ctk.CTkButton(
            btn_frame,
            text=f"{icon}  {text}",
            command=command,
            anchor="w",
            height=48,
            corner_radius=10,
            fg_color="transparent",
            hover_color=Colors.PRIMARY_LIGHT if not is_active else Colors.PRIMARY_DARK,
            text_color=Colors.TEXT_WHITE if is_active else Colors.TEXT_PRIMARY,
            font=ctk.CTkFont(size=14, weight="bold" if is_active else "normal")
        )
        btn.pack(fill="both", expand=True, padx=2, pady=2)
        
        return btn
    
    def setup_greeting_section(self):
        """Setup greeting card section"""
        # Create greeting card with action buttons
        greeting = GreetingCard(self.main_content, self.user_info['username'])
        greeting.grid(row=0, column=0, sticky="ew", pady=(0, 25))
        
        # Wire up button commands
        greeting.new_bill_btn.configure(command=lambda: self.switch_frame("billing"))
        greeting.view_stock_btn.configure(command=lambda: self.verify_and_switch("stock"))
        
        # Current date/time display
        time_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        time_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        time_frame.grid_columnconfigure(1, weight=1)
        
        date_label = ctk.CTkLabel(
            time_frame,
            text=datetime.now().strftime("%A, %d %B %Y"),
            font=ctk.CTkFont(size=13),
            text_color=Colors.TEXT_SECONDARY
        )
        date_label.grid(row=0, column=0, sticky="w")
        
        self.time_label = ctk.CTkLabel(
            time_frame,
            text=datetime.now().strftime("%I:%M %p"),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Colors.PRIMARY
        )
        self.time_label.grid(row=0, column=1, sticky="e")
        self.update_time()
    
    def setup_metrics_section(self):
        """Setup metric cards section"""
        metrics_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        metrics_container.grid(row=2, column=0, sticky="ew", pady=(0, 25))
        
        # Configure grid for 4 cards
        for i in range(4):
            metrics_container.grid_columnconfigure(i, weight=1, uniform="metric")
        
        # Create stat cards
        self.todays_sales_card = StatCard(
            metrics_container,
            title="Today's Sales",
            value="₹0",
            subtitle="Loading...",
            icon="💰",
            color=Colors.PRIMARY,
            height=150
        )
        self.todays_sales_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        self.monthly_revenue_card = StatCard(
            metrics_container,
            title="This Month",
            value="₹0",
            subtitle="Loading...",
            icon="📈",
            color=Colors.SUCCESS,
            height=150
        )
        self.monthly_revenue_card.grid(row=0, column=1, sticky="nsew", padx=6)
        
        self.low_stock_card = StatCard(
            metrics_container,
            title="Low Stock",
            value="0",
            subtitle="Items need restocking",
            icon="⚠️",
            color=Colors.WARNING,
            height=150
        )
        self.low_stock_card.grid(row=0, column=2, sticky="nsew", padx=6)
        
        self.transactions_card = StatCard(
            metrics_container,
            title="Transactions",
            value="0",
            subtitle="Today",
            icon="🧾",
            color=Colors.INFO,
            height=150
        )
        self.transactions_card.grid(row=0, column=3, sticky="nsew", padx=(12, 0))
    
    def setup_analytics_section(self):
        """Setup charts and analytics section"""
        analytics_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        analytics_container.grid(row=3, column=0, sticky="ew", pady=(0, 25))
        analytics_container.grid_columnconfigure(0, weight=2)
        analytics_container.grid_columnconfigure(1, weight=1)
        
        # Earnings chart
        self.earnings_chart = EarningsBarChart(analytics_container, height=320)
        self.earnings_chart.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        # Top categories/items
        top_items_frame = ctk.CTkFrame(analytics_container, fg_color=Colors.CARD_BG,
                                      corner_radius=15, border_width=1,
                                      border_color=Colors.BORDER_LIGHT)
        top_items_frame.grid(row=0, column=1, sticky="nsew")
        
        # Header
        header = ctk.CTkLabel(
            top_items_frame,
            text="Top Categories",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        header.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Sample top items
        self.top_items_container = ctk.CTkFrame(top_items_frame, fg_color="transparent")
        self.top_items_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.populate_top_items()
    
    def populate_top_items(self):
        """Populate top selling items/categories"""
        # Sample data (replace with real data)
        top_items = [
            ("💎", "Silk Sarees", "₹45,280", Colors.PRIMARY),
            ("👗", "Designer Wear", "₹32,150", Colors.SECONDARY),
            ("🎨", "Cotton Collection", "₹28,940", Colors.ACCENT),
            ("✨", "Accessories", "₹15,680", Colors.INFO),
        ]
        
        for icon, name, amount, color in top_items:
            item_frame = ctk.CTkFrame(self.top_items_container, 
                                     fg_color=Colors.BG_LIGHT,
                                     corner_radius=10, height=60)
            item_frame.pack(fill="x", pady=4)
            item_frame.pack_propagate(False)
            
            # Icon
            icon_label = ctk.CTkLabel(
                item_frame, text=icon,
                font=ctk.CTkFont(size=20)
            )
            icon_label.pack(side="left", padx=(15, 10))
            
            # Name and amount
            text_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True)
            
            name_label = ctk.CTkLabel(
                text_frame, text=name,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            )
            name_label.pack(anchor="w", pady=(10, 2))
            
            amount_label = ctk.CTkLabel(
                text_frame, text=amount,
                font=ctk.CTkFont(size=12),
                text_color=color,
                anchor="w"
            )
            amount_label.pack(anchor="w")
    
    def setup_recent_section(self):
        """Setup recent transactions section"""
        recent_frame = ctk.CTkFrame(self.main_content, fg_color=Colors.CARD_BG,
                                   corner_radius=15, border_width=1,
                                   border_color=Colors.BORDER_LIGHT)
        recent_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        
        # Header
        header_container = ctk.CTkFrame(recent_frame, fg_color="transparent")
        header_container.pack(fill="x", padx=25, pady=(20, 15))
        header_container.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            header_container,
            text="Recent Transactions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title.grid(row=0, column=0, sticky="w")
        
        refresh_btn = AnimatedButton(
            header_container,
            text="🔄 Refresh",
            command=self.load_metrics,
            width=100,
            height=32,
            fg_color=Colors.BG_LIGHT,
            text_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_LIGHT
        )
        refresh_btn.grid(row=0, column=1, sticky="e")
        
        # Table container
        table_container = ctk.CTkFrame(recent_frame, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        # Create modern table
        columns = ["Invoice", "Customer", "Amount", "Date", "Status"]
        column_widths = [4, 6, 4, 4, 3]
        
        self.transactions_table = ModernTable(
            table_container,
            columns=columns,
            column_widths=column_widths
        )
        self.transactions_table.pack(fill="both", expand=True)
    
    def load_metrics(self):
        """Load dashboard metrics asynchronously"""
        def load():
            try:
                # Today's sales
                sales_data = self.db.get_today_sales()
                if sales_data:
                    today_sales = sales_data['total_sales'] or 0
                    trans_count = sales_data['transaction_count'] or 0
                    
                    self.after(0, self.todays_sales_card.update_value,
                             Formatters.format_currency(today_sales),
                             f"{trans_count} transactions")
                    
                    self.after(0, self.transactions_card.update_value,
                             str(trans_count),
                             "Completed today")
                
                # Monthly revenue
                with self.db.get_connection() as conn:
                    monthly_data = conn.execute(
                        """SELECT SUM(total_amount) as total, COUNT(*) as count
                           FROM sales 
                           WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')"""
                    ).fetchone()
                
                if monthly_data:
                    monthly_total = monthly_data['total'] or 0
                    monthly_count = monthly_data['count'] or 0
                    self.after(0, self.monthly_revenue_card.update_value,
                             Formatters.format_currency(monthly_total),
                             f"{monthly_count} transactions")
                
                # Low stock items
                low_stock = self.db.get_low_stock_items()
                low_stock_count = len(low_stock) if low_stock else 0
                
                self.after(0, self.low_stock_card.update_value,
                         str(low_stock_count),
                         "Items need restocking")
                
                # Recent transactions
                recent_trans = self.db.get_recent_transactions(8)
                self.after(0, self.update_recent_transactions, recent_trans)
                
                # Update chart with real data
                self.after(0, self.update_earnings_chart)
                
            except Exception as e:
                print(f"Error loading metrics: {e}")
        
        threading.Thread(target=load, daemon=True).start()
    
    def update_recent_transactions(self, transactions):
        """Update recent transactions table"""
        self.transactions_table.clear_rows()
        
        for trans in transactions:
            trans = dict(trans)
            
            # Create status badge text
            status = "Completed"
            
            row_data = [
                trans.get('invoice_number', 'N/A'),
                trans.get('customer_name', 'Walk-in Customer'),
                Formatters.format_currency(trans.get('total_amount', 0)),
                Formatters.format_date(trans.get('created_at', '')),
                status
            ]
            
            # Add row with status color
            row_colors = [
                Colors.TEXT_PRIMARY,
                Colors.TEXT_PRIMARY,
                Colors.SUCCESS,
                Colors.TEXT_SECONDARY,
                Colors.SUCCESS
            ]
            
            self.transactions_table.add_row(row_data, row_colors)
    
    def update_earnings_chart(self):
        """Update earnings chart with real data"""
        try:
            # Get last 7 days of sales
            with self.db.get_connection() as conn:
                query = """
                    SELECT 
                        DATE(created_at) as date,
                        SUM(total_amount) as total
                    FROM sales
                    WHERE created_at >= date('now', '-7 days')
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """
                results = conn.execute(query).fetchall()
                
                if results:
                    dates = [datetime.strptime(r['date'], '%Y-%m-%d').strftime('%a') 
                            for r in results]
                    amounts = [r['total'] or 0 for r in results]
                    
                    # Pad with zeros if less than 7 days
                    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    while len(dates) < 7:
                        dates.insert(0, days[7-len(dates)-1])
                        amounts.insert(0, 0)
                    
                    self.earnings_chart.update_chart(dates, amounts)
        except Exception as e:
            print(f"Error updating chart: {e}")
    
    def update_time(self):
        """Update time display"""
        self.time_label.configure(text=datetime.now().strftime("%I:%M %p"))
        self.after(60000, self.update_time)
    
    def verify_and_switch(self, frame_name):
        """Verify PIN before switching to protected frames"""
        from auth import PinDialog
        
        if frame_name in ["stock", "new_stock"]:
            pin_dialog = PinDialog(self.parent, "Enter Admin PIN",
                                 self.parent.auth.verify_admin_pin)
            if pin_dialog.show():
                self.switch_frame(frame_name)
        else:
            self.switch_frame(frame_name)
    
    def show_dashboard(self):
        """Already on dashboard"""
        pass
    
    def show_reports(self):
        """Show reports"""
        messagebox.showinfo("Coming Soon", "Reports module will be available soon!")
    
    def show_settings(self):
        """Show settings"""
        messagebox.showinfo("Coming Soon", "Settings module will be available soon!")