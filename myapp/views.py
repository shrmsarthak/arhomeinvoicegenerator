from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from reportlab.pdfgen import canvas
from pathlib import Path
from random import randint
from datetime import datetime
import os
from django.conf import settings
from django.http import HttpResponse, FileResponse

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize global variables to store data in lists
invoice_items = []
customer_info = {}

def index(request):
    global customer_info

    if request.method == "POST":
        name = request.POST.get('name')
        address = request.POST.get("address")
        province = request.POST.get("province")
        country = request.POST.get("country")
        postalcode = request.POST.get("postalcode")

        # Store customer information in a dictionary
        customer_info = {
            "name": name,
            "address": address,
            "province": province,
            "country": country,
            "postalcode": postalcode
        }

        return redirect('index_two')

    return render(request, "index.html")

def index_two(request):
    global invoice_items, customer_info

    if request.method == "POST":

        if 'additem' in request.POST:
            description = request.POST.get("description")
            quantityorarea = request.POST.get("quantityorarea")
            unitprice = request.POST.get("unitprice")

            if len(description) != 0 and len(quantityorarea) != 0 and len(unitprice) != 0:
                # Add item to the list of invoice items
                invoice_items.append({
                    'description': description,
                    'quantityorarea': quantityorarea,
                    'unitprice': unitprice
                })

                print(invoice_items)

            else:
                return render(request, 'index_two.html', {"mymessage": "Please enter data in the given fields.", "Flag": "True"})

        elif 'generateinvoice' in request.POST:
            if not invoice_items or not customer_info:
                return render(request, 'index_two.html', {"mymessage": "No items or customer info available to generate invoice.", "Flag": "True"})

            name = customer_info.get("name")
            address = customer_info.get("address")
            province = customer_info.get("province")
            country = customer_info.get("country")
            postalcode = customer_info.get("postalcode", "")[:3] + " " + customer_info.get("postalcode", "")[3:]

            outfilename = os.path.join(BASE_DIR, 'myapp/static/myapp/final_invoice.pdf')

            can = canvas.Canvas(outfilename)

            # Header
            file_name = os.path.join(BASE_DIR, 'myapp/static/myapp/header.png')
            can.drawImage(file_name, 0, 570, width=570, preserveAspectRatio=True, mask='auto')
            can.setFont("Helvetica", 10)

            # Invoice details
            can.drawString(25, 720, "Date: " + datetime.today().strftime('%Y-%m-%d'))
            can.drawString(25, 710, "Invoice No. " + str(randint(1, 100000)))

            # Customer info
            can.drawString(25, 680, "BILLED TO")
            can.drawString(25, 660, name)
            can.drawString(25, 650, address + ", " + province)
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
                description = item['description']
                quantity = item['quantityorarea']
                price = item['unitprice']
                total = int(quantity) * int(price)

                subtotal += total

                # Drawing items
                can.drawString(25, base - (i + 1) * 25, description)
                can.drawString(260, base - (i + 1) * 25, quantity)
                can.drawString(405, base - (i + 1) * 25, "$" + price)
                can.drawString(525, base - (i + 1) * 25, "$" + str(total))

                if i == len(invoice_items) - 1:
                    current_base = base - (i + 1) * 25

            can.line(570, current_base - 12, 25, current_base - 12)

            # Subtotal
            can.drawString(405, current_base - 30, "Sub Total")
            can.drawString(525, current_base - 30, "$" + str(subtotal))

            # Total after tax
            can.drawString(405, current_base - 50, "Tax (15%)")
            can.drawString(525, current_base - 50, "$" + str(subtotal * 0.15))

            can.line(570, current_base - 60, 400, current_base - 60)

            can.drawString(405, current_base - 80, "Total")
            can.drawString(525, current_base - 80, "$" + str(subtotal + (subtotal * 0.15)))

            # Contact info
            can.drawString(25, 175, "CONTACT INFORMATION")
            can.drawString(25, 150, "Phone : 647-622-4449")
            can.drawString(25, 140, "Email: Arhomerenovation1@gmail.com")
            can.drawString(25, 130, "Website: https://arhomerenovation.ca/")

            can.drawString(450, 130, "HST No. 732134002RT001")

            footer_filename = os.path.join(BASE_DIR, 'myapp/static/myapp/footer.png')
            can.drawImage(footer_filename, 0, -130, width=570, preserveAspectRatio=True, mask='auto')

            can.showPage()
            can.save()

            return FileResponse(open(outfilename, 'rb'), as_attachment=True)

    return render(request, "index_two.html")
