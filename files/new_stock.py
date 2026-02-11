"""
New Stock Entry Module
Add new inventory items with validated form
"""

import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import config
from ui_components import AnimatedButton


class NewStockModule(ctk.CTkFrame):
    """New stock entry interface"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="📥 Add New Stock",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_1, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=(0, config.SPACING_LG), anchor="w")
        
        # Form card
        form_card = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        form_card.pack(fill="both", expand=True)
        
        # Scrollable form
        scroll_frame = ctk.CTkScrollableFrame(
            form_card,
            fg_color="transparent",
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        scroll_frame.pack(fill="both", expand=True, padx=config.SPACING_XL, pady=config.SPACING_XL)
        
        # Form fields
        fields = [
            ("SKU Code*", "sku_code", "text"),
            ("Saree Type*", "saree_type", "option"),
            ("Material*", "material", "option"),
            ("Color*", "color", "text"),
            ("Design", "design", "text"),
            ("Quantity*", "quantity", "number"),
            ("Purchase Price (₹)*", "purchase_price", "number"),
            ("Selling Price (₹)*", "selling_price", "number"),
            ("Supplier Name", "supplier", "text"),
            ("Category", "category", "option")
        ]
        
        self.entries = {}
        
        for label, key, field_type in fields:
            # Label
            lbl = ctk.CTkLabel(
                scroll_frame,
                text=label,
                font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
                text_color=config.COLOR_TEXT_PRIMARY
            )
            lbl.pack(pady=(config.SPACING_MD, config.SPACING_XS), anchor="w")
            
            # Input field
            if field_type == "option":
                if "Type" in label:
                    values = config.SAREE_TYPES
                elif "Material" in label:
                    values = config.MATERIAL_TYPES
                elif "Category" in label:
                    values = config.STOCK_CATEGORIES
                else:
                    values = []
                
                entry = ctk.CTkComboBox(
                    scroll_frame,
                    height=config.INPUT_HEIGHT,
                    values=values,
                    border_color=config.COLOR_BORDER,
                    border_width=1,
                    button_color=config.COLOR_PRIMARY,
                    button_hover_color=config.COLOR_PRIMARY_LIGHT
                )
            else:
                entry = ctk.CTkEntry(
                    scroll_frame,
                    height=config.INPUT_HEIGHT,
                    border_color=config.COLOR_BORDER,
                    border_width=1
                )
            
            entry.pack(fill="x", pady=(0, config.SPACING_XS))
            self.entries[key] = entry
        
        # Buttons
        button_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        button_frame.pack(pady=config.SPACING_XL)
        
        AnimatedButton(
            button_frame,
            text="💾 Save Stock",
            width=180,
            height=config.BUTTON_HEIGHT_LG,
            fg_color=config.COLOR_SUCCESS,
            hover_color="#059669",
            command=self._save_stock
        ).pack(side="left", padx=config.SPACING_SM)
        
        AnimatedButton(
            button_frame,
            text="🗑️ Clear Form",
            width=180,
            height=config.BUTTON_HEIGHT_LG,
            fg_color=config.COLOR_TEXT_SECONDARY,
            hover_color="#4B5563",
            command=self._clear_form
        ).pack(side="left", padx=config.SPACING_SM)
    
    def _save_stock(self):
        """Save new stock item"""
        try:
            # Validate required fields
            required = ["sku_code", "saree_type", "material", "color", "quantity", 
                       "purchase_price", "selling_price"]
            
            for field in required:
                value = self.entries[field].get()
                if not value or (isinstance(value, str) and value.strip() == ""):
                    field_name = field.replace("_", " ").title()
                    messagebox.showerror("Validation Error", f"{field_name} is required")
                    return
            
            # Insert into database
            self.db.execute_insert(
                """INSERT INTO inventory (sku_code, saree_type, material, color, design,
                   quantity, purchase_price, selling_price, supplier_name, category)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    self.entries["sku_code"].get().strip(),
                    self.entries["saree_type"].get(),
                    self.entries["material"].get(),
                    self.entries["color"].get().strip(),
                    self.entries["design"].get().strip() or None,
                    int(self.entries["quantity"].get()),
                    float(self.entries["purchase_price"].get()),
                    float(self.entries["selling_price"].get()),
                    self.entries["supplier"].get().strip() or None,
                    self.entries["category"].get() or None
                )
            )
            
            messagebox.showinfo("Success", "Stock item added successfully!")
            self._clear_form()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "SKU Code already exists")
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for quantity and prices")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add stock: {str(e)}")
    
    def _clear_form(self):
        """Clear all form fields"""
        for entry in self.entries.values():
            if isinstance(entry, ctk.CTkEntry):
                entry.delete(0, "end")
            elif isinstance(entry, ctk.CTkComboBox):
                entry.set("")
