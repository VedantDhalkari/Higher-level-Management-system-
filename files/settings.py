"""
Settings Module
Application and shop settings configuration
"""

import customtkinter as ctk
from tkinter import messagebox
import config
from ui_components import AnimatedButton
from auth import verify_admin_pin


class SettingsModule(ctk.CTkFrame):
    """Settings and configuration interface"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_1, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=(0, config.SPACING_LG), anchor="w")
        
        # Settings card
        settings_card = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        settings_card.pack(fill="both", expand=True)
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(
            settings_card,
            fg_color="transparent",
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        scroll_frame.pack(fill="both", expand=True, padx=config.SPACING_XL, pady=config.SPACING_XL)
        
        # Shop Details Section
        section_label = ctk.CTkLabel(
            scroll_frame,
            text="Shop Details",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        section_label.pack(pady=(0, config.SPACING_MD), anchor="w")
        
        # Settings fields
        settings_fields = [
            ("Shop Name", config.SETTING_SHOP_NAME),
            ("Address", config.SETTING_SHOP_ADDRESS),
            ("Phone", config.SETTING_SHOP_PHONE),
            ("Email", config.SETTING_SHOP_EMAIL),
            ("GST Number", config.SETTING_GST_NUMBER),
            ("Bill Prefix", config.SETTING_BILL_PREFIX)
        ]
        
        self.entries = {}
        
        for label, key in settings_fields:
            # Label
            lbl = ctk.CTkLabel(
                scroll_frame,
                text=label,
                font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
                text_color=config.COLOR_TEXT_PRIMARY
            )
            lbl.pack(pady=(config.SPACING_MD, config.SPACING_XS), anchor="w")
            
            # Entry
            entry = ctk.CTkEntry(
                scroll_frame,
                height=config.INPUT_HEIGHT,
                border_color=config.COLOR_BORDER,
                border_width=1
            )
            entry.insert(0, self.db.get_setting(key) or "")
            entry.pack(fill="x", pady=(0, config.SPACING_XS))
            self.entries[key] = entry
        
        # Save button
        save_btn = AnimatedButton(
            scroll_frame,
            text="💾 Save Settings",
            width=200,
            height=config.BUTTON_HEIGHT_LG,
            fg_color=config.COLOR_SUCCESS,
            hover_color="#059669",
            command=self._save_settings
        )
        save_btn.pack(pady=config.SPACING_XL)
        
        # Admin Settings Section
        separator = ctk.CTkFrame(scroll_frame, height=2, fg_color=config.COLOR_BORDER)
        separator.pack(fill="x", pady=config.SPACING_LG)
        
        admin_label = ctk.CTkLabel(
            scroll_frame,
            text="Admin Settings",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        admin_label.pack(pady=(0, config.SPACING_MD), anchor="w")
        
        # Admin actions
        admin_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        admin_frame.pack(fill="x", pady=config.SPACING_SM)
        
        change_pin_btn = AnimatedButton(
            admin_frame,
            text="🔐 Change Admin PIN",
            width=200,
            height=config.BUTTON_HEIGHT,
            fg_color=config.COLOR_WARNING,
            hover_color="#D97706",
            command=self._change_pin
        )
        change_pin_btn.pack(side="left", padx=(0, config.SPACING_SM))
        
        backup_btn = AnimatedButton(
            admin_frame,
            text="💾 Backup Database",
            width=200,
            height=config.BUTTON_HEIGHT,
            fg_color=config.COLOR_INFO,
            hover_color="#2563EB",
            command=self._backup_database
        )
        backup_btn.pack(side="left")
        
        # About section
        separator2 = ctk.CTkFrame(scroll_frame, height=2, fg_color=config.COLOR_BORDER)
        separator2.pack(fill="x", pady=config.SPACING_LG)
        
        about_label = ctk.CTkLabel(
            scroll_frame,
            text="About",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        about_label.pack(pady=(0, config.SPACING_MD), anchor="w")
        
        about_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_PRIMARY
        )
        about_frame.pack(fill="x")
        
        about_text = f"""{config.APP_NAME}
Version: {config.VERSION}
{config.APP_SUBTITLE}

Premium boutique management system with modern UI,
inventory tracking, billing, and comprehensive reporting."""
        
        about_content = ctk.CTkLabel(
            about_frame,
            text=about_text,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_PRIMARY,
            justify="left"
        )
        about_content.pack(padx=config.SPACING_LG, pady=config.SPACING_LG, anchor="w")
    
    def _save_settings(self):
        """Save settings"""
        try:
            for key, entry in self.entries.items():
                value = entry.get().strip()
                if value:
                    self.db.update_setting(key, value)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def _change_pin(self):
        """Change admin PIN"""
        # Verify current PIN first
        if not verify_admin_pin(self.winfo_toplevel()):
            return
        
        # Create dialog for new PIN
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Admin PIN")
        dialog.geometry("400x250")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog, fg_color=config.COLOR_BG_CARD)
        main_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        ctk.CTkLabel(
            main_frame,
            text="Enter New PIN",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        ).pack(pady=(config.SPACING_LG, config.SPACING_SM))
        
        new_pin_entry = ctk.CTkEntry(
            main_frame,
            height=config.INPUT_HEIGHT,
            placeholder_text="New PIN",
            show="*",
            justify="center"
        )
        new_pin_entry.pack(fill="x", padx=config.SPACING_XL, pady=config.SPACING_SM)
        
        confirm_pin_entry = ctk.CTkEntry(
            main_frame,
            height=config.INPUT_HEIGHT,
            placeholder_text="Confirm PIN",
            show="*",
            justify="center"
        )
        confirm_pin_entry.pack(fill="x", padx=config.SPACING_XL, pady=config.SPACING_SM)
        
        def save_new_pin():
            new_pin = new_pin_entry.get()
            confirm_pin = confirm_pin_entry.get()
            
            if not new_pin or len(new_pin) < 4:
                messagebox.showerror("Error", "PIN must be at least 4 characters", parent=dialog)
                return
            
            if new_pin != confirm_pin:
                messagebox.showerror("Error", "PINs do not match", parent=dialog)
                return
            
            # In a real application, you would update this in a secure way
            messagebox.showinfo("Success", 
                              f"PIN changed successfully!\nNew PIN: {new_pin}\n\nUpdate config.ADMIN_PIN in code",
                              parent=dialog)
            dialog.destroy()
        
        AnimatedButton(
            main_frame,
            text="Save PIN",
            height=config.BUTTON_HEIGHT,
            fg_color=config.COLOR_PRIMARY,
            command=save_new_pin
        ).pack(pady=config.SPACING_LG)
    
    def _backup_database(self):
        """Backup database"""
        from shutil import copy2
        from datetime import datetime
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"boutique_backup_{timestamp}.db"
            copy2(config.DB_NAME, backup_name)
            
            messagebox.showinfo("Success", 
                              f"Database backed up successfully!\nBackup saved as: {backup_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to backup database: {str(e)}")
