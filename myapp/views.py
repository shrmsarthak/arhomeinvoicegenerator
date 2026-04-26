from django.shortcuts import render
from reportlab.pdfgen import canvas
from pathlib import Path
from random import randint
from datetime import datetime
import os
from django.http import FileResponse, JsonResponse
import io
import json
import re

BASE_DIR = Path(__file__).resolve().parent.parent

def invoice_app(request):
    """Single page invoice generator with Invoice/Estimate modes"""
    
    if request.method == "POST":
        # Get customer info
        customer_info = {
            "name": request.POST.get('name'),
            "address": request.POST.get('address'),
            "province": request.POST.get('province'),
            "country": request.POST.get('country'),
            "postalcode": request.POST.get('postalcode'),
        }
        
        # Get terms & conditions / notes
        terms_notes = request.POST.get('terms_notes', '')
        
        # Get invoice items from JSON string with error handling
        items_json = request.POST.get('items', '[]')
        
        # Fix: Handle empty or invalid JSON
        try:
            if not items_json or items_json.strip() == '' or items_json == '[]':
                invoice_items = []
            else:
                invoice_items = json.loads(items_json)
        except json.JSONDecodeError:
            invoice_items = []
        
        # Get document type (Invoice or Estimate)
        doc_type = request.POST.get('doc_type', 'invoice')
        
        # Get invoice/estimate number
        doc_number = request.POST.get('doc_number', str(randint(1, 100000)))
        
        # Validate - Return proper error message
        if not customer_info.get('name'):
            return JsonResponse({'error': 'Customer name is required'}, status=400)
        
        if not invoice_items or len(invoice_items) == 0:
            return JsonResponse({'error': 'Please add at least one item'}, status=400)
        
        # Validate each item has required fields
        for i, item in enumerate(invoice_items):
            if not item.get('description'):
                return JsonResponse({'error': f'Description required for item {i+1}'}, status=400)
            if not item.get('quantityorarea') or float(item.get('quantityorarea', 0)) <= 0:
                return JsonResponse({'error': f'Valid quantity required for item {i+1}'}, status=400)
            if not item.get('unitprice') or float(item.get('unitprice', 0)) <= 0:
                return JsonResponse({'error': f'Valid price required for item {i+1}'}, status=400)
        
        # Generate PDF
        buffer = generate_pdf(customer_info, invoice_items, doc_type, doc_number, terms_notes)
        
        # Create filename
        safe_name = re.sub(r'[^\w\s-]', '', customer_info.get('name', 'customer'))[:30]
        safe_name = re.sub(r'[-\s]+', '-', safe_name)
        date_str = datetime.today().strftime('%Y%m%d')
        filename = f"{safe_name}_{doc_type}_{date_str}.pdf"
        
        return FileResponse(buffer, as_attachment=True, filename=filename)
    
    return render(request, "invoice_app.html")

