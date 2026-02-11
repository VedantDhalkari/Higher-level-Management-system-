"""
Stock management module
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from config import Colors, AppConfig
from utils import Validators, Formatters

class StockManagement(ctk.CTkFrame):
    """Stock management interface"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = parent.db
        
        self.setup_ui()
        self.load_stock()
    
    def setup_ui(self):
        """Setup stock management UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Stock Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.grid(row=0, column=1, sticky="e")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            action_frame,
            text="Refresh",
            command=self.load_stock,
            width=100,
            height=35
        )
        refresh_btn.grid(row=0, column=0, padx=5)
        
        # Export button
        export_btn = ctk.CTkButton(
            action_frame,
            text="Export",
            command=self.export_stock,
            width=100,
            height=35,
            fg_color=Colors.SECONDARY
        )
        export_btn.grid(row=0, column=1, padx=5)
        
        # Low stock filter
        self.low_stock_var = ctk.BooleanVar(value=False)
        low_stock_check = ctk.CTkCheckBox(
            action_frame,
            text="Show Low Stock Only",
            variable=self.low_stock_var,
            command=self.load_stock
        )
        low_stock_check.grid(row=0, column=2, padx=20)
        
        # Search frame
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        search_label = ctk.CTkLabel(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=(0, 10))
        
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', lambda *args: self.load_stock())
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by SKU, Name, Category, Material...",
            textvariable=self.search_var
        )
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        clear_btn = ctk.CTkButton(
            search_frame,
            text="Clear",
            command=lambda: self.search_var.set(""),
            width=80
        )
        clear_btn.grid(row=0, column=2)
        
        # Stock table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        self.tree_scroll_y = ctk.CTkScrollbar(table_frame)
        self.tree_scroll_y.grid(row=0, column=1, sticky="ns")
        
        self.tree_scroll_x = ctk.CTkScrollbar(table_frame, orientation="horizontal")
        self.tree_scroll_x.grid(row=1, column=0, sticky="ew")
        
        self.stock_tree = ttk.Treeview(
            table_frame,
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set,
            selectmode="extended",
            height=20
        )
        self.stock_tree.grid(row=0, column=0, sticky="nsew")
        
        self.tree_scroll_y.configure(command=self.stock_tree.yview)
        self.tree_scroll_x.configure(command=self.stock_tree.xview)
        
        # Define columns
        columns = (
            "ID", "SKU", "Name", "Category", "Material", "Color", "Size",
            "Quantity", "Purchase", "Selling", "Supplier", "Arrival Date"
        )
        self.stock_tree['columns'] = columns
        
        # Format columns
        self.stock_tree.column("#0", width=0, stretch=False)
        col_widths = [50, 100, 150, 100, 100, 80, 60, 80, 80, 80, 120, 120]
        for col, width in zip(columns, col_widths):
            self.stock_tree.column(col, width=width, minwidth=50)
        
        # Create headings
        self.stock_tree.heading("#0", text="", anchor="w")
        for col in columns:
            self.stock_tree.heading(col, text=col, anchor="w")
        
        # Bind double-click for editing
        self.stock_tree.bind('<Double-1>', self.on_item_double_click)
        
        # Action buttons frame
        action_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_btn_frame.grid(row=3, column=0, sticky="ew", pady=10)
        action_btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Edit button
        edit_btn = ctk.CTkButton(
            action_btn_frame,
            text="Edit Selected",
            command=self.edit_selected,
            width=120,
            fg_color=Colors.PRIMARY
        )
        edit_btn.grid(row=0, column=0, padx=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            action_btn_frame,
            text="Delete Selected",
            command=self.delete_selected,
            width=120,
            fg_color=Colors.DANGER,
            hover_color="#bd2130"
        )
        delete_btn.grid(row=0, column=1, padx=5)
        
        # Update stock button
        update_stock_btn = ctk.CTkButton(
            action_btn_frame,
            text="Update Stock Qty",
            command=self.update_stock_qty,
            width=120,
            fg_color=Colors.SUCCESS,
            hover_color="#218838"
        )
        update_stock_btn.grid(row=0, column=2, padx=5)
    
    def load_stock(self):
        """Load stock items into treeview"""
        # Clear existing items
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        # Build query based on filters
        query = '''
            SELECT * FROM stock WHERE is_active = 1
        '''
        params = []
        
        # Apply low stock filter
        if self.low_stock_var.get():
            query += ' AND quantity <= min_stock_level'
        
        # Apply search filter
        search_term = self.search_var.get().strip()
        if search_term:
            query += ' AND (sku LIKE ? OR name LIKE ? OR category LIKE ? OR material LIKE ?)'
            search_pattern = f'%{search_term}%'
            params = [search_pattern, search_pattern, search_pattern, search_pattern]
        
        query += ' ORDER BY name'
        
        # Execute query
        items = self.db.execute_query(query, params, fetch_all=True)
        
        # Add to treeview
        for item in items:
            item = dict(item)
            
            # Format prices
            purchase_price = Formatters.format_currency(item['purchase_price'])
            selling_price = Formatters.format_currency(item['selling_price'])
            
            # Format date
            arrival_date = Formatters.format_date(item['arrival_date'])
            
            # Add row
            values = (
                item['id'],
                item['sku'],
                item['name'],
                item['category'],
                item['material'] or "",
                item['color'] or "",
                item['size'] or "",
                item['quantity'],
                purchase_price,
                selling_price,
                item['supplier_name'] or "",
                arrival_date
            )
            
            item_id = self.stock_tree.insert("", "end", values=values)
            
            # Highlight low stock items
            if item['quantity'] <= item['min_stock_level']:
                self.stock_tree.item(item_id, tags=('low_stock',))
                self.stock_tree.tag_configure('low_stock', background='#fff3cd')
    
    def on_item_double_click(self, event):
        """Handle double-click on item"""
        self.edit_selected()
    
    def edit_selected(self):
        """Edit selected item"""
        selection = self.stock_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit!")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one item to edit!")
            return
        
        item = self.stock_tree.item(selection[0])
        item_id = item['values'][0]
        
        # Open edit dialog
        self.open_edit_dialog(item_id)
    
    def open_edit_dialog(self, item_id):
        """Open edit dialog for item"""
        # Get item details
        query = "SELECT * FROM stock WHERE id = ?"
        item = self.db.execute_query(query, (item_id,), fetch_one=True)
        
        if not item:
            messagebox.showerror("Error", "Item not found!")
            return
        
        item = dict(item)
        
        # Create edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Stock Item")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        self.center_window(dialog)
        
        # Create form
        form_frame = ctk.CTkFrame(dialog)
        form_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Form fields
        fields = [
            ("SKU", "sku", item['sku']),
            ("Name", "name", item['name']),
            ("Category", "category", item['category']),
            ("Material", "material", item['material'] or ""),
            ("Color", "color", item['color'] or ""),
            ("Size", "size", item['size'] or ""),
            ("Quantity", "quantity", str(item['quantity'])),
            ("Min Stock Level", "min_stock_level", str(item['min_stock_level'])),
            ("Purchase Price", "purchase_price", str(item['purchase_price'])),
            ("Selling Price", "selling_price", str(item['selling_price'])),
            ("Supplier Name", "supplier_name", item['supplier_name'] or ""),
        ]
        
        self.edit_vars = {}
        
        for i, (label, field, value) in enumerate(fields):
            # Label
            ctk_label = ctk.CTkLabel(form_frame, text=f"{label}:")
            ctk_label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            
            # Entry
            var = ctk.StringVar(value=value)
            self.edit_vars[field] = var
            
            entry = ctk.CTkEntry(form_frame, textvariable=var)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
        
        # Configure grid
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Button frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        # Save button
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Changes",
            command=lambda: self.save_edit(item_id, dialog),
            width=120,
            fg_color=Colors.SUCCESS
        )
        save_btn.grid(row=0, column=0, padx=10)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=120,
            fg_color=Colors.DANGER
        )
        cancel_btn.grid(row=0, column=1, padx=10)
    
    def save_edit(self, item_id, dialog):
        """Save edited item"""
        try:
            # Validate inputs
            quantity = int(self.edit_vars['quantity'].get())
            min_stock = int(self.edit_vars['min_stock_level'].get())
            purchase_price = float(self.edit_vars['purchase_price'].get())
            selling_price = float(self.edit_vars['selling_price'].get())
            
            if quantity < 0 or min_stock < 0:
                messagebox.showwarning("Warning", "Quantity and min stock cannot be negative!")
                return
            
            if purchase_price < 0 or selling_price < 0:
                messagebox.showwarning("Warning", "Prices cannot be negative!")
                return
            
            if selling_price < purchase_price:
                messagebox.showwarning("Warning", "Selling price cannot be less than purchase price!")
                return
            
            # Update database
            update_query = '''
                UPDATE stock SET
                    sku = ?,
                    name = ?,
                    category = ?,
                    material = ?,
                    color = ?,
                    size = ?,
                    quantity = ?,
                    min_stock_level = ?,
                    purchase_price = ?,
                    selling_price = ?,
                    supplier_name = ?,
                    last_updated = ?
                WHERE id = ?
            '''
            
            self.db.execute_query(
                update_query,
                (
                    self.edit_vars['sku'].get(),
                    self.edit_vars['name'].get(),
                    self.edit_vars['category'].get(),
                    self.edit_vars['material'].get() or None,
                    self.edit_vars['color'].get() or None,
                    self.edit_vars['size'].get() or None,
                    quantity,
                    min_stock,
                    purchase_price,
                    selling_price,
                    self.edit_vars['supplier_name'].get() or None,
                    datetime.now().isoformat(),
                    item_id
                )
            )
            
            messagebox.showinfo("Success", "Item updated successfully!")
            dialog.destroy()
            self.load_stock()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def delete_selected(self):
        """Delete selected items"""
        selection = self.stock_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select items to delete!")
            return
        
        if not messagebox.askyesno("Confirm", f"Delete {len(selection)} selected item(s)?"):
            return
        
        for item in selection:
            item_data = self.stock_tree.item(item)
            item_id = item_data['values'][0]
            
            # Soft delete (mark as inactive)
            self.db.execute_query(
                "UPDATE stock SET is_active = 0 WHERE id = ?",
                (item_id,)
            )
        
        messagebox.showinfo("Success", f"{len(selection)} item(s) deleted!")
        self.load_stock()
    
    def update_stock_qty(self):
        """Update stock quantity for selected item"""
        selection = self.stock_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to update!")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one item to update!")
            return
        
        item = self.stock_tree.item(selection[0])
        item_id = item['values'][0]
        current_qty = item['values'][7]
        
        # Create update dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Update Stock Quantity")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        self.center_window(dialog)
        
        # Dialog content
        content = ctk.CTkFrame(dialog)
        content.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Current quantity
        current_label = ctk.CTkLabel(
            content,
            text=f"Current Quantity: {current_qty}",
            font=ctk.CTkFont(weight="bold")
        )
        current_label.pack(pady=(0, 20))
        
        # New quantity frame
        qty_frame = ctk.CTkFrame(content, fg_color="transparent")
        qty_frame.pack(fill="x", pady=(0, 20))
        
        qty_label = ctk.CTkLabel(qty_frame, text="New Quantity:")
        qty_label.grid(row=0, column=0, padx=(0, 10))
        
        self.new_qty_var = ctk.StringVar(value=str(current_qty))
        qty_entry = ctk.CTkEntry(qty_frame, textvariable=self.new_qty_var)
        qty_entry.grid(row=0, column=1, sticky="ew")
        qty_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack()
        
        update_btn = ctk.CTkButton(
            btn_frame,
            text="Update",
            command=lambda: self.save_qty_update(item_id, dialog),
            width=100,
            fg_color=Colors.SUCCESS
        )
        update_btn.grid(row=0, column=0, padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=100,
            fg_color=Colors.DANGER
        )
        cancel_btn.grid(row=0, column=1, padx=10)
    
    def save_qty_update(self, item_id, dialog):
        """Save quantity update"""
        try:
            new_qty = int(self.new_qty_var.get())
            if new_qty < 0:
                messagebox.showwarning("Warning", "Quantity cannot be negative!")
                return
            
            # Update database
            self.db.execute_query(
                "UPDATE stock SET quantity = ?, last_updated = ? WHERE id = ?",
                (new_qty, datetime.now().isoformat(), item_id)
            )
            
            messagebox.showinfo("Success", "Quantity updated successfully!")
            dialog.destroy()
            self.load_stock()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
    
    def export_stock(self):
        """Export stock to CSV (placeholder)"""
        messagebox.showinfo("Export", "Stock export feature will be available soon!")
    
    def center_window(self, window):
        """Center a window on screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')