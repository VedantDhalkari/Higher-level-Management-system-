"""
Reports Module
Sales analytics and reporting with premium visualizations
"""

import customtkinter as ctk
from datetime import datetime, timedelta
import config
from charts import EarningsBarChart


class ReportsModule(ctk.CTkFrame):
    """Reports and analytics interface"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="📈 Reports & Analytics",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_1, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=(0, config.SPACING_LG), anchor="w")
        
        # Period selector
        selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        selector_frame.pack(fill="x", pady=(0, config.SPACING_LG))
        
        ctk.CTkLabel(
            selector_frame,
            text="Select Period:",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(0, config.SPACING_SM))
        
        self.period_var = ctk.StringVariable(value="week")
        
        ctk.CTkRadioButton(
            selector_frame,
            text="Today",
            variable=self.period_var,
            value="today",
            fg_color=config.COLOR_PRIMARY,
            command=self._load_reports
        ).pack(side="left", padx=config.SPACING_SM)
        
        ctk.CTkRadioButton(
            selector_frame,
            text="This Week",
            variable=self.period_var,
            value="week",
            fg_color=config.COLOR_PRIMARY,
            command=self._load_reports
        ).pack(side="left", padx=config.SPACING_SM)
        
        ctk.CTkRadioButton(
            selector_frame,
            text="This Month",
            variable=self.period_var,
            value="month",
            fg_color=config.COLOR_PRIMARY,
            command=self._load_reports
        ).pack(side="left", padx=config.SPACING_SM)
        
        # Reports content
        self.reports_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.reports_frame.pack(fill="both", expand=True)
        
        self._load_reports()
    
    def _load_reports(self):
        """Load reports for selected period"""
        # Clear content
        for widget in self.reports_frame.winfo_children():
            widget.destroy()
        
        period = self.period_var.get()
        
        # Summary metrics
        metrics_frame = ctk.CTkFrame(self.reports_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, config.SPACING_LG))
        
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)
        
        # Get period data
        if period == "today":
            date_filter = datetime.now().strftime("%Y-%m-%d")
            sales_data = self.db.execute_query(
                """SELECT COUNT(*), COALESCE(SUM(final_amount), 0), 
                   COALESCE(AVG(final_amount), 0)
                   FROM sales WHERE DATE(sale_date) = ?""",
                (date_filter,)
            )[0]
            period_label = "Today"
        elif period == "week":
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            sales_data = self.db.execute_query(
                """SELECT COUNT(*), COALESCE(SUM(final_amount), 0), 
                   COALESCE(AVG(final_amount), 0)
                   FROM sales WHERE DATE(sale_date) >= ?""",
                (week_ago,)
            )[0]
            period_label = "This Week"
        else:
            month_start = datetime.now().strftime("%Y-%m-01")
            sales_data = self.db.execute_query(
                """SELECT COUNT(*), COALESCE(SUM(final_amount), 0), 
                   COALESCE(AVG(final_amount), 0)
                   FROM sales WHERE DATE(sale_date) >= ?""",
                (month_start,)
            )[0]
            period_label = "This Month"
        
        # Create metric cards
        self._create_metric_card(
            metrics_frame, 0, "Total Sales", 
            f"₹{sales_data[1]:,.2f}", config.COLOR_PRIMARY
        )
        self._create_metric_card(
            metrics_frame, 1, "Transactions", 
            str(sales_data[0]), config.COLOR_SUCCESS
        )
        self._create_metric_card(
            metrics_frame, 2, "Average Sale", 
            f"₹{sales_data[2]:,.2f}", config.COLOR_INFO
        )
        
        # Total items sold
        total_items = self.db.execute_query(
            """SELECT COALESCE(SUM(si.quantity), 0)
               FROM sale_items si
               JOIN sales s ON si.sale_id = s.sale_id
               WHERE DATE(s.sale_date) >= ?""",
            (week_ago if period == "week" else 
             month_start if period == "month" else date_filter,)
        )[0][0]
        
        self._create_metric_card(
            metrics_frame, 3, "Items Sold", 
            str(total_items), config.COLOR_WARNING
        )
        
        # Earnings chart
        sales_time_data = self.db.get_sales_by_period(period)
        if sales_time_data:
            chart_data = [(label or "N/A", amount or 0) for label, amount in sales_time_data]
        else:
            chart_data = []
        
        earnings_chart = EarningsBarChart(
            self.reports_frame,
            data=chart_data,
            period=period_label
        )
        earnings_chart.pack(fill="both", expand=True, pady=(0, config.SPACING_LG))
        
        # Top selling items
        top_items_frame = ctk.CTkFrame(
            self.reports_frame,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        top_items_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            top_items_frame,
            text="Top Selling Items",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        ).pack(pady=config.SPACING_LG, padx=config.SPACING_LG, anchor="w")
        
        # Get top items
        top_items = self.db.execute_query(
            """SELECT si.item_name, SUM(si.quantity) as qty, SUM(si.total_price) as total
               FROM sale_items si
               JOIN sales s ON si.sale_id = s.sale_id
               WHERE DATE(s.sale_date) >= ?
               GROUP BY si.item_name
               ORDER BY qty DESC
               LIMIT 10""",
            (week_ago if period == "week" else 
             month_start if period == "month" else date_filter,)
        )
        
        scroll_frame = ctk.CTkScrollableFrame(
            top_items_frame,
            fg_color="transparent",
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        scroll_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, 
                         pady=(0, config.SPACING_LG))
        
        if top_items:
            for idx, (item_name, qty, total) in enumerate(top_items):
                bg = config.COLOR_BG_HOVER if idx % 2 == 0 else "transparent"
                item_frame = ctk.CTkFrame(scroll_frame, fg_color=bg)
                item_frame.pack(fill="x", pady=1)
                
                ctk.CTkLabel(
                    item_frame,
                    text=f"{idx+1}. {item_name}",
                    font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
                    text_color=config.COLOR_TEXT_PRIMARY
                ).pack(side="left", padx=config.SPACING_MD, pady=config.SPACING_SM)
                
                ctk.CTkLabel(
                    item_frame,
                    text=f"Qty: {qty} | Total: ₹{total:,.2f}",
                    font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
                    text_color=config.COLOR_TEXT_SECONDARY
                ).pack(side="right", padx=config.SPACING_MD, pady=config.SPACING_SM)
        else:
            ctk.CTkLabel(
                scroll_frame,
                text="No sales data available",
                font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
                text_color=config.COLOR_TEXT_SECONDARY
            ).pack(pady=config.SPACING_XL)
    
    def _create_metric_card(self, parent, column, title, value, color):
        """Create a metric card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        card.grid(row=0, column=column, padx=config.SPACING_XS if column < 3 else 0, sticky="ew")
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        ).pack(pady=(config.SPACING_MD, config.SPACING_XS))
        
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_2, weight="bold"),
            text_color=color
        ).pack(pady=(0, config.SPACING_MD))
