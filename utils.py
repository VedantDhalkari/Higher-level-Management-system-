"""
Utility functions for the application
"""
import os
import random
import string
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import logging
from config import Colors, AppConfig

logger = logging.getLogger(__name__)

class InvoiceGenerator:
    """Generate professional PDF invoices"""
    
    @staticmethod
    def generate_invoice_number():
        """Generate unique invoice number"""
        date_str = datetime.now().strftime("%Y%m%d")
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"INV-{date_str}-{random_str}"
    
    @staticmethod
    def generate_invoice(sale_data, customer_info, items, save_path=None):
        """Generate PDF invoice"""
        if save_path is None:
            save_path = os.path.join(AppConfig.INVOICE_DIR, f"{sale_data['invoice_number']}.pdf")
        
        # Create invoice directory if not exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            save_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor(Colors.PRIMARY),
            alignment=1  # Center
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor(Colors.SECONDARY)
        )
        
        # Story elements
        story = []
        
        # Company Header
        company_title = Paragraph(AppConfig.COMPANY_NAME, title_style)
        story.append(company_title)
        
        story.append(Paragraph("Women's Ethnic Wear Boutique", styles['Heading3']))
        story.append(Spacer(1, 20))
        
        # Invoice title
        story.append(Paragraph(f"INVOICE: {sale_data['invoice_number']}", header_style))
        story.append(Paragraph(f"Date: {sale_data['created_at']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Customer info
        story.append(Paragraph("Bill To:", styles['Heading3']))
        story.append(Paragraph(f"Name: {customer_info['name']}", styles['Normal']))
        if customer_info.get('phone'):
            story.append(Paragraph(f"Phone: {customer_info['phone']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Items table
        table_data = [['Item', 'Quantity', 'Price', 'Total']]
        for item in items:
            table_data.append([
                item['name'],
                str(item['quantity']),
                f"₹{item['price']:.2f}",
                f"₹{item['total']:.2f}"
            ])
        
        # Add totals row
        table_data.append(['', '', 'Subtotal:', f"₹{sale_data['subtotal']:.2f}"])
        if sale_data.get('discount', 0) > 0:
            table_data.append(['', '', 'Discount:', f"-₹{sale_data['discount']:.2f}"])
        table_data.append(['', '', 'GST (18%):', f"₹{sale_data['gst_amount']:.2f}"])
        table_data.append(['', '', '<b>Total:</b>', f"<b>₹{sale_data['total_amount']:.2f}</b>"])
        
        # Create table
        table = Table(table_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Colors.PRIMARY)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -5), colors.white),
            ('GRID', (0, 0), (-1, -5), 1, colors.grey),
            ('SPAN', (0, -4), (1, -4)),
            ('ALIGN', (-2, -4), (-1, -1), 'RIGHT'),
            ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 30))
        
        # Payment info
        story.append(Paragraph(f"Payment Method: {sale_data.get('payment_method', 'Cash')}", styles['Normal']))
        story.append(Paragraph(f"Payment Status: {sale_data.get('payment_status', 'Completed')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Thank you note
        story.append(Paragraph("Thank you for your business!", styles['Italic']))
        story.append(Paragraph("We hope to see you again soon.", styles['Italic']))
        
        # Generate PDF
        doc.build(story)
        logger.info(f"Invoice generated: {save_path}")
        
        return save_path

class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_price(price_str):
        """Validate price input"""
        try:
            price = float(price_str)
            return price >= 0
        except ValueError:
            return False
    
    @staticmethod
    def validate_quantity(qty_str):
        """Validate quantity input"""
        try:
            qty = int(qty_str)
            return qty >= 0
        except ValueError:
            return False
    
    @staticmethod
    def validate_phone(phone_str):
        """Validate phone number"""
        if not phone_str:
            return True
        return phone_str.isdigit() and len(phone_str) == 10
    
    @staticmethod
    def validate_email(email_str):
        """Validate email address"""
        if not email_str:
            return True
        return '@' in email_str and '.' in email_str

class Formatters:
    """Data formatting utilities"""
    
    @staticmethod
    def format_currency(amount):
        """Format amount as Indian currency"""
        return f"₹{amount:,.2f}"
    
    @staticmethod
    def format_date(date_str):
        """Format date string"""
        if not date_str:
            return ""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%d %b %Y, %I:%M %p")
        except:
            return date_str
    
    @staticmethod
    def truncate_text(text, max_length=50):
        """Truncate text with ellipsis"""
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text