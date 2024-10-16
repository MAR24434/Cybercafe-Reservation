from reportlab.lib.pagesizes import letter
import io
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from .forms import ReservationForm, PCRentalForm, PrintingOptionForm
from .models import UserAccount, Reservation, PCRental, PrintingOption
from django.utils.timezone import now
from django.contrib import messages
from reportlab.pdfgen import canvas
import hashlib

def hash_password(password):
    """Hash a password for storing in the database."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = UserAccount.objects.get(username=username)

            # Check the provided password against the hashed password in the database
            if check_password(password, user.password):
                # Set user session and redirect based on status
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['status'] = user.status

                if user.status == 'customer':
                    return redirect('customer_dashboard')
                elif user.status == 'employee':
                    return redirect('employee_dashboard')
                elif user.status == 'admin':
                    return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        except UserAccount.DoesNotExist:
            messages.error(request, "Invalid username or password.")

    return render(request, 'index.html')

# Sign-up view
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        name = request.POST['name']
        address = request.POST['address']
        password = request.POST['password']

        # Check if username or email already exists
        if UserAccount.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
        if UserAccount.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        # Create new user account with hashed password
        new_user = UserAccount(
            username=username,
            password=make_password(password),  # Hash the password
            email=email,
            name=name,
            address=address,
            status='customer'
        )
        new_user.save()

        messages.success(request, 'Sign up successful!')
        return redirect('login')
    
    return render(request, 'signup.html', {'is_admin': False})

# Admin account creation view
def add_account_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        name = request.POST['name']
        address = request.POST['address']
        password = request.POST['password']
        status = request.POST.get('status', 'customer')

        # Check if username or email already exists
        if UserAccount.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
        if UserAccount.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        # Create new user account with hashed password
        new_user = UserAccount(
            username=username,
            password=make_password(password),  # Hash the password
            email=email,
            name=name,
            address=address,
            status=status
        )
        new_user.save()

        messages.success(request, 'Sign up successful!')
        return redirect('manage_account')
    
    return render(request, 'signup.html', {'is_admin': True})

def customer_dashboard(request):
    user_id = request.session.get('user_id')
    filter_date = request.GET.get('filter_date')  # Get the selected date from the query parameters

    # If a filter date is provided, filter the reservations by that date
    if filter_date:
        reservations = Reservation.objects.filter(customer_id=user_id, date=filter_date).order_by('-date', '-time')
    else:
        # If no date is selected, show all reservations
        reservations = Reservation.objects.filter(customer_id=user_id).order_by('-date', '-time')

    # Pass the current date to the template
    context = {
        'reservations': reservations,
        'current_date': filter_date or ''  # Empty if no filter date, to show all by default
    }

    return render(request, 'customer_dashboard.html', context)

# Employee dashboard view
def employee_dashboard(request):
    filter_date = request.GET.get('filter_date')
    # Ensure the user is an employee (this should be part of your admin check)
    if request.session.get('status') != 'employee':
        return redirect('login')  # Redirect non-employee users to the login page
    if filter_date:
        reservations = Reservation.objects.all().order_by( date=filter_date).order_by('-date', '-time')
    else:
        # Fetch all reservations for the admin
        reservations = Reservation.objects.all().order_by('-date', '-time')  # Ordered by most recent

    context = {
        'reservations': reservations,
        'current_date': filter_date or ''
    }

    return render(request, 'employee_dashboard.html', context)

# Admin dashboard view
def admin_dashboard(request):
    filter_date = request.GET.get('filter_date')
    # Ensure the user is an employee (this should be part of your admin check)
    if request.session.get('status') != 'admin':
        return redirect('login')  # Redirect non-employee users to the login page
    if filter_date:
        reservations = Reservation.objects.all().order_by( date=filter_date).order_by('-date', '-time')
    else:
        # Fetch all reservations for the admin
        reservations = Reservation.objects.all().order_by('-date', '-time')  # Ordered by most recent

    context = {
        'reservations': reservations,
        'current_date': filter_date or ''
    }

    return render(request, 'admin_dashboard.html', context)
    
def manage_account_view(request):
    user_accounts = UserAccount.objects.all()  # Get all user accounts
    return render(request, 'manage_account.html', {'user_accounts': user_accounts})

def account_detail_view(request, account_id):
    account = get_object_or_404(UserAccount, id=account_id)
    return render(request, 'account_detail.html', {'account': account, 'request': request})

def update_account_view(request, account_id):
    account = get_object_or_404(UserAccount, id=account_id)
    if request.method == 'POST':
        # Handle form submission and update logic here
        # e.g., account.username = request.POST['username'], etc.
        account.save()
        return redirect('manage_account')  # Redirect after saving

    return render(request, 'update_account.html', {'account': account})

def delete_account_view(request, account_id):
    account = get_object_or_404(UserAccount, id=account_id)
    if request.method == 'POST':
        account.delete()
        return redirect('manage_account')  # Redirect after deletion

    return render(request, 'delete_account_confirmation.html', {'account': account})  # Render a confirmation template

def manage_services_view(request):
    pc_rentals = PCRental.objects.all()
    printing_options = PrintingOption.objects.all()
    return render(request, 'manage_services.html', {
        'pc_rentals': pc_rentals,
        'printing_options': printing_options,
    })

def add_or_edit_pc_rental_view(request, rental_id=None):
    if rental_id:
        rental = get_object_or_404(PCRental, id=rental_id)
        form = PCRentalForm(request.POST or None, instance=rental)
        service_type = 'Edit PC Rental'
    else:
        form = PCRentalForm(request.POST or None)
        service_type = 'Add PC Rental'

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('manage_services')

    return render(request, 'add_service.html', {'form': form, 'service_type': service_type})

def add_or_edit_printing_option_view(request, option_id=None):
    if option_id:
        option = get_object_or_404(PrintingOption, id=option_id)
        form = PrintingOptionForm(request.POST or None, instance=option)
        service_type = 'Edit Printing Option'
    else:
        form = PrintingOptionForm(request.POST or None)
        service_type = 'Add Printing Option'

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('manage_services')

    return render(request, 'add_service.html', {'form': form, 'service_type': service_type})


def delete_pc_rental_view(request, rental_id):
    rental = get_object_or_404(PCRental, id=rental_id)
    rental.delete()
    return redirect('manage_services')

def delete_printing_option_view(request, option_id):
    option = get_object_or_404(PrintingOption, id=option_id)
    option.delete()
    return redirect('manage_services')

# Reservation detail view to show reservation details and allow file download
def reservation_detail(request, reservation_id):
    # Ensure the user is authenticated
    if not request.session.get('user_id'):
        messages.error(request, "You need to be logged in to view this page.")
        return redirect('login')

    # Get the reservation, ensuring it belongs to the logged-in user
    if request.session.get('status') != 'customer':
        reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    else:
        reservation = get_object_or_404(Reservation, reservation_id=reservation_id, customer_id=request.session.get('user_id'))

    if request.method == 'POST':
        # Update the reservation with the submitted data
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()  # Save the updated reservation
            messages.success(request, "Reservation updated successfully.")
            return redirect('reservation_detail', reservation_id=reservation_id)
        else:
            # Add an error message if form validation fails
            messages.error(request, "There was an error updating your reservation. Please check the form.")
    else:
        # Pre-fill the form with existing reservation data
        form = ReservationForm(instance=reservation)

    # Render the template with the form and reservation details
    return render(request, 'reservation_detail.html', {'form': form, 'reservation': reservation})

# File download view (if a file is associated with the reservation)
def download_file(request, reservation_id, file_type):
    # Use 'reservation_id' instead of 'id' to get the reservation
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)

    if file_type == 'file':
        file_to_download = reservation.file
    elif file_type == 'receipt':
        file_to_download = reservation.receipt
    else:
        raise Http404("Invalid file type requested.")

    if file_to_download:
        response = HttpResponse(file_to_download, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_to_download.name}"'
        return response
    else:
        raise Http404("File not found.")
    
# Ensure the user is logged in
def make_reservation(request):
    if not request.session.get('user_id'):
        messages.error(request, "You must be logged in to make a reservation.")
        return redirect('login')

    if request.method == 'POST':
        form = ReservationForm(request.POST, request.FILES)  # Include request.FILES to handle file uploads
        if form.is_valid():
            reservation = form.save(commit=False)

            # Get customer ID from session and retrieve the UserAccount instance
            user_id = request.session.get('user_id')
            if user_id:
                customer = UserAccount.objects.get(id=user_id)  # Retrieve the UserAccount instance
                reservation.customer = customer  # Assign the instance to reservation.customer
            else:
                messages.error(request, "You must be logged in to make a reservation.")
                return redirect('login')

            reservation.save()
            messages.success(request, "Reservation created successfully.")
            return redirect('customer_dashboard')  # Redirect to the customer dashboard after successful reservation
        else:
            print("Form is invalid", form.errors)  # Debug: Print form errors
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReservationForm()

    # Get the username from the session
    username = request.session.get('username', '')

    return render(request, 'make_reservation.html', {'form': form, 'username': username})

def payment_page(request, reservation_id):
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    
    if request.method == 'POST':
        if 'receipt' in request.FILES:  # Check if receipt is in the uploaded files
            receipt = request.FILES['receipt']
            reservation.receipt = receipt
            reservation.save()  # Save the uploaded file to the model
            messages.success(request, "Receipt uploaded successfully.")
        else:
            messages.error(request, "Please upload a valid receipt.")
    
    return render(request, 'payment_page.html', {'reservation': reservation})

def generate_report_view(request):
    if request.method == 'POST':
        # Get the start and end dates from the form
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date', now().date())

        # Filter reservations within the date range
        reservations = Reservation.objects.filter(date__range=[start_date, end_date])

        # Pass the filtered reservations and date range to the template
        return render(request, 'generate_report.html', {
            'reservations': reservations,
            'start_date': start_date,
            'end_date': end_date,
        })
    
    # If it's a GET request, render the form with default end date (current date)
    return render(request, 'generate_report.html', {
        'default_end_date': now().date(),
        'reservations': None,  # No reservations yet
    })
    
def generate_report(request):
    # Get the date range from the request (or use a default)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', now().date())

    # Filter reservations by the provided date range
    if start_date:
        reservations = Reservation.objects.filter(date__range=[start_date, end_date])
    else:
        reservations = Reservation.objects.all()

    # Create the HttpResponse object with the PDF header
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="business_report.pdf"'

    # Create a PDF document
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Add content to the PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Cybercafe Reservation Business Report")

    p.setFont("Helvetica", 12)
    p.drawString(100, height - 100, f"Report Date Range: {start_date} to {end_date}")
    p.drawString(100, height - 120, f"Generated on: {now().date()}")
    
    total_reservations = reservations.count()
    total_income = sum(r.total_price for r in reservations)
    
    pc_rental_count = reservations.filter(pc_rental__isnull=False).count()
    total_hours = sum(r.duration for r in reservations if r.pc_rental)
    pc_rental_income = sum(r.total_price for r in reservations if r.pc_rental)

    printing_count = reservations.filter(printing_option__isnull=False).count()
    total_pages = sum(r.number_of_pages for r in reservations if r.printing_option)
    printing_income = sum(r.total_price for r in reservations if r.printing_option)

    # Write the report summary
    y_position = height - 150
    p.drawString(100, y_position, f"Total Reservations: {total_reservations}")
    p.drawString(100, y_position - 20, f"Total Income: ${total_income:.2f}")

    y_position -= 60
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y_position, "PC Rentals Summary")
    p.setFont("Helvetica", 12)
    p.drawString(100, y_position - 20, f"Total PC Rentals: {pc_rental_count}")
    p.drawString(100, y_position - 40, f"Total Hours Booked: {total_hours} hours")
    p.drawString(100, y_position - 60, f"Total PC Rental Income: ${pc_rental_income:.2f}")

    y_position -= 100
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y_position, "Printing Services Summary")
    p.setFont("Helvetica", 12)
    p.drawString(100, y_position - 20, f"Total Printing Reservations: {printing_count}")
    p.drawString(100, y_position - 40, f"Total Pages Printed: {total_pages}")
    p.drawString(100, y_position - 60, f"Total Printing Income: ${printing_income:.2f}")

    # Close the PDF object
    p.showPage()
    p.save()

    return response

def download_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter reservations by the date range
    reservations = Reservation.objects.filter(date__range=[start_date, end_date])

    # Prepare report content
    report_content = io.StringIO()
    report_content.write(f"Cybercafe Reservation Business Report\n")
    report_content.write(f"Report Date Range: {start_date} to {end_date}\n")
    report_content.write(f"Generated on: {now().date()}\n\n")
    report_content.write(f"Total Reservations: {reservations.count()}\n\n")

    for reservation in reservations:
        report_content.write(f"Reservation ID: {reservation.reservation_id}\n")
        report_content.write(f"Customer: {reservation.customer.username}\n")
        report_content.write(f"Date: {reservation.date}\n")
        report_content.write(f"Total Price: ${reservation.total_price:.2f}\n")
        report_content.write(f"Payment Status: {reservation.payment_status}\n")
        report_content.write(f"-----------------------------------\n")

    # Create response for downloading the report as a text file
    response = HttpResponse(report_content.getvalue(), content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="business_report_{start_date}_to_{end_date}.txt"'

    return response

def logout_view(request):
    # Log the user out and clear the session
    logout(request)
    # Redirect to the login page (index.html)
    return redirect('login')  # Assuming your login page is named 'login'