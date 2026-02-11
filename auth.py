"""
Premium Authentication Module with Modern Login Screen
"""
import hashlib
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
import logging
from config import Colors, AppConfig

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, db):
        self.db = db
        self.current_user = None
    
    def hash_password(self, password):
        """Hash password using MD5 (for simplicity, use bcrypt in production)"""
        return hashlib.md5(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Authenticate user"""
        query = '''
            SELECT * FROM users 
            WHERE username = ? AND password_hash = ?
        '''
        user = self.db.execute_query(query, (username, self.hash_password(password)), fetch_one=True)
        
        if user:
            # Update last login
            self.db.execute_query(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now(), user['id'])
            )
            self.current_user = dict(user)
            return True
        return False
    
    def verify_admin_pin(self, pin):
        """Verify admin PIN for sensitive operations"""
        return pin == AppConfig.DEFAULT_ADMIN_PIN
    
    def verify_billing_pin(self, pin):
        """Verify billing PIN for stock management"""
        return pin == AppConfig.DEFAULT_BILLING_PIN


class LoginWindow(ctk.CTkFrame):
    """Premium split-screen login window"""
    
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=Colors.BG_LIGHT)
        self.parent = parent
        self.on_login_success = on_login_success
        self.auth = AuthManager(parent.db)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup modern split-screen login UI"""
        # Configure grid for split layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left side - Branding with gradient
        left_panel = ctk.CTkFrame(self, fg_color=Colors.PRIMARY, corner_radius=0)
        left_panel.grid(row=0, column=0, sticky="nsew")
        
        # Branding content
        brand_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        brand_container.pack(expand=True)
        
        # Logo icon
        logo_label = ctk.CTkLabel(
            brand_container,
            text="💎",
            font=ctk.CTkFont(size=80)
        )
        logo_label.pack(pady=(0, 20))
        
        # App name
        app_name = ctk.CTkLabel(
            brand_container,
            text="Boutique Manager",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=Colors.TEXT_WHITE
        )
        app_name.pack(pady=(0, 10))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            brand_container,
            text="Professional Edition",
            font=ctk.CTkFont(size=16),
            text_color=Colors.TEXT_WHITE
        )
        subtitle.pack(pady=(0, 30))
        
        # Company name
        company_name = ctk.CTkLabel(
            brand_container,
            text=AppConfig.COMPANY_NAME,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=Colors.TEXT_WHITE
        )
        company_name.pack()
        
        # Right side - Login form
        right_panel = ctk.CTkFrame(self, fg_color=Colors.CARD_BG, corner_radius=0)
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Center the form
        form_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_container.pack(expand=True, padx=80)
        
        # Welcome text
        welcome_label = ctk.CTkLabel(
            form_container,
            text="Welcome Back!",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        welcome_label.pack(pady=(0, 10), anchor="w")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            form_container,
            text="Sign in to continue to your dashboard",
            font=ctk.CTkFont(size=14),
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle_label.pack(pady=(0, 40), anchor="w")
        
        # Username label and field
        username_label = ctk.CTkLabel(
            form_container,
            text="Username",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        username_label.pack(anchor="w", pady=(0, 8))
        
        self.username_var = ctk.StringVar()
        username_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Enter your username",
            height=50,
            textvariable=self.username_var,
            font=ctk.CTkFont(size=14),
            border_width=2,
            corner_radius=10,
            border_color=Colors.BORDER_LIGHT,
            fg_color=Colors.BG_LIGHT
        )
        username_entry.pack(fill="x", pady=(0, 20))
        
        # Password label and field
        password_label = ctk.CTkLabel(
            form_container,
            text="Password",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        password_label.pack(anchor="w", pady=(0, 8))
        
        self.password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Enter your password",
            show="•",
            height=50,
            textvariable=self.password_var,
            font=ctk.CTkFont(size=14),
            border_width=2,
            corner_radius=10,
            border_color=Colors.BORDER_LIGHT,
            fg_color=Colors.BG_LIGHT
        )
        password_entry.pack(fill="x", pady=(0, 30))
        
        # Login button
        login_btn = ctk.CTkButton(
            form_container,
            text="Sign In",
            command=self.login,
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_DARK,
            corner_radius=10
        )
        login_btn.pack(fill="x", pady=(0, 20))
        
        # Default credentials hint
        hint_frame = ctk.CTkFrame(form_container, fg_color=Colors.INFO_LIGHT,
                                 corner_radius=10, height=50)
        hint_frame.pack(fill="x", pady=(10, 0))
        hint_frame.pack_propagate(False)
        
        hint_label = ctk.CTkLabel(
            hint_frame,
            text="ℹ️  Default credentials: admin / admin",
            font=ctk.CTkFont(size=12),
            text_color=Colors.INFO
        )
        hint_label.pack(expand=True)
        
        # Bind Enter key to login
        self.bind("<Return>", lambda e: self.login())
        password_entry.bind("<Return>", lambda e: self.login())
    
    def login(self):
        """Handle login attempt"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        if self.auth.authenticate(username, password):
            logger.info(f"User {username} logged in successfully")
            self.on_login_success(self.auth.current_user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")


class PinDialog(ctk.CTkToplevel):
    """Modern PIN verification dialog"""
    
    def __init__(self, parent, title="Enter PIN", verify_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.verify_callback = verify_callback
        self.result = None
        
        # Configure window
        self.configure(fg_color=Colors.BG_LIGHT)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.geometry("400x250")
        self.resizable(False, False)
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup modern PIN dialog UI"""
        self.grid_columnconfigure(0, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            self,
            text="🔐",
            font=ctk.CTkFont(size=40)
        )
        icon_label.grid(row=0, column=0, pady=(30, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Security Verification",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.grid(row=1, column=0, pady=(0, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            self,
            text="Please enter your admin PIN to continue",
            font=ctk.CTkFont(size=12),
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle_label.grid(row=2, column=0, pady=(0, 20))
        
        # PIN entry
        self.pin_var = ctk.StringVar()
        pin_entry = ctk.CTkEntry(
            self,
            placeholder_text="Enter 4-digit PIN",
            show="•",
            height=50,
            textvariable=self.pin_var,
            font=ctk.CTkFont(size=16),
            justify="center",
            width=200,
            border_width=2,
            border_color=Colors.PRIMARY,
            fg_color=Colors.CARD_BG
        )
        pin_entry.grid(row=3, column=0, padx=50, pady=(0, 25))
        pin_entry.focus_set()
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=(0, 25))
        
        # Submit button
        submit_btn = ctk.CTkButton(
            btn_frame,
            text="✓ Verify",
            command=self.verify_pin,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_DARK,
            corner_radius=10
        )
        submit_btn.grid(row=0, column=0, padx=5)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="✕ Cancel",
            command=self.cancel,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Colors.BORDER_LIGHT,
            text_color=Colors.TEXT_PRIMARY,
            hover_color=Colors.BORDER_MEDIUM,
            corner_radius=10
        )
        cancel_btn.grid(row=0, column=1, padx=5)
        
        # Bind Enter key
        self.bind("<Return>", lambda e: self.verify_pin())
    
    def verify_pin(self):
        """Verify entered PIN"""
        pin = self.pin_var.get().strip()
        if self.verify_callback and self.verify_callback(pin):
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Invalid PIN", "The PIN you entered is incorrect. Please try again.")
            self.pin_var.set("")
    
    def cancel(self):
        """Cancel PIN entry"""
        self.result = False
        self.destroy()
    
    def show(self):
        """Show dialog and wait for result"""
        self.wait_window()
        return self.result