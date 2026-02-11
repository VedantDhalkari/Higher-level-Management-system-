"""
Dashboard Module
Main dashboard with sidebar navigation and premium metrics display
"""

import customtkinter as ctk
from typing import Callable
import config
from ui_components import StatCard, GreetingCard, ModernTable, SidebarButton
from charts import EarningsBarChart, CategoryList


class Dashboard(ctk.CTkFrame):
    """Main dashboard with sidebar and content area"""
    
    def __init__(self, parent, current_user: dict, db_manager, 
                 on_navigate: Callable, **kwargs):
        """
        Create dashboard
        
        Args:
            parent: Parent widget
            current_user: Dictionary with user info (id, username, role)
            db_manager: DatabaseManager instance
            on_navigate: Callback for navigation (receives screen name)
        """
        super().__init__(parent, fg_color=config.COLOR_BG_MAIN, **kwargs)
        
        self.current_user = current_user
        self.db = db_manager
        self.on_navigate = on_navigate
        self.active_screen = "dashboard"
        
        # Create sidebar
        self._create_sidebar()
        
        # Create main content area
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=config.COLOR_BG_MAIN,
            scrollbar_button_color=config.COLOR_PRIMARY,
            scrollbar_button_hover_color=config.COLOR_PRIMARY_LIGHT
        )
        self.content_frame.pack(side="right", fill="both", expand=True, 
                               padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        # Load dashboard content
        self. load_dashboard_content()
    
    def _create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = ctk.CTkFrame(
            self,
            width=config.SIDEBAR_WIDTH,
            fg_color=config.COLOR_BG_SIDEBAR,
            corner_radius=0
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo/Brand section
        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=120)
        brand_frame.pack(fill="x", pady=(config.SPACING_XL, config.SPACING_LG))
        brand_frame.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(
            brand_frame,
            text=config.ICON_LOGO,
            font=ctk.CTkFont(size=40)
        )
        logo_label.pack(pady=(config.SPACING_SM, 0))
        
        app_name_label = ctk.CTkLabel(
            brand_frame,
            text="Boutique Manager",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        app_name_label.pack()
        
        edition_label = ctk.CTkLabel(
            brand_frame,
            text=config.COMPANY,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        edition_label.pack()
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=config.SPACING_MD, pady=config.SPACING_SM)
        
        self.nav_buttons = {}
        
        nav_items = [
            ("dashboard", "Dashboard", config.ICON_DASHBOARD, lambda: self._navigate("dashboard")),
            ("billing", "New Bill", config.ICON_BILLING, lambda: self._navigate("billing")),
            ("stock", "Stock Management", config.ICON_STOCK, lambda: self._navigate("stock")),
            ("new_stock", "New Stock", config.ICON_NEW_STOCK, lambda: self._navigate("new_stock")),
            ("search", "Global Search", config.ICON_SEARCH, lambda: self._navigate("search")),
            ("reports", "Reports", config.ICON_REPORTS, lambda: self._navigate("reports")),
            ("settings", "Settings", config.ICON_SETTINGS, lambda: self._navigate("settings")),
        ]
        
        for key, text, icon, command in nav_items:
            btn = SidebarButton(nav_frame, text=text, icon=icon, command=command)
            btn.pack(fill="x", pady=config.SPACING_XS)
            self.nav_buttons[key] = btn
        
        # Set dashboard as active
        self.nav_buttons["dashboard"].set_active(True)
        
        # User profile section (bottom)
        user_frame = ctk.CTkFrame(
            sidebar,
            fg_color=config.COLOR_BG_HOVER,
            corner_radius=config.RADIUS_MD,
            height=80
        )
        user_frame.pack(side="bottom", fill="x", padx=config.SPACING_MD, 
                       pady=config.SPACING_MD)
        user_frame.pack_propagate(False)
        
        # User avatar circle
        avatar_frame = ctk.CTkFrame(
            user_frame,
            width=50,
            height=50,
            fg_color=config.COLOR_PRIMARY_LIGHT,
            corner_radius=25
        )
        avatar_frame.pack(side="left", padx=config.SPACING_MD, pady=config.SPACING_SM)
        avatar_frame.pack_propagate(False)
        
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=config.ICON_USER,
            font=ctk.CTkFont(size=24)
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # User info
        user_info_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_info_frame.pack(side="left", fill="both", expand=True)
        
        username_label = ctk.CTkLabel(
            user_info_frame,
            text=self.current_user['username'],
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        username_label.pack(anchor="w", pady=(config.SPACING_SM, 0))
        
        role_label = ctk.CTkLabel(
            user_info_frame,
            text=self.current_user['role'].capitalize(),
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        role_label.pack(anchor="w")
        
        # Logout button
        logout_btn = ctk.CTkButton(
            sidebar,
            text="🚪 Logout",
            width=220,
            height=40,
            fg_color=config.COLOR_DANGER,
            hover_color="#DC2626",
            text_color=config.COLOR_TEXT_WHITE,
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            corner_radius=config.RADIUS_MD,
            command=lambda: self._navigate("logout")
        )
        logout_btn.pack(side="bottom", padx=config.SPACING_MD, pady=(0, config.SPACING_MD))
    
    def _navigate(self, screen: str):
        """Handle navigation"""
        # Update active button
        for key, btn in self.nav_buttons.items():
            btn.set_active(key == screen)
        
        self.active_screen = screen
        
        # Call navigation callback
        if self.on_navigate:
            self.on_navigate(screen)
    
    def load_dashboard_content(self):
        """Load dashboard metrics and widgets"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Greeting card
        greeting = GreetingCard(
            self.content_frame,
            username=self.current_user['username'],
            on_new_bill=lambda: self._navigate("billing"),
            on_view_stock=lambda: self._navigate("stock")
        )
        greeting.pack(fill="x", pady=(0, config.SPACING_LG))
        
        # Get metrics from database
        metrics = self.db.get_dashboard_metrics()
        
        # Metrics row
        metrics_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, config.SPACING_LG))
        
        # Configure grid
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)
        
        # Today's Sales card
        card1 = StatCard(
            metrics_frame,
            title="Today's Sales",
            value=f"₹{metrics['today_sales_amount']:,.0f}",
            subtitle=f"{metrics['today_sales_count']} transactions",
            icon=config.ICON_SALES,
            icon_color=config.COLOR_PRIMARY
        )
        card1.grid(row=0, column=0, padx=(0, config.SPACING_SM), sticky="ew")
        
        # This Month card
        card2 = StatCard(
            metrics_frame,
            title="This Month",
            value=f"₹{metrics['month_sales_amount']:,.0f}",
            subtitle=f"{metrics['month_sales_count']} transactions",
            icon=config.ICON_REVENUE,
            icon_color=config.COLOR_SUCCESS
        )
        card2.grid(row=0, column=1, padx=config.SPACING_SM, sticky="ew")
        
        # Low Stock card
        low_stock_color = config.COLOR_WARNING if metrics['low_stock_count'] > 0 else config.COLOR_SUCCESS
        card3 = StatCard(
            metrics_frame,
            title="Low Stock",
            value=str(metrics['low_stock_count']),
            subtitle="Items need restocking" if metrics['low_stock_count'] > 0 else "All items stocked",
            icon=config.ICON_WARNING,
            icon_color=low_stock_color
        )
        card3.grid(row=0, column=2, padx=config.SPACING_SM, sticky="ew")
        
        # Transactions card
        card4 = StatCard(
            metrics_frame,
            title="Transactions",
            value=str(metrics['today_sales_count']),
            subtitle="Completed today",
            icon=config.ICON_TRANSACTIONS,
            icon_color=config.COLOR_INFO
        )
        card4.grid(row=0, column=3, padx=(config.SPACING_SM, 0), sticky="ew")
        
        # Analytics section (2 columns)
        analytics_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        analytics_frame.pack(fill="both", expand=True, pady=(0, config.SPACING_LG))
        
        analytics_frame.grid_columnconfigure(0, weight=2)
        analytics_frame.grid_columnconfigure(1, weight=1)
        
        # Earnings chart (left, 2/3 width)
        sales_data = self.db.get_sales_by_period("week")
        
        # Process data for chart
        if sales_data:
            chart_data = [(label or "N/A", amount or 0) for label, amount in sales_data]
        else:
            # Default data if no sales
            chart_data = [("Mon", 0), ("Tue", 0), ("Wed", 0), ("Thu", 0), 
                         ("Fri", 0), ("Sat", 0), ("Sun", 0)]
        
        earnings_chart = EarningsBarChart(
            analytics_frame,
            data=chart_data,
            period="This Week"
        )
        earnings_chart.grid(row=0, column=0, sticky="nsew", padx=(0, config.SPACING_SM))
        
        # Top categories (right, 1/3 width)
        categories = self.db.get_top_categories(5)
        
        category_list = CategoryList(
            analytics_frame,
            categories=categories
        )
        category_list.grid(row=0, column=1, sticky="nsew", padx=(config.SPACING_SM, 0))
        
        # Recent transactions table
        table_container = ctk.CTkFrame(
            self.content_frame,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG
        )
        table_container.pack(fill="both", expand=True)
        table_container.configure(border_width=1, border_color=config.COLOR_BORDER)
        
        # Header with refresh button
        header_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Recent Transactions",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        header_label.pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=100,
            height=32,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_LIGHT,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
            corner_radius=config.RADIUS_SM,
            command=self.load_dashboard_content
        )
        refresh_btn.pack(side="right")
        
        # Table
        table = ModernTable(
            table_container,
            headers=["Invoice #", "Customer", "Amount", "Date", "Status"]
        )
        table.pack(fill="both", expand=True, padx=config.SPACING_LG, 
                  pady=(0, config.SPACING_LG))
        
        # Get recent transactions
        transactions = self.db.get_recent_transactions(10)
        
        if transactions:
            for bill_no, cust_name, amount, date in transactions:
                table.add_row([
                    bill_no,
                    cust_name or "Walk-in",
                    f"₹{amount:,.2f}",
                    date[:16],
                    "Completed"
                ], amount_color=config.COLOR_SUCCESS)
        else:
            # No transactions message
            no_data_label = ctk.CTkLabel(
                table.content_frame,
                text="No transactions yet",
                font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
                text_color=config.COLOR_TEXT_SECONDARY
            )
            no_data_label.pack(pady=config.SPACING_XL)
    
    def show_content(self, content_widget):
        """Show a different content widget (for other modules)"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Pack new content
        content_widget.pack(fill="both", expand=True)
