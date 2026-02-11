"""
Stock Management Module
View, edit, and manage inventory with premium light theme
"""

import customtkinter as ctk
from tkinter import messagebox
import config
from ui_components import AnimatedButton, SearchBar


class StockManagementModule(ctk.CTkFrame):
    """Stock management interface"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="📦 Stock Management",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_1, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=(0, config.SPACING_LG), anchor="w")
        
        # Search bar
        search_bar = SearchBar(
            self,
            placeholder="Search by SKU, Type, Color, Material...",
            on_search=self._on_search
        )
        search_bar.pack(fill="x", pady=(0, config.SPACING_LG))
        self.search_entry = search_bar.entry
        
        # Stock table
        self.table_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        self.table_frame.pack(fill="both", expand=True)
        self.table_frame.configure(border_width=1, border_color=config.COLOR_BORDER)
        
        self._load_stock()
    
    def _on_search(self, query):
        """Handle search"""
        self._load_stock(query)
    
    def _load_stock(self, search_query=""):
        """Load stock data"""
        # Clear table
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # Headers
        headers = ["SKU", "Type", "Material", "Color", "Qty", "Purchase ₹", "Selling ₹", "Supplier", "Actions"]
        header_frame = ctk.CTkFrame(
            self.table_frame,
            fg_color=config.COLOR_PRIMARY,
            corner_radius=0,
            height=45
        )
        header_frame.pack(fill="x", pady=(0, config.SPACING_SM))
        header_frame.pack_propagate(False)
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
                text_color=config.COLOR_TEXT_WHITE,
                width=100 if i < 8 else 120
            )
            label.grid(row=0, column=i, padx=config.SPACING_XS, pady=config.SPACING_SM, sticky="w")
        
        # Get stock data
        if search_query:
            items = self.db.execute_query(
                """SELECT item_id, sku_code, saree_type, material, color, quantity,
                   purchase_price, selling_price, supplier_name
                   FROM inventory
                   WHERE sku_code LIKE ? OR saree_type LIKE ? OR color LIKE ? OR material LIKE ?
                   ORDER BY added_date DESC""",
                (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%")
            )
        else:
            items = self.db.execute_query(
                """SELECT item_id, sku_code, saree_type, material, color, quantity,
                   purchase_price, selling_price, supplier_name
                   FROM inventory ORDER BY added_date DESC"""
            )
        
        # Display items
        for idx, item in enumerate(items):
            bg_color = config.COLOR_BG_HOVER if idx % 2 == 0 else "transparent"
            
            # Highlight low stock
            if item[5] <= config.LOW_STOCK_THRESHOLD:
                bg_color = "#FEF3C7"  # Light amber for low stock
            
            item_frame = ctk.CTkFrame(self.table_frame, fg_color=bg_color, height=40)
            item_frame.pack(fill="x", pady=1)
            item_frame.pack_propagate(False)
            
            # Data
            data = [
                item[1],  # SKU
                item[2][:20],  # Type (truncated)
                item[3][:15],  # Material
                item[4][:15],  # Color
                str(item[5]),  # Quantity
                f"₹{item[6]:.0f}",  # Purchase price
                f"₹{item[7]:.0f}",  # Selling price
                (item[8] or "N/A")[:15]  # Supplier
            ]
            
            for i, value in enumerate(data):
                text_color = config.COLOR_TEXT_PRIMARY
                if item[5] <= config.LOW_STOCK_THRESHOLD and i == 4:
                    text_color = config.COLOR_DANGER
                
                label = ctk.CTkLabel(
                    item_frame,
                    text=value,
                    font=ctk.CTkFont(size=config.FONT_SIZE_SMALL - 1),
                    text_color=text_color,
                    width=100
                )
                label.grid(row=0, column=i, padx=config.SPACING_XS, sticky="w")
            
            # Actions
            actions_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=8, padx=config.SPACING_XS)
            
            ctk.CTkButton(
                actions_frame,
                text="Edit",
                width=50,
                height=25,
                fg_color=config.COLOR_INFO,
                font=ctk.CTkFont(size=config.FONT_SIZE_SMALL - 1),
                command=lambda id=item[0]: self._edit_item(id)
            ).pack(side="left", padx=1)
            
            ctk.CTkButton(
                actions_frame,
                text="Delete",
                width=50,
                height=25,
                fg_color=config.COLOR_DANGER,
                font=ctk.CTkFont(size=config.FONT_SIZE_SMALL - 1),
                command=lambda id=item[0]: self._delete_item(id)
            ).pack(side="left", padx=1)
    
    def _edit_item(self, item_id):
        """Edit stock item"""
        # Get item details
        item = self.db.execute_query(
            "SELECT * FROM inventory WHERE item_id = ?",
            (item_id,)
        )[0]
        
        # Create edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Stock Item")
        dialog.geometry("500x650")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Main frame
        main_frame = ctk.CTkScrollableFrame(dialog, fg_color=config.COLOR_BG_CARD)
        main_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        # Fields
        fields = [
            ("SKU Code", item[1]),
            ("Saree Type", item[2]),
            ("Material", item[3]),
            ("Color", item[4]),
            ("Design", item[5] or ""),
            ("Quantity", str(item[6])),
            ("Purchase Price", str(item[7])),
            ("Selling Price", str(item[8])),
            ("Supplier", item[9] or ""),
            ("Category", item[10] or "")
        ]
        
        entries = {}
        for label, value in fields:
            ctk.CTkLabel(
                main_frame,
                text=label,
                font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
                text_color=config.COLOR_TEXT_PRIMARY
            ).pack(pady=(config.SPACING_SM, 2), anchor="w")
            
            entry = ctk.CTkEntry(main_frame, height=35)
            entry.insert(0, value)
            entry.pack(fill="x", pady=(0, config.SPACING_XS))
            entries[label] = entry
        
        def save_changes():
            try:
                self.db.execute_query(
                    """UPDATE inventory SET sku_code=?, saree_type=?, material=?, color=?,
                       design=?, quantity=?, purchase_price=?, selling_price=?, 
                       supplier_name=?, category=?, last_updated=CURRENT_TIMESTAMP
                       WHERE item_id=?""",
                    (entries["SKU Code"].get(), entries["Saree Type"].get(),
                     entries["Material"].get(), entries["Color"].get(),
                     entries["Design"].get(), int(entries["Quantity"].get()),
                     float(entries["Purchase Price"].get()),
                     float(entries["Selling Price"].get()),
                     entries["Supplier"].get(), entries["Category"].get(), item_id)
                )
                messagebox.showinfo("Success", "Item updated successfully")
                dialog.destroy()
                self._load_stock()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")
        
        AnimatedButton(
            main_frame,
            text="💾 Save Changes",
            fg_color=config.COLOR_PRIMARY,
            command=save_changes
        ).pack(pady=config.SPACING_LG)
    
    def _delete_item(self, item_id):
        """Delete stock item"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            try:
                self.db.execute_query("DELETE FROM inventory WHERE item_id = ?", (item_id,))
                messagebox.showinfo("Success", "Item deleted successfully")
                self._load_stock()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
