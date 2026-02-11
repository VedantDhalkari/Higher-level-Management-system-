"""
Global Search Module
Search across bills, customers, and inventory
"""

import customtkinter as ctk
from tkinter import messagebox
import config
from ui_components import AnimatedButton


class GlobalSearchModule(ctk.CTkFrame):
    """Global search interface"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="🔍 Global Search",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_1, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=(0, config.SPACING_LG), anchor="w")
        
        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, config.SPACING_LG))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            height=config.BUTTON_HEIGHT_LG,
            placeholder_text="Search bills, customers, items, SKU codes...",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            border_color=config.COLOR_BORDER,
            border_width=2
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, config.SPACING_SM))
        
        search_btn = AnimatedButton(
            search_frame,
            text="🔍 Search",
            width=150,
            height=config.BUTTON_HEIGHT_LG,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_LIGHT,
            command=self._perform_search
        )
        search_btn.pack(side="left")
        
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        
        # Results area
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        self.results_frame.pack(fill="both", expand=True)
        self.results_frame.configure(border_width=1, border_color=config.COLOR_BORDER)
        
        # Initial message
        self._show_initial_message()
    
    def _show_initial_message(self):
        """Show initial search message"""
        msg_label = ctk.CTkLabel(
            self.results_frame,
            text="🔍\n\nEnter a search term to find\nbills, customers, or inventory items",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            text_color=config.COLOR_TEXT_SECONDARY,
            justify="center"
        )
        msg_label.pack(expand=True, pady=config.SPACING_XL * 2)
    
    def _perform_search(self):
        """Perform global search"""
        query = self.search_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Empty Search", "Please enter a search term")
            return
        
        # Clear results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Search bills
        self._create_section_header("Bills / Invoices", config.ICON_BILLING)
        
        bills = self.db.execute_query(
            """SELECT bill_number, customer_name, customer_phone, final_amount, sale_date
               FROM sales
               WHERE bill_number LIKE ? OR customer_name LIKE ? OR customer_phone LIKE ?
               ORDER BY sale_date DESC LIMIT 10""",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        
        if bills:
            for bill in bills:
                self._create_bill_card(bill)
        else:
            self._create_no_results("No bills found")
        
        # Search inventory
        self._create_section_header("Inventory Items", config.ICON_INVENTORY)
        
        items = self.db.execute_query(
            """SELECT sku_code, saree_type, material, color, quantity, selling_price
               FROM inventory
               WHERE sku_code LIKE ? OR saree_type LIKE ? OR material LIKE ? OR color LIKE ?
               LIMIT 10""",
            (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")
        )
        
        if items:
            for item in items:
                self._create_item_card(item)
        else:
            self._create_no_results("No items found")
    
    def _create_section_header(self, title, icon):
        """Create section header"""
        header_label = ctk.CTkLabel(
            self.results_frame,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        header_label.pack(pady=(config.SPACING_LG, config.SPACING_SM), padx=config.SPACING_LG, anchor="w")
    
    def _create_bill_card(self, bill):
        """Create bill result card"""
        card = ctk.CTkFrame(
            self.results_frame,
            fg_color=config.COLOR_BG_HOVER,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        card.pack(fill="x", padx=config.SPACING_LG, pady=config.SPACING_XS)
        
        text = f"Bill: {bill[0]} | Customer: {bill[1] or 'Walk-in'} | Amount: ₹{bill[2]:,.2f} | Date: {bill[4][:16]}"
        label = ctk.CTkLabel(
            card,
            text=text,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        label.pack(pady=config.SPACING_SM, padx=config.SPACING_MD, anchor="w")
    
    def _create_item_card(self, item):
        """Create item result card"""
        card = ctk.CTkFrame(
            self.results_frame,
            fg_color=config.COLOR_BG_HOVER,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        card.pack(fill="x", padx=config.SPACING_LG, pady=config.SPACING_XS)
        
        text = f"SKU: {item[0]} | {item[1]} - {item[2]} ({item[3]}) | Stock: {item[4]} | Price: ₹{item[5]:,.2f}"
        label = ctk.CTkLabel(
            card,
            text=text,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        label.pack(pady=config.SPACING_SM, padx=config.SPACING_MD, anchor="w")
    
    def _create_no_results(self, message):
        """Create no results message"""
        label = ctk.CTkLabel(
            self.results_frame,
            text=message,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        label.pack(padx=config.SPACING_LG, pady=config.SPACING_SM, anchor="w")
