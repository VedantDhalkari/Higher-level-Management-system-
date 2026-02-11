"""
Settings Module
Application settings and configuration
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from config import Colors, AppConfig
from ui_components import ContentHeader, AnimatedButton
from datetime import datetime
import shutil
import os


class Settings(ctk.CTkFrame):
    """Settings and configuration section"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_LIGHT)
        self.parent = parent
        self.db = parent.db
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI"""
        # Header
        header = ContentHeader(
            self,
            title="Settings",
            subtitle="Configure application preferences and manage data"
        )
        header.pack(fill="x", padx=20, pady=20)
        
        # Main content with tabs
        self.tab_view = ctk.CTkTabview(self, fg_color=Colors.CARD_BG, corner_radius=15)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Add tabs
        self.tab_view.add("Shop Info")
        self.tab_view.add("Users")
        self.tab_view.add("Database")
        self.tab_view.add("Print Settings")
        
        # Setup each tab
        self.setup_shop_info_tab()
        self.setup_users_tab()
        self.setup_database_tab()
        self.setup_print_settings_tab()
    
    def setup_shop_info_tab(self):
        """Setup shop information tab"""
        tab = self.tab_view.tab("Shop Info")
        
        # Shop info form
        form_frame = ctk.CTkFrame(tab, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Form fields
        fields = [
            ("Shop Name", "Saree Boutique"),
            ("Address", "123 Main Street, City"),
            ("Phone", "+91 1234567890"),
            ("Email", "info@boutique.com"),
            ("GST Number", "27XXXXX1234X1ZX"),
        ]
        
        for i, (label, placeholder) in enumerate(fields):
            # Label
            lbl = ctk.CTkLabel(
                form_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            lbl.grid(row=i, column=0, sticky="w", padx=(0, 20), pady=10)
            
            # Entry
            entry = ctk.CTkEntry(
                form_frame,
                placeholder_text=placeholder,
                height=35
            )
            entry.grid(row=i, column=1, sticky="ew", pady=10)
            form_frame.grid_columnconfigure(1, weight=1)
        
        # Save button
        save_btn = AnimatedButton(
            form_frame,
            text="💾 Save Changes",
            command=self.save_shop_info,
            width=150,
            height=40
        )
        save_btn.grid(row=len(fields), column=1, sticky="e", pady=20)
    
    def setup_users_tab(self):
        """Setup users management tab"""
        tab = self.tab_view.tab("Users")
        
        info = ctk.CTkLabel(
            tab,
            text="👥 User Management\n\nUser management features will be available soon.\n"
                 "You'll be able to add, edit, and manage system users.",
            font=ctk.CTkFont(size=14),
            text_color=Colors.TEXT_SECONDARY,
            justify="center"
        )
        info.pack(expand=True)
    
    def setup_database_tab(self):
        """Setup database management tab"""
        tab = self.tab_view.tab("Database")
        
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Database info
        info_frame = ctk.CTkFrame(content, fg_color=Colors.BG_LIGHT, corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 30))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="💾 Database Management",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.PRIMARY
        )
        info_label.pack(pady=(20, 5))
        
        desc_label = ctk.CTkLabel(
            info_frame,
            text="Backup and restore your boutique data",
            font=ctk.CTkFont(size=13),
            text_color=Colors.TEXT_SECONDARY
        )
        desc_label.pack(pady=(0, 20))
        
        # Backup button
        backup_btn = AnimatedButton(
            content,
            text="📁 Create Backup",
            command=self.create_backup,
            width=200,
            height=45,
            fg_color=Colors.SUCCESS
        )
        backup_btn.pack(pady=10)
        
        # Restore button
        restore_btn = AnimatedButton(
            content,
            text="♻️ Restore from Backup",
            command=self.restore_backup,
            width=200,
            height=45
        )
        restore_btn.pack(pady=10)
    
    def setup_print_settings_tab(self):
        """Setup print settings tab"""
        tab = self.tab_view.tab("Print Settings")
        
        info = ctk.CTkLabel(
            tab,
            text="🖨️ Print Settings\n\nPrint configuration will be available soon.\n"
                 "Configure invoice templates and printer preferences.",
            font=ctk.CTkFont(size=14),
            text_color=Colors.TEXT_SECONDARY,
            justify="center"
        )
        info.pack(expand=True)
    
    def save_shop_info(self):
        """Save shop information"""
        messagebox.showinfo(
            "Success",
            "Shop information saved successfully!\n\n"
            "Note: Full implementation coming soon."
        )
    
    def create_backup(self):
        """Create database backup"""
        try:
            # Ask user where to save backup
            filename = f"boutique_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                initialfile=filename
            )
            
            if filepath:
                # Copy database file
                shutil.copy2(AppConfig.DB_NAME, filepath)
                messagebox.showinfo(
                    "Backup Created",
                    f"Database backup created successfully!\n\nLocation:\n{filepath}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup:\n{str(e)}")
    
    def restore_backup(self):
        """Restore database from backup"""
        if not messagebox.askyesno(
            "Confirm Restore",
            "⚠️ Warning!\n\nRestoring from a backup will replace all current data.\n"
            "Make sure you have a backup of the current database.\n\n"
            "Do you want to continue?"
        ):
            return
        
        try:
            # Ask user to select backup file
            filepath = filedialog.askopenfilename(
                title="Select Backup File",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            
            if filepath:
                # Close any active connections would go here
                # For now, just copy the file
                shutil.copy2(filepath, AppConfig.DB_NAME)
                messagebox.showinfo(
                    "Restore Complete",
                    "Database restored successfully!\n\nPlease restart the application for changes to take effect."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore backup:\n{str(e)}")
