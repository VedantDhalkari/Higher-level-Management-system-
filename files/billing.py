"""
Billing Module
Invoice creation, cart management, and checkout with premium light theme
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
import config
from ui_components import AnimatedButton


class BillingModule(ctk.CTkFrame):
    """Billing and invoice creation interface"""
    
    def __init__(self, parent, db_manager, invoice_generator, current_user, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        self.invoice_gen = invoice_generator
        self.current_user = current_user
        self.cart = []
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="New Bill / Invoice",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_1, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=(0, config.SPACING_LG), anchor="w")
        
        # Main layout
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # Left panel - Search & Items
        left_panel = ctk.CTkFrame(
            main_container,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, config.SPACING_SM))
        
        # Search section
        search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search Items (SKU / Name / Color)",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        search_label.pack(anchor="w", pady=(0, config.SPACING_SM))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            height=config.INPUT_HEIGHT,
            placeholder_text="Type to search...",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            border_color=config.COLOR_BORDER,
            border_width=2
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Items display
        self.items_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent",
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        self.items_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, 
                             pady=(0, config.SPACING_LG))
        
        # Right panel - Cart
        right_panel = ctk.CTkFrame(
            main_container,
            width=450,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)
        
        # Cart title
        cart_title = ctk.CTkLabel(
            right_panel,
            text="🛒 Cart Items",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        cart_title.pack(pady=config.SPACING_LG, padx=config.SPACING_LG, anchor="w")
        
        # Cart items
        self.cart_items_frame = ctk.CTkScrollableFrame(
            right_panel,
            fg_color="transparent",
            height=250,
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        self.cart_items_frame.pack(fill="x", padx=config.SPACING_LG, pady=(0, config.SPACING_SM))
        
        # Customer details
        customer_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        customer_frame.pack(fill="x", padx=config.SPACING_LG, pady=config.SPACING_SM)
        
        ctk.CTkLabel(
            customer_frame,
            text="Customer Name (Optional):",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, config.SPACING_XS))
        
        self.customer_name_entry = ctk.CTkEntry(
            customer_frame,
            height=35,
            border_color=config.COLOR_BORDER,
            border_width=1
        )
        self.customer_name_entry.pack(fill="x", pady=(0, config.SPACING_SM))
        
        ctk.CTkLabel(
            customer_frame,
            text="Phone (Optional):",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, config.SPACING_XS))
        
        self.customer_phone_entry = ctk.CTkEntry(
            customer_frame,
            height=35,
            border_color=config.COLOR_BORDER,
            border_width=1
        )
        self.customer_phone_entry.pack(fill="x", pady=(0, config.SPACING_SM))
        
        ctk.CTkLabel(
            customer_frame,
            text="Discount %:",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, config.SPACING_XS))
        
        self.discount_entry = ctk.CTkEntry(
            customer_frame,
            height=35,
            placeholder_text="0",
            border_color=config.COLOR_BORDER,
            border_width=1
        )
        self.discount_entry.pack(fill="x")
        self.discount_entry.bind("<KeyRelease>", lambda e: self._update_summary())
        
        # Summary
        summary_frame = ctk.CTkFrame(
            right_panel,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_PRIMARY
        )
        summary_frame.pack(fill="x", padx=config.SPACING_LG, pady=config.SPACING_MD)
        
        self.subtotal_label = ctk.CTkLabel(
            summary_frame,
            text="Subtotal: ₹0.00",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        self.subtotal_label.pack(pady=(config.SPACING_SM, 2), padx=config.SPACING_MD, anchor="w")
        
        self.discount_label = ctk.CTkLabel(
            summary_frame,
            text="Discount: ₹0.00",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        self.discount_label.pack(pady=2, padx=config.SPACING_MD, anchor="w")
        
        self.gst_label = ctk.CTkLabel(
            summary_frame,
            text=f"GST ({config.GST_RATE}%): ₹0.00",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        self.gst_label.pack(pady=2, padx=config.SPACING_MD, anchor="w")
        
        self.total_label = ctk.CTkLabel(
            summary_frame,
            text="Total: ₹0.00",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        self.total_label.pack(pady=(config.SPACING_SM, config.SPACING_SM), padx=config.SPACING_MD, anchor="w")
        
        # Checkout button
        checkout_btn = AnimatedButton(
            right_panel,
            text="💳 Complete Sale & Generate Invoice",
            height=config.BUTTON_HEIGHT_LG,
            fg_color=config.COLOR_SUCCESS,
            hover_color="#059669",
            text_color=config.COLOR_TEXT_WHITE,
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            command=self._complete_sale
        )
        checkout_btn.pack(side="bottom", fill="x", padx=config.SPACING_LG, pady=config.SPACING_LG)
    
    def _on_search(self, event=None):
        """Handle search"""
        query = self.search_entry.get().strip()
        
        # Clear items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        if len(query) < 2:
            return
        
        # Search database
        results = self.db.execute_query(
            """SELECT item_id, sku_code, saree_type, material, color, selling_price, quantity
               FROM inventory 
               WHERE (sku_code LIKE ? OR saree_type LIKE ? OR color LIKE ? OR material LIKE ?)
               AND quantity > 0
               LIMIT 20""",
            (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")
        )
        
        for item in results:
            self._create_item_card(item)
    
    def _create_item_card(self, item):
        """Create item card"""
        card = ctk.CTkFrame(
            self.items_frame,
            fg_color=config.COLOR_BG_HOVER,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        card.pack(fill="x", pady=config.SPACING_XS)
        
        # Item info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=config.SPACING_MD, pady=config.SPACING_SM)
        
        name = f"{item[2]} - {item[3]} ({item[4]})"
        name_label = ctk.CTkLabel(
            info_frame,
            text=name,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        name_label.pack(anchor="w")
        
        details = f"SKU: {item[1]} | Stock: {item[6]}"
        details_label = ctk.CTkLabel(
            info_frame,
            text=details,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL - 1),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        details_label.pack(anchor="w")
        
        price = f"₹{item[5]:,.2f}"
        price_label = ctk.CTkLabel(
            info_frame,
            text=price,
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        price_label.pack(anchor="w")
        
        # Add button
        add_btn = AnimatedButton(
            card,
            text="+ Add",
            width=80,
            height=32,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_LIGHT,
            command=lambda: self._add_to_cart(item)
        )
        add_btn.pack(side="right", padx=config.SPACING_MD, pady=config.SPACING_SM)
    
    def _add_to_cart(self, item):
        """Add item to cart"""
        # Check if already in cart
        for cart_item in self.cart:
            if cart_item['item_id'] == item[0]:
                if cart_item['quantity'] < item[6]:
                    cart_item['quantity'] += 1
                    cart_item['total'] = cart_item['quantity'] * cart_item['price']
                else:
                    messagebox.showwarning("Stock Limit", "Cannot add more than available quantity")
                    return
                break
        else:
            self.cart.append({
                'item_id': item[0],
                'sku': item[1],
                'name': f"{item[2]} - {item[3]} ({item[4]})",
                'price': item[5],
                'quantity': 1,
                'total': item[5],
                'available_qty': item[6]
            })
        
        self._refresh_cart()
    
    def _refresh_cart(self):
        """Refresh cart display"""
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        for idx, item in enumerate(self.cart):
            self._create_cart_item(idx, item)
        
        self._update_summary()
    
    def _create_cart_item(self, idx, item):
        """Create cart item widget"""
        item_frame = ctk.CTkFrame(
            self.cart_items_frame,
            fg_color=config.COLOR_BG_HOVER,
            corner_radius=config.RADIUS_SM,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        item_frame.pack(fill="x", pady=config.SPACING_XS)
        
        # Item info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=config.SPACING_SM, pady=config.SPACING_SM)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=item['name'],
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL - 1, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        name_label.pack(anchor="w")
        
        price_label = ctk.CTkLabel(
            info_frame,
            text=f"₹{item['price']} × {item['quantity']} = ₹{item['total']:,.2f}",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL - 1),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        price_label.pack(anchor="w")
        
        # Controls
        controls_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=config.SPACING_SM)
        
        ctk.CTkButton(
            controls_frame,
            text="-",
            width=25,
            height=25,
            fg_color=config.COLOR_TEXT_SECONDARY,
            command=lambda: self._decrease_qty(idx)
        ).pack(side="left", padx=1)
        
        ctk.CTkLabel(
            controls_frame,
            text=str(item['quantity']),
            width=30,
            text_color=config.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=config.SPACING_XS)
        
        ctk.CTkButton(
            controls_frame,
            text="+",
            width=25,
            height=25,
            fg_color=config.COLOR_SUCCESS,
            command=lambda: self._increase_qty(idx)
        ).pack(side="left", padx=1)
        
        ctk.CTkButton(
            controls_frame,
            text="✕",
            width=25,
            height=25,
            fg_color=config.COLOR_DANGER,
            command=lambda: self._remove_item(idx)
        ).pack(side="left", padx=(config.SPACING_SM, 0))
    
    def _decrease_qty(self, idx):
        if self.cart[idx]['quantity'] > 1:
            self.cart[idx]['quantity'] -= 1
            self.cart[idx]['total'] = self.cart[idx]['quantity'] * self.cart[idx]['price']
            self._refresh_cart()
    
    def _increase_qty(self, idx):
        if self.cart[idx]['quantity'] < self.cart[idx]['available_qty']:
            self.cart[idx]['quantity'] += 1
            self.cart[idx]['total'] = self.cart[idx]['quantity'] * self.cart[idx]['price']
            self._refresh_cart()
        else:
            messagebox.showwarning("Stock Limit", "Cannot exceed available quantity")
    
    def _remove_item(self, idx):
        self.cart.pop(idx)
        self._refresh_cart()
    
    def _update_summary(self):
        """Update cart summary"""
        subtotal = sum(item['total'] for item in self.cart)
        discount_percent = float(self.discount_entry.get() or 0)
        discount_amount = subtotal * (discount_percent / 100)
        after_discount = subtotal - discount_amount
        gst_amount = after_discount * (config.GST_RATE / 100)
        total = after_discount + gst_amount
        
        self.subtotal_label.configure(text=f"Subtotal: ₹{subtotal:,.2f}")
        self.discount_label.configure(text=f"Discount ({discount_percent}%): ₹{discount_amount:,.2f}")
        self.gst_label.configure(text=f"GST ({config.GST_RATE}%): ₹{gst_amount:,.2f}")
        self.total_label.configure(text=f"Total: ₹{total:,.2f}")
    
    def _complete_sale(self):
        """Complete sale and generate invoice"""
        if not self.cart:
            messagebox.showerror("Error", "Cart is empty")
            return
        
        try:
            # Calculate totals
            subtotal = sum(item['total'] for item in self.cart)
            discount_percent = float(self.discount_entry.get() or 0)
            discount_amount = subtotal * (discount_percent / 100)
            after_discount = subtotal - discount_amount
            gst_amount = after_discount * (config.GST_RATE / 100)
            total = after_discount + gst_amount
            
            # Generate bill number
            bill_prefix = self.db.get_setting(config.SETTING_BILL_PREFIX)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            bill_number = f"{bill_prefix}{timestamp}"
            
            # Insert sale
            sale_id = self.db.execute_insert(
                """INSERT INTO sales (bill_number, customer_name, customer_phone,
                   total_amount, discount_percent, discount_amount, gst_amount,
                   final_amount, payment_method, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (bill_number, self.customer_name_entry.get() or None,
                 self.customer_phone_entry.get() or None, subtotal, discount_percent,
                 discount_amount, gst_amount, total, "Cash",
                 self.current_user['username'])
            )
            
            # Insert sale items and update inventory
            for item in self.cart:
                self.db.execute_insert(
                    """INSERT INTO sale_items (sale_id, item_id, sku_code, item_name,
                       quantity, unit_price, total_price)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (sale_id, item['item_id'], item['sku'], item['name'],
                     item['quantity'], item['price'], item['total'])
                )
                
                # Update inventory
                self.db.execute_query(
                    "UPDATE inventory SET quantity = quantity - ? WHERE item_id = ?",
                    (item['quantity'], item['item_id'])
                )
            
            # Generate invoice
            invoice_path = self.invoice_gen.generate_invoice(sale_id)
            
            messagebox.showinfo(
                "Success",
                f"Sale completed!\n\nBill Number: {bill_number}\nInvoice saved: {invoice_path}"
            )
            
            # Clear cart
            self.cart.clear()
            self._refresh_cart()
            self.customer_name_entry.delete(0, 'end')
            self.customer_phone_entry.delete(0, 'end')
            self.discount_entry.delete(0, 'end')
            self.search_entry.delete(0, 'end')
            
            # Clear items
            for widget in self.items_frame.winfo_children():
                widget.destroy()
            
            # Ask to open invoice
            if messagebox.askyesno("Open Invoice", "Do you want to open the invoice?"):
                os.startfile(invoice_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")
