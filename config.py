"""
Configuration settings for the Boutique Management System
"""
import os
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Colors:
    """Premium light purple/lavender color palette"""
    # Primary Colors
    PRIMARY = "#7C3AED"  # Vibrant Purple
    PRIMARY_LIGHT = "#A78BFA"  # Light Purple
    PRIMARY_DARK = "#5B21B6"  # Dark Purple
    SECONDARY = "#EC4899"  # Pink Accent
    ACCENT = "#8B5CF6"  # Purple Accent
    
    # Backgrounds
    BG_LIGHT = "#F5F3FF"  # Very Light Lavender
    BG_LIGHT_ALT = "#FAF9FC"  # Alternative Light Background
    CARD_BG = "#FFFFFF"  # Pure White Cards
    SIDEBAR_BG = "#FFFFFF"  # White Sidebar
    
    # Gradients
    GRADIENT_START = "#7C3AED"  # Purple
    GRADIENT_END = "#EC4899"  # Pink
    GRADIENT_LIGHT_START = "#A78BFA"
    GRADIENT_LIGHT_END = "#F3E8FF"
    
    # Text Colors
    TEXT_PRIMARY = "#1F2937"  # Dark Gray
    TEXT_SECONDARY = "#6B7280"  # Medium Gray
    TEXT_LIGHT = "#9CA3AF"  # Light Gray
    TEXT_WHITE = "#FFFFFF"
    
    # Semantic Colors
    SUCCESS = "#10B981"  # Green
    SUCCESS_LIGHT = "#D1FAE5"
    WARNING = "#F59E0B"  # Amber
    WARNING_LIGHT = "#FEF3C7"
    DANGER = "#EF4444"  # Red
    DANGER_LIGHT = "#FEE2E2"
    INFO = "#3B82F6"  # Blue
    INFO_LIGHT = "#DBEAFE"
    
    # Chart Colors
    CHART_COLORS = [
        "#7C3AED", "#EC4899", "#8B5CF6", "#F472B6",
        "#A78BFA", "#FB7185", "#C4B5FD", "#FDA4AF"
    ]
    
    # UI Elements
    BORDER_LIGHT = "#E5E7EB"
    BORDER_MEDIUM = "#D1D5DB"
    SHADOW = "rgba(0, 0, 0, 0.1)"
    HOVER_BG = "#F3F4F6"
    
    # Dark theme variants (for theme toggle)
    DARK_BG = "#1F2937"
    DARK_CARD = "#374151"
    DARK_TEXT = "#F9FAFB"

@dataclass
class AppConfig:
    """Application configuration"""
    APP_NAME = "Saree Boutique Management System"
    VERSION = "1.0.0"
    COMPANY_NAME = "Ethnic Elegance Boutique"
    DEFAULT_ADMIN_PIN = "1234"  # Change in production
    DEFAULT_BILLING_PIN = "5678"  # Change in production
    GST_RATE = 18  # 18% GST
    LOGO_PATH = os.path.join("assets", "logo.png") if os.path.exists(os.path.join("assets", "logo.png")) else None
    
    # Database
    DB_NAME = "boutique_management.db"
    
    # Paths
    INVOICE_DIR = "invoices"
    BACKUP_DIR = "backups"
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories"""
        for directory in [cls.INVOICE_DIR, cls.BACKUP_DIR]:
            os.makedirs(directory, exist_ok=True)