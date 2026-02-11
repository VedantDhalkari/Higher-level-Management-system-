"""
Premium UI Components for Boutique Management System
Modern, reusable components with animations and premium styling
"""
import customtkinter as ctk
from typing import Optional, Callable, List, Tuple
from config import Colors
from PIL import Image, ImageDraw, ImageFilter
import io


class GradientCard(ctk.CTkFrame):
    """Card with gradient background"""
    
    def __init__(self, parent, gradient_start=None, gradient_end=None, **kwargs):
        # Set default colors
        fg_color = kwargs.pop('fg_color', Colors.CARD_BG)
        super().__init__(parent, fg_color=fg_color, corner_radius=15, **kwargs)
        
        self.gradient_start = gradient_start or Colors.GRADIENT_START
        self.gradient_end = gradient_end or Colors.GRADIENT_END


class StatCard(ctk.CTkFrame):
    """Premium metric/statistic display card with icon and animation"""
    
    def __init__(self, parent, title: str, value: str, subtitle: str = "",
                 icon: str = "📊", color: str = Colors.PRIMARY, **kwargs):
        super().__init__(parent, fg_color=Colors.CARD_BG, corner_radius=15, 
                        border_width=1, border_color=Colors.BORDER_LIGHT, **kwargs)
        
        self.title = title
        self.color = color
        
        # Add shadow effect via padding
        self.grid_propagate(False)
        
        # Content container
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=25, pady=20)
        
        # Icon with colored background (use light variant instead of alpha)
        # Determine light background color based on the main color
        if color == Colors.PRIMARY:
            icon_bg = "#E9D5FF"  # Light purple
        elif color == Colors.SUCCESS:
            icon_bg = "#D1FAE5"  # Light green
        elif color == Colors.WARNING:
            icon_bg = "#FEF3C7"  # Light amber
        elif color == Colors.INFO:
            icon_bg = "#DBEAFE"  # Light blue
        else:
            icon_bg = Colors.BG_LIGHT  # Fallback
        
        icon_frame = ctk.CTkFrame(content, fg_color=icon_bg, 
                                 corner_radius=10, width=50, height=50)
        icon_frame.pack(anchor="w", pady=(0, 10))
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(icon_frame, text=icon, 
                                 font=ctk.CTkFont(size=24))
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Value (main metric)
        self.value_label = ctk.CTkLabel(
            content, text=value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=color
        )
        self.value_label.pack(anchor="w", pady=(0, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            content, text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.pack(anchor="w")
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            content, text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color=Colors.TEXT_SECONDARY
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, event):
        """Hover effect - subtle lift"""
        self.configure(border_color=Colors.PRIMARY_LIGHT)
        
    def _on_leave(self, event):
        """Remove hover effect"""
        self.configure(border_color=Colors.BORDER_LIGHT)
        
    def update_value(self, value: str, subtitle: str = None):
        """Update the card's value and optionally subtitle"""
        self.value_label.configure(text=value)
        if subtitle:
            self.subtitle_label.configure(text=subtitle)


class AnimatedButton(ctk.CTkButton):
    """Button with smooth hover animations"""
    
    def __init__(self, parent, **kwargs):
        # Default styling
        default_kwargs = {
            'corner_radius': 10,
            'height': 40,
            'font': ctk.CTkFont(size=14, weight="bold"),
            'fg_color': Colors.PRIMARY,
            'hover_color': Colors.PRIMARY_DARK,
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)


class ModernTable(ctk.CTkFrame):
    """Modern table with styled headers and rows"""
    
    def __init__(self, parent, columns: List[str], column_widths: List[int] = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.columns = columns
        self.column_widths = column_widths or [1] * len(columns)
        self.rows = []
        
        # Configure grid
        for i, width in enumerate(self.column_widths):
            self.grid_columnconfigure(i, weight=width, uniform="col")
        
        # Create header
        self._create_header()
        
    def _create_header(self):
        """Create table header"""
        header_frame = ctk.CTkFrame(self, fg_color=Colors.BG_LIGHT, 
                                   corner_radius=8, height=45)
        header_frame.grid(row=0, column=0, columnspan=len(self.columns), 
                         sticky="ew", pady=(0, 10))
        header_frame.grid_propagate(False)
        
        for i, col in enumerate(self.columns):
            header_frame.grid_columnconfigure(i, weight=self.column_widths[i])
            
            label = ctk.CTkLabel(
                header_frame, text=col,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            )
            label.grid(row=0, column=i, sticky="ew", padx=15)
    
    def add_row(self, data: List[str], row_colors: List[str] = None):
        """Add a row to the table"""
        row_num = len(self.rows) + 1
        
        # Alternating row background
        bg_color = Colors.CARD_BG if row_num % 2 == 0 else Colors.BG_LIGHT_ALT
        
        row_widgets = []
        for i, value in enumerate(data):
            text_color = row_colors[i] if row_colors and i < len(row_colors) else Colors.TEXT_PRIMARY
            
            label = ctk.CTkLabel(
                self, text=value,
                font=ctk.CTkFont(size=13),
                text_color=text_color,
                fg_color=bg_color,
                anchor="w",
                height=40
            )
            label.grid(row=row_num, column=i, sticky="ew", padx=15, pady=1)
            row_widgets.append(label)
        
        self.rows.append(row_widgets)
        return row_widgets
    
    def clear_rows(self):
        """Clear all rows except header"""
        for row in self.rows:
            for widget in row:
                widget.destroy()
        self.rows.clear()


class StatusBadge(ctk.CTkLabel):
    """Colored status badge"""
    
    STATUS_COLORS = {
        'success': (Colors.SUCCESS, Colors.SUCCESS_LIGHT),
        'warning': (Colors.WARNING, Colors.WARNING_LIGHT),
        'danger': (Colors.DANGER, Colors.DANGER_LIGHT),
        'info': (Colors.INFO, Colors.INFO_LIGHT),
        'completed': (Colors.SUCCESS, Colors.SUCCESS_LIGHT),
        'pending': (Colors.WARNING, Colors.WARNING_LIGHT),
        'cancelled': (Colors.DANGER, Colors.DANGER_LIGHT),
    }
    
    def __init__(self, parent, text: str, status: str = 'info', **kwargs):
        text_color, bg_color = self.STATUS_COLORS.get(status.lower(), 
                                                       (Colors.TEXT_PRIMARY, Colors.BG_LIGHT))
        
        super().__init__(
            parent, text=f" {text} ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=text_color,
            fg_color=bg_color,
            corner_radius=6,
            **kwargs
        )


class IconLabel(ctk.CTkFrame):
    """Text with icon combination"""
    
    def __init__(self, parent, icon: str, text: str, 
                icon_color: str = Colors.PRIMARY, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        icon_label = ctk.CTkLabel(
            self, text=icon,
            font=ctk.CTkFont(size=16),
            text_color=icon_color
        )
        icon_label.pack(side="left", padx=(0, 8))
        
        text_label = ctk.CTkLabel(
            self, text=text,
            font=ctk.CTkFont(size=14),
            text_color=Colors.TEXT_PRIMARY
        )
        text_label.pack(side="left")


class GreetingCard(ctk.CTkFrame):
    """Large greeting card with gradient background"""
    
    def __init__(self, parent, username: str, **kwargs):
        super().__init__(parent, fg_color=Colors.PRIMARY, corner_radius=20, 
                        height=180, **kwargs)
        self.grid_propagate(False)
        
        # Create gradient overlay (simulated with frames)
        overlay = ctk.CTkFrame(self, fg_color="transparent")
        overlay.pack(expand=True, fill="both", padx=40, pady=30)
        
        # Greeting text
        import datetime
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        
        greeting_label = ctk.CTkLabel(
            overlay,
            text=f"{greeting}, {username}!",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=Colors.TEXT_WHITE
        )
        greeting_label.pack(anchor="w")
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            overlay,
            text="Here's what's happening with your boutique today",
            font=ctk.CTkFont(size=15),
            text_color=Colors.TEXT_WHITE
        )
        subtitle.pack(anchor="w", pady=(5, 20))
        
        # Quick action buttons
        button_frame = ctk.CTkFrame(overlay, fg_color="transparent")
        button_frame.pack(anchor="w")
        
        new_bill_btn = ctk.CTkButton(
            button_frame,
            text="💰 New Bill",
            height=38,
            corner_radius=10,
            fg_color=Colors.TEXT_WHITE,
            text_color=Colors.PRIMARY,
            hover_color=Colors.BG_LIGHT,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        new_bill_btn.pack(side="left", padx=(0, 10))
        
        view_stock_btn = ctk.CTkButton(
            button_frame,
            text="📦 View Stock",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color=Colors.TEXT_WHITE,
            text_color=Colors.TEXT_WHITE,
            hover_color=Colors.PRIMARY_DARK,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        view_stock_btn.pack(side="left")
        
        self.new_bill_btn = new_bill_btn
        self.view_stock_btn = view_stock_btn


class GlassCard(ctk.CTkFrame):
    """Card with glassmorphism effect"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.CARD_BG,  # Remove alpha - use solid color
            corner_radius=15,
            border_width=1,
            border_color=Colors.BORDER_LIGHT,
            **kwargs
        )


class LiveClock(ctk.CTkLabel):
    """Real-time clock that updates every second"""
    
    def __init__(self, parent, date_format="%I:%M:%S %p", show_date=True, **kwargs):
        """
        Args:
            parent: Parent widget
            date_format: Time format string (default shows 12-hour with AM/PM)
            show_date: Whether to show date below time
            **kwargs: Additional CTkLabel arguments
        """
        default_kwargs = {
            'font': ctk.CTkFont(size=14, weight="bold"),
            'text_color': Colors.TEXT_PRIMARY,
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, text="", **default_kwargs)
        
        self.date_format = date_format
        self.show_date = show_date
        self._update_active = True
        self.update_time()
    
    def update_time(self):
        """Update the displayed time"""
        if not self._update_active:
            return
            
        from datetime import datetime
        now = datetime.now()
        
        if self.show_date:
            time_str = now.strftime(self.date_format)
            date_str = now.strftime("%d %B %Y")
            self.configure(text=f"{time_str}\n{date_str}")
        else:
            time_str = now.strftime(self.date_format)
            self.configure(text=time_str)
        
        # Schedule next update (1000ms = 1 second)
        self.after(1000, self.update_time)
    
    def stop(self):
        """Stop the clock updates (call when destroying)"""
        self._update_active = False


class ContentHeader(ctk.CTkFrame):
    """Header component for content sections with title and live date/time"""
    
    def __init__(self, parent, title, subtitle="", show_time=True, **kwargs):
        """
        Args:
            parent: Parent widget
            title: Main title text
            subtitle: Optional subtitle text
            show_time: Whether to show live clock on the right
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Left side - Title and subtitle
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w")
        
        # Title
        title_label = ctk.CTkLabel(
            left_frame,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.pack(anchor="w")
        
        # Subtitle (if provided)
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                left_frame,
                text=subtitle,
                font=ctk.CTkFont(size=14),
                text_color=Colors.TEXT_SECONDARY
            )
            subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Right side - Live clock (if enabled)
        if show_time:
            self.clock = LiveClock(
                self,
                date_format="%I:%M %p",
                show_date=True,
                font=ctk.CTkFont(size=13),
                text_color=Colors.TEXT_SECONDARY
            )
            self.clock.grid(row=0, column=1, sticky="e", padx=(20, 0))
        
        # Divider line
        divider = ctk.CTkFrame(self, height=2, fg_color=Colors.BORDER_LIGHT)
        divider.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(15, 0))

