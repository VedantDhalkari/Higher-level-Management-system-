"""
Invoice Generator Module
Generates professional PDF invoices using ReportLab with premium purple branding
"""

from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import config


class InvoiceGenerator:
    """Handles PDF invoice generation"""
    
    def __init__(self, db_manager):
        """
        Initialize invoice generator
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.invoices_dir = Path(config.INVOICES_DIR)
        self.invoices_dir.mkdir(exist_ok=True)
    
    def generate_invoice(self, sale_id: int) -> str:
        """
        Generate PDF invoice for a sale
        
        Args:
            sale_id: Sale ID from database
            
        Returns:
            Path to generated PDF file
        """
        # Get sale details
        sale_data = self.db.execute_query(
            """SELECT bill_number, customer_name, customer_phone, total_amount,
               discount_percent, discount_amount, gst_amount, final_amount,
               payment_method, sale_date FROM sales WHERE sale_id = ?""",
            (sale_id,)
        )[0]
        
        # Get sale items
        items_data = self.db.execute_query(
            """SELECT sku_code, item_name, quantity, unit_price, total_price
               FROM sale_items WHERE sale_id = ?""",
            (sale_id,)
        )
        
        # Get shop details
        shop_name = self.db.get_setting(config.SETTING_SHOP_NAME)
        shop_address = self.db.get_setting(config.SETTING_SHOP_ADDRESS)
        shop_phone = self.db.get_setting(config.SETTING_SHOP_PHONE)
        shop_email = self.db.get_setting(config.SETTING_SHOP_EMAIL)
        gst_number = self.db.get_setting(config.SETTING_GST_NUMBER)
        
        # Create PDF
        bill_number = sale_data[0]
        filename = self.invoices_dir / f"{bill_number}.pdf"
        
        doc = SimpleDocTemplate(str(filename), pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles with purple theme
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor(config.COLOR_PRIMARY),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        # Shop Header
        story.append(Paragraph(shop_name, title_style))
        story.append(Paragraph(f"{shop_address}", header_style))
        story.append(Paragraph(f"Phone: {shop_phone} | Email: {shop_email}", header_style))
        story.append(Paragraph(f"GSTIN: {gst_number}", header_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice heading
        invoice_heading = ParagraphStyle(
            'InvoiceHeading',
            parent=styles['Heading2'],
            textColor=colors.HexColor(config.COLOR_PRIMARY),
            alignment=TA_CENTER
        )
        story.append(Paragraph("<b>TAX INVOICE</b>", invoice_heading))
        story.append(Spacer(1, 0.2*inch))
        
        # Invoice details
        invoice_info = [
            ["Bill No:", bill_number, "Date:", sale_data[9][:10]],
            ["Customer:", sale_data[1] or "Walk-in Customer", "Phone:", sale_data[2] or "N/A"],
            ["Payment:", sale_data[8] or "Cash", "", "", ""]
        ]
        
        t = Table(invoice_info, colWidths=[1.5*inch, 2.5*inch, 1*inch, 2*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # Items table
        items_table_data = [
            ["S.No", "SKU", "Item Description", "Qty", "Rate", "Amount"]
        ]
        
        for idx, item in enumerate(items_data, 1):
            items_table_data.append([
                str(idx),
                item[0],
                item[1],
                str(item[2]),
                f"₹{item[3]:,.2f}",
                f"₹{item[4]:,.2f}"
            ])
        
        items_table = Table(
            items_table_data, 
            colWidths=[0.5*inch, 1*inch, 3.2*inch, 0.6*inch, 1.2*inch, 1.3*inch]
        )
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(config.COLOR_PRIMARY)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('LEFTPADDING', (2, 1), (2, -1), 10),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Totals section
        totals_data = [
            ["", "", "", "", "Subtotal:", f"₹{sale_data[3]:,.2f}"],
            ["", "", "", "", f"Discount ({sale_data[4]}%):", f"- ₹{sale_data[5]:,.2f}"],
            ["", "", "", "", f"GST ({config.GST_RATE}%):", f"₹{sale_data[6]:,.2f}"],
            ["", "", "", "", "Grand Total:", f"₹{sale_data[7]:,.2f}"]
        ]
        
        totals_table = Table(
            totals_data, 
            colWidths=[0.5*inch, 1*inch, 3.2*inch, 0.6*inch, 1.2*inch, 1.3*inch]
        )
        totals_table.setStyle(TableStyle([
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (4, 0), (4, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (4, 0), (-1, -1), 10),
            ('LINEABOVE', (4, -1), (-1, -1), 2, colors.black),
            ('FONTSIZE', (4, -1), (-1, -1), 12),
            ('FONTNAME', (4, -1), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (4, -1), (-1, -1), colors.HexColor(config.COLOR_PRIMARY)),
            ('TOPPADDING', (4, -1), (-1, -1), 10),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor(config.COLOR_PRIMARY)
        )
        
        terms_style = ParagraphStyle(
            'Terms',
            parent=styles['Italic'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.gray
        )
        
        story.append(Paragraph("<b>Thank you for shopping with us!</b>", footer_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("*Terms & Conditions Apply", terms_style))
        story.append(Paragraph("This is a computer generated invoice", terms_style))
        
        # Build PDF
        doc.build(story)
        return str(filename)
