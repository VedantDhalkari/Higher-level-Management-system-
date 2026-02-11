"""
New stock entry module
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import random
import string
from config import Colors, AppConfig
from utils import Validators

class NewStockEntry(ctk.CTkFrame):
    """New stock entry form"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = parent.db
        
        self.setup_ui()
        self.generate_sku()
    
    def setup_ui(self):
        """Setup new stock entry UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main container
        container = ctk.CTkScrollableFrame(self)
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        container.grid_columnconfigure((0, 1), weight=1, uniform="col")
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="New Stock Entry",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Colors.PRIMARY
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Form fields
        self.fields = {}
        row = 1
        
        # SKU (auto-generated)
        sku_frame = ctk.CTkFrame(container, fg_color="transparent")
        sku_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        sku_frame.grid_columnconfigure(1, weight=1)
        
        sku_label = ctk.CTkLabel(sku_frame, text="SKU:", font=ctk.CTkFont(weight="bold"))
        sku_label.grid(row=0, column=0, padx=(0, 10))
        
        self.sku_var = ctk.StringVar()
        sku_entry = ctk.CTkEntry(
            sku_frame,
            textvariable=self.sku_var,
            state="readonly",
            fg_color="#e9ecef",
            text_color="black"
        )
        sku_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        regen_btn = ctk.CTkButton(
            sku_frame,
            text="Regenerate",
            command=self.generate_sku,
            width=100
        )
        regen_btn.grid(row=0, column=2)
        row += 1
        
        # Define form fields
        field_definitions = [
            ("Name *", "name", ""),
            ("Category *", "category", ""),
            ("Material", "material", ""),
            ("Color", "color", ""),
            ("Size", "size", ""),
            ("Quantity *", "quantity", "0"),
            ("Min Stock Level", "min_stock_level", "5"),
            ("Purchase Price *", "purchase_price", ""),
            ("Selling Price *", "selling_price", ""),
            ("Supplier Name", "supplier_name", ""),
            ("Supplier Contact", "supplier_contact", "")
        ]
        
        # Create form fields
        for label, field, default in field_definitions:
            # Label
            ctk_label = ctk.CTkLabel(
                container,
                text=label,
                anchor="w"
            )
            ctk_label.grid(row=row, column=0, padx=(20, 10), pady=5, sticky="w")
            
            # Entry field
            var = ctk.StringVar(value=default)
            self.fields[field] = var
            
            entry = ctk.CTkEntry(
                container,
                textvariable=var,
                placeholder_text=f"Enter {label.lower()}"
            )
            entry.grid(row=row, column=1, padx=(10, 20), pady=5, sticky="ew")
            
            row += 1
        
        # Category dropdown
        category_label = ctk.CTkLabel(
            container,
            text="Select Category:",
            anchor="w"
        )
        category_label.grid(row=field_definitions.index(("Category *", "category", "")) + 1, 
                          column=0, padx=(20, 10), pady=5, sticky="w")
        
        self.category_var = ctk.StringVar()
        categories = ["Saree", "Lehenga", "Salwar Suit", "Kurti", "Dress", "Accessories", "Other"]
        category_dropdown = ctk.CTkOptionMenu(
            container,
            variable=self.category_var,
            values=categories,
            command=lambda cat: self.fields['category'].set(cat)
        )
        category_dropdown.grid(row=field_definitions.index(("Category *", "category", "")) + 1, 
                             column=1, padx=(10, 20), pady=5, sticky="ew")
        self.fields['category'].set(categories[0])
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=30)
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear Form",
            command=self.clear_form,
            width=150,
            height=45,
            fg_color=Colors.DANGER,
            hover_color="#bd2130"
        )
        clear_btn.grid(row=0, column=0, padx=20)
        
        # Save button
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Stock Item",
            command=self.save_stock,
            width=150,
            height=45,
            fg_color=Colors.SUCCESS,
            hover_color="#218838"
        )
        save_btn.grid(row=0, column=1, padx=20)
    
    def generate_sku(self):
        """Generate unique SKU"""
        date_part = datetime.now().strftime("%y%m%d")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        sku = f"SKU-{date_part}-{random_part}"
        self.sku_var.set(sku)
    
    def clear_form(self):
        """Clear all form fields"""
        if messagebox.askyesno("Confirm", "Clear all form fields?"):
            for field, var in self.fields.items():
                if field == 'quantity':
                    var.set("0")
                elif field == 'min_stock_level':
                    var.set("5")
                else:
                    var.set("")
            self.generate_sku()
    
    def save_stock(self):
        """Save new stock item"""
        # Validate required fields
        required_fields = ['name', 'category', 'purchase_price', 'selling_price']
        for field in required_fields:
            if not self.fields[field].get().strip():
                messagebox.showwarning("Warning", f"Please fill in {field.replace('_', ' ')}!")
                return
        
        # Validate numeric fields
        try:
            quantity = int(self.fields['quantity'].get())
            min_stock_level = int(self.fields['min_stock_level'].get() or "5")
            purchase_price = float(self.fields['purchase_price'].get())
            selling_price = float(self.fields['selling_price'].get())
            
            if quantity < 0 or min_stock_level < 0:
                messagebox.showwarning("Warning", "Quantity and min stock cannot be negative!")
                return
            
            if purchase_price < 0 or selling_price < 0:
                messagebox.showwarning("Warning", "Prices cannot be negative!")
                return
            
            if selling_price < purchase_price:
                messagebox.showwarning("Warning", "Selling price cannot be less than purchase price!")
                return
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for quantity and prices!")
            return
        
        # Validate supplier contact if provided
        supplier_contact = self.fields['supplier_contact'].get().strip()
        if supplier_contact and not Validators.validate_phone(supplier_contact):
            if '@' not in supplier_contact:  # Not an email
                messagebox.showwarning("Warning", "Please enter a valid phone number or email!")
                return
        
        # Save to database
        insert_query = '''
            INSERT INTO stock (
                sku, name, category, material, color, size,
                quantity, min_stock_level, purchase_price, selling_price,
                supplier_name, supplier_contact, arrival_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        try:
            self.db.execute_query(
                insert_query,
                (
                    self.sku_var.get(),
                    self.fields['name'].get().strip(),
                    self.fields['category'].get().strip(),
                    self.fields['material'].get().strip() or None,
                    self.fields['color'].get().strip() or None,
                    self.fields['size'].get().strip() or None,
                    quantity,
                    min_stock_level,
                    purchase_price,
                    selling_price,
                    self.fields['supplier_name'].get().strip() or None,
                    supplier_contact or None,
                    datetime.now().isoformat()
                )
            )
            
            messagebox.showinfo(
                "Success!",
                f"Stock item saved successfully!\n"
                f"SKU: {self.sku_var.get()}\n"
                f"Name: {self.fields['name'].get()}"
            )
            
            # Clear form for next entry
            self.clear_form()
            
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Error", "SKU already exists! Please regenerate SKU.")
                self.generate_sku()
            else:
                messagebox.showerror("Error", f"Failed to save stock item: {str(e)}")