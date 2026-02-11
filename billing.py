"""
Billing and invoice generation module
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from config import Colors, AppConfig
from utils import InvoiceGenerator, Validators, Formatters
from auth import PinDialog

class BillingSystem(ctk.CTkFrame):
    """Billing system with cart and invoice generation"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_LIGHT)
        self.parent = parent
        self.db = parent.db
        
        # Cart items
        self.cart_items = []
        
        # Customer info
        self.customer_info = {
            "name": "",
            "phone": "",
            "email": ""
        }
        
        self.setup_ui()
        self.load_stock_items()
    
    def setup_ui(self):
        """Setup billing UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - Product selection
        left_panel = ctk.CTkFrame(self, fg_color=Colors.CARD_BG, corner_radius=15,
                                 border_width=1, border_color=Colors.BORDER_LIGHT)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)
        
        # Search frame
        search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Search label
        search_label = ctk.CTkLabel(
            search_frame,
            text="Quick Search:",
            font=ctk.CTkFont(weight="bold")
        )
        search_label.grid(row=0, column=0, padx=(0, 10))
        
        # Search entry
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by SKU, Name, Category...",
            textvariable=self.search_var
        )
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Clear button
        clear_btn = ctk.CTkButton(
            search_frame,
            text="Clear",
            command=self.clear_search,
            width=80
        )
        clear_btn.grid(row=0, column=2)
        
        # Stock items treeview
        tree_frame = ctk.CTkFrame(left_panel)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview with scrollbar
        self.tree_scroll = ctk.CTkScrollbar(tree_frame)
        self.tree_scroll.grid(row=0, column=1, sticky="ns")
        
        self.stock_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=self.tree_scroll.set,
            selectmode="browse",
            height=15
        )
        self.stock_tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scroll.configure(command=self.stock_tree.yview)
        
        # Define columns
        columns = ("ID", "SKU", "Name", "Category", "Material", "Color", "Qty", "Price")
        self.stock_tree['columns'] = columns
        
        # Format columns
        self.stock_tree.column("#0", width=0, stretch=False)
        for col in columns:
            self.stock_tree.column(col, width=100, minwidth=50)
        
        # Create headings
        self.stock_tree.heading("#0", text="", anchor="w")
        for col in columns:
            self.stock_tree.heading(col, text=col, anchor="w")
        
        # Bind selection
        self.stock_tree.bind('<<TreeviewSelect>>', self.on_item_selected)
        
        # Right panel - Cart and billing
        right_panel = ctk.CTkFrame(self, fg_color=Colors.CARD_BG, corner_radius=15,
                                  border_width=1, border_color=Colors.BORDER_LIGHT)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        # Customer info frame
        customer_frame = ctk.CTkFrame(right_panel)
        customer_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        customer_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Customer info title
        customer_title = ctk.CTkLabel(
            customer_frame,
            text="Customer Information",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        customer_title.grid(row=0, column=0, columnspan=2, pady=(10, 5))
        
        # Customer name
        name_label = ctk.CTkLabel(customer_frame, text="Name:")
        name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.customer_name_var = ctk.StringVar()
        name_entry = ctk.CTkEntry(
            customer_frame,
            textvariable=self.customer_name_var,
            placeholder_text="Walk-in Customer"
        )
        name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Customer phone
        phone_label = ctk.CTkLabel(customer_frame, text="Phone:")
        phone_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.customer_phone_var = ctk.StringVar()
        phone_entry = ctk.CTkEntry(
            customer_frame,
            textvariable=self.customer_phone_var,
            placeholder_text="Optional"
        )
        phone_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # Cart frame
        cart_frame = ctk.CTkFrame(right_panel)
        cart_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        cart_frame.grid_columnconfigure(0, weight=1)
        cart_frame.grid_rowconfigure(0, weight=1)
        
        # Cart title
        cart_title = ctk.CTkLabel(
            cart_frame,
            text="Cart Items",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        cart_title.grid(row=0, column=0, pady=(10, 5))
        
        # Cart items display
        self.cart_text = ctk.CTkTextbox(cart_frame, height=150)
        self.cart_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.cart_text.insert("1.0", "No items in cart")
        self.cart_text.configure(state="disabled")
        
        # Quantity frame
        qty_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        qty_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        qty_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        qty_label = ctk.CTkLabel(qty_frame, text="Quantity:")
        qty_label.grid(row=0, column=0, padx=5, sticky="e")
        
        self.qty_var = ctk.StringVar(value="1")
        qty_entry = ctk.CTkEntry(
            qty_frame,
            textvariable=self.qty_var,
            width=80,
            justify="center"
        )
        qty_entry.grid(row=0, column=1, padx=5)
        
        add_btn = ctk.CTkButton(
            qty_frame,
            text="Add to Cart",
            command=self.add_to_cart,
            fg_color=Colors.PRIMARY,
            width=100
        )
        add_btn.grid(row=0, column=2, padx=5)
        
        # Totals frame
        totals_frame = ctk.CTkFrame(right_panel)
        totals_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        totals_frame.grid_columnconfigure(1, weight=1)
        
        # Subtotal
        subtotal_label = ctk.CTkLabel(
            totals_frame,
            text="Subtotal:",
            font=ctk.CTkFont(weight="bold")
        )
        subtotal_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.subtotal_var = ctk.StringVar(value="₹0.00")
        subtotal_value = ctk.CTkLabel(
            totals_frame,
            textvariable=self.subtotal_var,
            font=ctk.CTkFont(weight="bold")
        )
        subtotal_value.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        
        # Discount
        discount_label = ctk.CTkLabel(totals_frame, text="Discount:")
        discount_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        discount_frame = ctk.CTkFrame(totals_frame, fg_color="transparent")
        discount_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        discount_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.discount_var = ctk.StringVar(value="0")
        discount_entry = ctk.CTkEntry(
            discount_frame,
            textvariable=self.discount_var,
            width=80,
            justify="center"
        )
        discount_entry.grid(row=0, column=0, padx=(0, 5))
        
        discount_type_label = ctk.CTkLabel(discount_frame, text="₹")
        discount_type_label.grid(row=0, column=1, sticky="w")
        
        # GST
        gst_label = ctk.CTkLabel(totals_frame, text=f"GST ({AppConfig.GST_RATE}%):")
        gst_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.gst_var = ctk.StringVar(value="₹0.00")
        gst_value = ctk.CTkLabel(
            totals_frame,
            textvariable=self.gst_var,
            font=ctk.CTkFont(weight="bold")
        )
        gst_value.grid(row=2, column=1, padx=10, pady=5, sticky="e")
        
        # Total
        total_label = ctk.CTkLabel(
            totals_frame,
            text="Total:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        total_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.total_var = ctk.StringVar(value="₹0.00")
        total_value = ctk.CTkLabel(
            totals_frame,
            textvariable=self.total_var,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Colors.SECONDARY
        )
        total_value.grid(row=3, column=1, padx=10, pady=10, sticky="e")
        
        # Action buttons
        button_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        button_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear Cart",
            command=self.clear_cart,
            fg_color=Colors.DANGER,
            hover_color="#bd2130"
        )
        clear_btn.grid(row=0, column=0, padx=5)
        
        generate_btn = ctk.CTkButton(
            button_frame,
            text="Generate Bill",
            command=self.generate_bill,
            fg_color=Colors.SUCCESS,
            hover_color="#218838"
        )
        generate_btn.grid(row=0, column=1, padx=5)
    
    def load_stock_items(self):
        """Load stock items into treeview"""
        # Clear existing items
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        # Get stock items
        query = '''
            SELECT id, sku, name, category, material, color, quantity, selling_price
            FROM stock 
            WHERE is_active = 1 AND quantity > 0
            ORDER BY name
        '''
        items = self.db.execute_query(query, fetch_all=True)
        
        # Add to treeview
        for item in items:
            self.stock_tree.insert(
                "", "end",
                values=(
                    item['id'],
                    item['sku'],
                    item['name'],
                    item['category'],
                    item['material'] or "",
                    item['color'] or "",
                    item['quantity'],
                    Formatters.format_currency(item['selling_price'])
                )
            )
    
    def on_search_changed(self, *args):
        """Handle search input change"""
        search_term = self.search_var.get().lower()
        
        # Show all items if search is empty
        if not search_term:
            for item in self.stock_tree.get_children():
                self.stock_tree.item(item, tags=())
            return
        
        # Filter items
        for item in self.stock_tree.get_children():
            values = self.stock_tree.item(item)['values']
            item_text = ' '.join(str(v).lower() for v in values)
            
            if search_term in item_text:
                self.stock_tree.item(item, tags=('match',))
                self.stock_tree.tag_configure('match', background='lightyellow')
            else:
                self.stock_tree.item(item, tags=())
    
    def clear_search(self):
        """Clear search field"""
        self.search_var.set("")
    
    def on_item_selected(self, event):
        """Handle item selection from treeview"""
        selection = self.stock_tree.selection()
        if selection:
            item = self.stock_tree.item(selection[0])
            self.selected_item = item['values']
            
            # Auto-set quantity to 1
            self.qty_var.set("1")
    
    def add_to_cart(self):
        """Add selected item to cart"""
        if not hasattr(self, 'selected_item'):
            messagebox.showwarning("Warning", "Please select an item first!")
            return
        
        try:
            quantity = int(self.qty_var.get())
            if quantity <= 0:
                messagebox.showwarning("Warning", "Quantity must be greater than 0!")
                return
            
            # Get item details
            item_id = self.selected_item[0]
            sku = self.selected_item[1]
            name = self.selected_item[2]
            category = self.selected_item[3]
            material = self.selected_item[4]
            color = self.selected_item[5]
            stock_qty = int(self.selected_item[6])
            price_str = self.selected_item[7].replace('₹', '').replace(',', '')
            price = float(price_str)
            
            # Check stock availability
            if quantity > stock_qty:
                messagebox.showwarning("Warning", f"Only {stock_qty} items available in stock!")
                return
            
            # Check if item already in cart
            for i, cart_item in enumerate(self.cart_items):
                if cart_item['id'] == item_id:
                    # Update quantity
                    new_qty = cart_item['quantity'] + quantity
                    if new_qty > stock_qty:
                        messagebox.showwarning("Warning", f"Only {stock_qty} items available in stock!")
                        return
                    
                    self.cart_items[i]['quantity'] = new_qty
                    self.cart_items[i]['total'] = new_qty * price
                    self.update_cart_display()
                    self.calculate_totals()
                    return
            
            # Add new item to cart
            cart_item = {
                'id': item_id,
                'sku': sku,
                'name': name,
                'category': category,
                'material': material,
                'color': color,
                'price': price,
                'quantity': quantity,
                'total': price * quantity
            }
            
            self.cart_items.append(cart_item)
            self.update_cart_display()
            self.calculate_totals()
            
            # Reset quantity
            self.qty_var.set("1")
            
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid quantity!")
    
    def update_cart_display(self):
        """Update cart display"""
        self.cart_text.configure(state="normal")
        self.cart_text.delete("1.0", "end")
        
        if not self.cart_items:
            self.cart_text.insert("1.0", "No items in cart")
        else:
            cart_text = ""
            for item in self.cart_items:
                cart_text += f"{item['quantity']} x {item['name']} ({item['sku']}) = ₹{item['total']:.2f}\n"
            self.cart_text.insert("1.0", cart_text)
        
        self.cart_text.configure(state="disabled")
    
    def calculate_totals(self):
        """Calculate subtotal, GST, and total"""
        subtotal = sum(item['total'] for item in self.cart_items)
        
        try:
            discount = float(self.discount_var.get() or 0)
        except ValueError:
            discount = 0
            self.discount_var.set("0")
        
        if discount > subtotal:
            discount = subtotal
            self.discount_var.set(str(discount))
        
        taxable = subtotal - discount
        gst_amount = taxable * (AppConfig.GST_RATE / 100)
        total = taxable + gst_amount
        
        # Update display
        self.subtotal_var.set(Formatters.format_currency(subtotal))
        self.gst_var.set(Formatters.format_currency(gst_amount))
        self.total_var.set(Formatters.format_currency(total))
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items:
            if messagebox.askyesno("Confirm", "Clear all items from cart?"):
                self.cart_items = []
                self.update_cart_display()
                self.calculate_totals()
    
    def generate_bill(self):
        """Generate invoice and save sale"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        
        # Verify billing PIN for stock management access
        pin_dialog = PinDialog(self.parent, "Enter Billing PIN", 
                             self.parent.auth.verify_billing_pin)
        if not pin_dialog.show():
            messagebox.showwarning("Warning", "PIN verification failed!")
            return
        
        # Get customer info
        customer_name = self.customer_name_var.get().strip() or "Walk-in Customer"
        customer_phone = self.customer_phone_var.get().strip() or None
        
        # Validate customer phone
        if customer_phone and not Validators.validate_phone(customer_phone):
            messagebox.showwarning("Warning", "Please enter a valid 10-digit phone number!")
            return
        
        # Calculate totals
        subtotal = sum(item['total'] for item in self.cart_items)
        try:
            discount = float(self.discount_var.get() or 0)
        except ValueError:
            discount = 0
        
        taxable = subtotal - discount
        gst_amount = taxable * (AppConfig.GST_RATE / 100)
        total = taxable + gst_amount
        
        # Generate invoice number
        invoice_number = InvoiceGenerator.generate_invoice_number()
        
        # Prepare sale data
        sale_data = {
            'invoice_number': invoice_number,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'items': json.dumps(self.cart_items),
            'subtotal': subtotal,
            'discount': discount,
            'gst_amount': gst_amount,
            'total_amount': total,
            'payment_method': 'Cash',
            'payment_status': 'Completed',
            'sold_by': self.parent.auth.current_user['username'],
            'created_at': datetime.now().isoformat()
        }
        
        # Check if customer exists
        customer_id = None
        if customer_phone:
            query = "SELECT id FROM customers WHERE phone = ?"
            existing_customer = self.db.execute_query(query, (customer_phone,), fetch_one=True)
            if existing_customer:
                customer_id = existing_customer['id']
                # Update customer stats
                update_query = '''
                    UPDATE customers 
                    SET total_purchases = total_purchases + ?, 
                        last_purchase_date = ?
                    WHERE id = ?
                '''
                self.db.execute_query(update_query, (total, datetime.now(), customer_id))
            else:
                # Create new customer
                insert_query = '''
                    INSERT INTO customers (name, phone, total_purchases, last_purchase_date)
                    VALUES (?, ?, ?, ?)
                '''
                customer_id = self.db.execute_query(
                    insert_query,
                    (customer_name, customer_phone, total, datetime.now())
                )
        
        # Save sale to database
        sale_query = '''
            INSERT INTO sales (
                invoice_number, customer_id, customer_name, customer_phone,
                items, subtotal, discount, gst_amount, total_amount,
                payment_method, payment_status, sold_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        self.db.execute_query(
            sale_query,
            (
                invoice_number,
                customer_id,
                customer_name,
                customer_phone,
                json.dumps(self.cart_items),
                subtotal,
                discount,
                gst_amount,
                total,
                'Cash',
                'Completed',
                self.parent.auth.current_user['username'],
                datetime.now().isoformat()
            )
        )
        
        # Update stock quantities
        for item in self.cart_items:
            update_stock_query = '''
                UPDATE stock 
                SET quantity = quantity - ?, 
                    last_updated = ?
                WHERE id = ?
            '''
            self.db.execute_query(
                update_stock_query,
                (item['quantity'], datetime.now().isoformat(), item['id'])
            )
        
        # Generate invoice
        customer_info = {
            'name': customer_name,
            'phone': customer_phone or ''
        }
        
        try:
            invoice_path = InvoiceGenerator.generate_invoice(
                sale_data, customer_info, self.cart_items
            )
            
            # Show success message
            messagebox.showinfo(
                "Success!",
                f"Bill generated successfully!\n"
                f"Invoice: {invoice_number}\n"
                f"Total: ₹{total:.2f}\n\n"
                f"Invoice saved to:\n{invoice_path}"
            )
            
            # Reset form
            self.clear_cart()
            self.customer_name_var.set("")
            self.customer_phone_var.set("")
            self.discount_var.set("0")
            self.load_stock_items()  # Refresh stock
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate invoice: {str(e)}")