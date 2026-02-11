"""
Chart components for data visualization
Uses matplotlib for creating beautiful charts integrated with CustomTkinter
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import customtkinter as ctk
from config import Colors
from typing import List, Tuple
import matplotlib.dates as mdates
from datetime import datetime, timedelta


class ChartBase:
    """Base class for all charts with common styling"""
    
    @staticmethod
    def setup_chart_style():
        """Configure matplotlib to match our design system"""
        plt.rcParams['font.family'] = 'Segoe UI'
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.facecolor'] = Colors.CARD_BG
        plt.rcParams['figure.facecolor'] = Colors.CARD_BG
        plt.rcParams['text.color'] = Colors.TEXT_PRIMARY
        plt.rcParams['axes.labelcolor'] = Colors.TEXT_SECONDARY
        plt.rcParams['xtick.color'] = Colors.TEXT_SECONDARY
        plt.rcParams['ytick.color'] = Colors.TEXT_SECONDARY
        plt.rcParams['axes.edgecolor'] = Colors.BORDER_LIGHT


class EarningsBarChart(ctk.CTkFrame):
    """Bar chart for displaying earnings over time"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=Colors.CARD_BG, corner_radius=15,
                        border_width=1, border_color=Colors.BORDER_LIGHT, **kwargs)
        
        ChartBase.setup_chart_style()
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))
        
        title = ctk.CTkLabel(
            header,
            text="Earnings",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(side="left")
        
        # Time period selector
        self.period_var = ctk.StringVar(value="This Week")
        period_menu = ctk.CTkOptionMenu(
            header,
            values=["Today", "This Week", "This Month"],
            variable=self.period_var,
            width=120,
            height=28,
            fg_color=Colors.BG_LIGHT,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_DARK,
            font=ctk.CTkFont(size=12)
        )
        period_menu.pack(side="right")
        
        # Chart container
        self.chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        
        self.canvas = None
        self.create_sample_chart()
    
    def create_sample_chart(self):
        """Create a sample earnings chart"""
        # Sample data (you'll replace this with real data)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        earnings = [850, 920, 1100, 980, 1250, 1400, 1150]
        
        self.update_chart(days, earnings)
    
    def update_chart(self, labels: List[str], values: List[float]):
        """Update chart with new data"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        # Create figure
        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create bars with gradient effect
        bars = ax.bar(labels, values, color=Colors.PRIMARY, alpha=0.8, width=0.6)
        
        # Color bars with gradient
        for i, bar in enumerate(bars):
            # Alternate colors for visual interest
            if i % 2 == 0:
                bar.set_color(Colors.PRIMARY)
            else:
                bar.set_color(Colors.PRIMARY_LIGHT)
        
        # Styling
        ax.set_ylabel('Amount (₹)', fontsize=10, color=Colors.TEXT_SECONDARY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(Colors.BORDER_LIGHT)
        ax.spines['bottom'].set_color(Colors.BORDER_LIGHT)
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Format y-axis to show currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{int(x)}'))
        
        fig.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


class CategoryPieChart(ctk.CTkFrame):
    """Pie chart for category distribution"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=Colors.CARD_BG, corner_radius=15,
                        border_width=1, border_color=Colors.BORDER_LIGHT, **kwargs)
        
        ChartBase.setup_chart_style()
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="Sales by Category",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        header.pack(pady=(15, 5), padx=20, anchor="w")
        
        # Chart container
        self.chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        
        self.canvas = None
        self.create_sample_chart()
    
    def create_sample_chart(self):
        """Create a sample pie chart"""
        categories = ['Silk Sarees', 'Cotton Sarees', 'Designer Wear', 'Accessories']
        values = [35, 25, 30, 10]
        
        self.update_chart(categories, values)
    
    def update_chart(self, labels: List[str], values: List[float]):
        """Update chart with new data"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        # Create figure
        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create pie chart
        colors = Colors.CHART_COLORS[:len(labels)]
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'color': Colors.TEXT_PRIMARY, 'fontsize': 9}
        )
        
        # Make percentage text white
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.axis('equal')
        fig.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


class TrendLineChart(ctk.CTkFrame):
    """Line chart for showing trends over time"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=Colors.CARD_BG, corner_radius=15,
                        border_width=1, border_color=Colors.BORDER_LIGHT, **kwargs)
        
        ChartBase.setup_chart_style()
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="Sales Trend",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        header.pack(pady=(15, 5), padx=20, anchor="w")
        
        # Chart container
        self.chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        
        self.canvas = None
        self.create_sample_chart()
    
    def create_sample_chart(self):
        """Create a sample trend chart"""
        # Generate sample data for last 30 days
        dates = [(datetime.now() - timedelta(days=x)).strftime('%d/%m') 
                for x in range(30, 0, -1)]
        sales = [800 + (i * 50) + (i % 3) * 100 for i in range(30)]
        
        self.update_chart(dates[::3], sales[::3])  # Show every 3rd day
    
    def update_chart(self, dates: List[str], values: List[float]):
        """Update chart with new data"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        # Create figure
        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create line chart
        ax.plot(dates, values, color=Colors.PRIMARY, linewidth=2.5, marker='o', 
               markersize=5, markerfacecolor=Colors.PRIMARY_LIGHT)
        
        # Fill area under curve
        ax.fill_between(range(len(dates)), values, alpha=0.2, color=Colors.PRIMARY)
        
        # Styling
        ax.set_ylabel('Sales (₹)', fontsize=10, color=Colors.TEXT_SECONDARY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(Colors.BORDER_LIGHT)
        ax.spines['bottom'].set_color(Colors.BORDER_LIGHT)
        ax.grid(alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Rotate x-axis labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        fig.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


class MiniStatChart(ctk.CTkFrame):
    """Small inline chart for stat cards"""
    
    def __init__(self, parent, values: List[float], color: str = Colors.PRIMARY, **kwargs):
        super().__init__(parent, fg_color="transparent", width=80, height=40, **kwargs)
        self.pack_propagate(False)
        
        ChartBase.setup_chart_style()
        
        # Create mini sparkline
        fig = Figure(figsize=(1, 0.5), dpi=80)
        ax = fig.add_subplot(111)
        
        ax.plot(values, color=color, linewidth=1.5)
        ax.fill_between(range(len(values)), values, alpha=0.3, color=color)
        
        # Remove all axes decorations
        ax.axis('off')
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
