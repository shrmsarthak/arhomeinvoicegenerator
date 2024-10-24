from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode

# Global variable to store items (since you're avoiding session/pickle)
items_list = []

# View to handle the first form submission
def index(request):
    if request.method == "POST":
        # Collect form data
        name = request.POST.get('name')
        address = request.POST.get("address")
        province = request.POST.get("province")
        country = request.POST.get("country")
        postalcode = request.POST.get("postalcode")

        # Dictionary to store the form data
        user_data = {
            "name": name,
            "address": address,
            "province": province,
            "country": country,
            "postalcode": postalcode
        }

        # Build the query string and construct the full URL
        query_string = urlencode(user_data)
        url = reverse('index_two') + '?' + query_string

        # Redirect to index_two with the query parameters
        return redirect(url)

    return render(request, "index.html")


# View to handle item addition and invoice generation
def index_two(request):
    global items_list  # Use global list to store items

    # Retrieve user data from query parameters
    user_data = {
        "name": request.GET.get("name"),
        "address": request.GET.get("address"),
        "province": request.GET.get("province"),
        "country": request.GET.get("country"),
        "postalcode": request.GET.get("postalcode")
    }

    if 'additem' in request.POST:
        description = request.POST.get("description")
        quantityorarea = request.POST.get("quantityorarea")
        unitprice = request.POST.get("unitprice")

        if description and quantityorarea and unitprice:
            # Append item to the global list
            items_list.append({
                'description': description,
                'quantityorarea': quantityorarea,
                'unitprice': unitprice
            })
        else:
            return render(request, 'index_two.html', {
                "mymessage": "Please enter data in the given fields.",
                "Flag": "True",
                'user_data': user_data,
                'items_list': items_list
            })

    elif 'generateinvoice' in request.POST:
        from reportlab.pdfgen import canvas
        from datetime import datetime
        from random import randint
        import os
        from django.conf import settings
        from django.http import FileResponse

        # Retrieve user info
        name = user_data["name"]
        address = user_data["address"]
        province = user_data["province"]
        country = user_data["country"]
        postalcode = user_data["postalcode"]
        postalcode = postalcode[:3] + " " + postalcode[3:]

        # Create PDF invoice
        BASE_DIR = settings.BASE_DIR
        outfilename = os.path.join(BASE_DIR, 'myapp/static/myapp/final_invoice.pdf')
        can = canvas.Canvas(outfilename)

        # Header and basic details
        can.drawString(25, 720, "Date: " + datetime.today().strftime('%Y-%m-%d'))
        can.drawString(25, 710, "Invoice No. " + str(randint(1, 100000)))

        can.drawString(25, 680, "BILLED TO")
        can.drawString(25, 660, name)
        can.drawString(25, 650, address + ", " + province)
        can.drawString(25, 640, country + " " + postalcode)

        # Invoice items
        base = 595
        current_base = base

        for item in items_list:
            description = item['description']
            quantity = item['quantityorarea']
            price = item['unitprice']
            total = int(quantity) * int(price)

            can.drawString(25, current_base - 25, description)
            can.drawString(260, current_base - 25, quantity)
            can.drawString(405, current_base - 25, "$" + price)
            can.drawString(525, current_base - 25, "$" + str(total))

            current_base -= 25

        # Finalize PDF and return it as a file response
        can.save()
        return FileResponse(open(outfilename, 'rb'), as_attachment=True)

    # Render the page with the form and items
    return render(request, "index_two.html", {
        'user_data': user_data,
        'items_list': items_list
    })