def generate_pdf(customer_info, invoice_items, doc_type, doc_number, terms_notes):
    """Generate PDF invoice or estimate with appropriate heading"""
    buffer = io.BytesIO()
    can = canvas.Canvas(buffer)
    
    # Header
    file_name = os.path.join(BASE_DIR, 'myapp/static/myapp/header.png')
    if os.path.exists(file_name):
        can.drawImage(file_name, 0, 570, width=570, preserveAspectRatio=True, mask='auto')
    
    can.setFont("Helvetica-Bold", 14)
    
    # Set heading based on document type
    if doc_type == 'estimate':
        heading = "    ESTIMATE"
        subheading = "    This is not an invoice. Valid for 30 days."
        # Add left margin by increasing X coordinate (move right)
        heading_x = 250  # Changed from 250 to 280 (30px left margin)
        subheading_x = 220  # Changed from 220 to 250 (30px left margin)
    else:
        heading = "TAX INVOICE"
        subheading = ""
        heading_x = 250  # Keep original position for invoice
        subheading_x = 220
    
    # Draw heading
    can.drawString(heading_x, 740, heading)
    if subheading:
        can.setFont("Helvetica", 8)
        can.drawString(subheading_x, 725, subheading)
        can.setFont("Helvetica", 10)
    
    # Document details
    can.setFont("Helvetica", 10)
    can.drawString(25, 720, "Date: " + datetime.today().strftime('%Y-%m-%d'))
    
    if doc_type == 'invoice':
        can.drawString(25, 710, f"Invoice No. {doc_number}")
    else:
        can.drawString(25, 710, f"Estimate No. {doc_number}")
    
    # Customer info
    can.drawString(25, 680, "BILLED TO")
    can.drawString(25, 660, customer_info.get("name", ""))
    address = customer_info.get("address", "")
    province = customer_info.get("province", "")
    can.drawString(25, 650, address + ", " + province)
    
    country = customer_info.get("country", "")
    postalcode = customer_info.get("postalcode", "")
    if len(postalcode) > 3:
        postalcode = postalcode[:3] + " " + postalcode[3:]
    can.drawString(25, 640, country + " " + postalcode)
    
    can.line(570, 610, 25, 610)
    
    # Owner info
    can.setFont("Helvetica", 10)
    can.drawString(345, 700, "Amandeep Singh")
    can.drawString(345, 680, "AR Home Renovation & Construction Inc. C/O")
    can.drawString(345, 670, "411 Popular Avenue, Summerside")
    can.drawString(345, 660, "Canada C1N 2B9")
    
    # Item details header
    can.drawString(25, 595, "Description")
    can.drawString(225, 595, "Quantity or Area")
    can.drawString(400, 595, "Price")
    can.drawString(520, 595, "Total")
    can.line(570, 585, 25, 585)
    
    base = 595
    current_base = 0
    subtotal = 0
    
    for i, item in enumerate(invoice_items):
        description = item.get('description', '')
        quantity = item.get('quantityorarea', 0)
        price = item.get('unitprice', 0)
        total = round(float(quantity) * float(price), 2)
        subtotal += total
        
        # Drawing items
        can.drawString(25, base - (i + 1) * 25, description[:40])
        can.drawString(260, base - (i + 1) * 25, str(quantity))
        can.drawString(405, base - (i + 1) * 25, "$" + str(price))
        can.drawString(525, base - (i + 1) * 25, "$" + str(total))
        
        if i == len(invoice_items) - 1:
            current_base = base - (i + 1) * 25
    
    can.line(570, current_base - 12, 25, current_base - 12)
    
    # Subtotal
    can.drawString(405, current_base - 30, "Sub Total")
    can.drawString(525, current_base - 30, "$" + str(subtotal))
    
    # Total after tax
    can.drawString(405, current_base - 50, "Tax (15%)")
    can.drawString(525, current_base - 50, "$" + str(round(subtotal * 0.15, 2)))
    
    can.line(570, current_base - 60, 400, current_base - 60)
    
    can.drawString(405, current_base - 80, "Total")
    total_amount = subtotal + (subtotal * 0.15)
    can.drawString(525, current_base - 80, "$" + str(round(total_amount, 2)))
    
    # Terms & Conditions - 50px below total, left aligned (x=25)
    if terms_notes and terms_notes.strip():
        # Position 50px below the total (current_base - 130)
        terms_y_position = current_base - 130
        
        # Draw "Terms & Conditions" header
        can.setFont("Helvetica-Bold", 9)
        can.drawString(25, terms_y_position, "TERMS & CONDITIONS:")
        
        # Draw the terms content with word wrapping
        can.setFont("Helvetica", 8)
        terms_text = terms_notes.strip()
        
        # Word wrap the terms (max ~80 characters per line)
        lines = []
        words = terms_text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) <= 80:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw each line of terms
        line_y = terms_y_position - 15
        for line in lines:
            if line_y > 50:  # Don't go below page bottom
                can.drawString(25, line_y, line)
                line_y -= 12
    
    # Contact info
    can.drawString(25, 175, "CONTACT INFORMATION")
    can.drawString(25, 150, "Phone : 647-622-4449")
    can.drawString(25, 140, "Email: Arhomerenovation1@gmail.com")
    can.drawString(25, 130, "Website: https://arhomerenovation.ca/")
    
    can.drawString(450, 130, "HST No. 732134002RT001")
    
    footer_filename = os.path.join(BASE_DIR, 'myapp/static/myapp/footer.png')
    if os.path.exists(footer_filename):
        can.drawImage(footer_filename, 0, -130, width=570, preserveAspectRatio=True, mask='auto')
    
    # Add validity note for estimates
    if doc_type == 'estimate':
        can.setFont("Helvetica-Oblique", 8)
        can.drawString(25, 100, "This is a price estimate only. Actual invoice may vary based on final work completed.")
        can.drawString(25, 90, "Please contact us for any changes or questions regarding this estimate.")
    
    can.showPage()
    can.save()
    
    buffer.seek(0)
    return buffer