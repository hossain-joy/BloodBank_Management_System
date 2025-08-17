from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm # Django's login form
from django.contrib import messages # Import messages for user feedback

# Import all necessary forms and models
from .forms import (
    UserRegistrationForm,
    DonorRegistrationForm,
    RequesterRegistrationForm,
    DonorForm,
    RequesterForm
)
from .models import Profile, Donor, Requester, User, Notification, DonationRequest # Ensure DonationRequest is imported

# --- Decorators for Role-Based Access ---

def admin_required(view_func):
    """
    Decorator to ensure the user is logged in and has the 'admin' role.
    """
    @login_required(login_url='login') # Use generic login URL, role specified in URL pattern
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
            messages.error(request, "You do not have permission to access this page.")
            return redirect('home') # Redirect unauthorized users to home or a 403 page
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def donor_required(view_func):
    """
    Decorator to ensure the user is logged in and has the 'donor' role.
    """
    @login_required(login_url='login') # Use generic login URL, role specified in URL pattern
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'donor':
            messages.error(request, "You do not have permission to access this page.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def requester_required(view_func):
    """
    Decorator to ensure the user is logged in and has the 'requester' role.
    """
    @login_required(login_url='login') # Use generic login URL, role specified in URL pattern
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'requester':
            messages.error(request, "You do not have permission to access this page.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# --- General Views ---

def home_view(request):
    """
    Displays the main landing page with role choices.
    """
    return render(request, 'main/home.html')

# --- Authentication Views ---

def register_view(request, role):
    """
    Handles user registration for 'donor' or 'requester' roles.
    Admins are typically created via Django's admin panel.
    """
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        
        profile_form = None
        if role == 'donor':
            profile_form = DonorRegistrationForm(request.POST)
        elif role == 'requester':
            profile_form = RequesterRegistrationForm(request.POST)
        else: # For admin, we assume creation via the admin panel
            messages.error(request, "Invalid registration role.")
            return redirect('home')

        if user_form.is_valid() and profile_form and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            Profile.objects.create(user=user, role=role) # Create the user's role profile

            profile = profile_form.save(commit=False)
            profile.user = user # Link the donor/requester profile to the new user account
            profile.save()

            login(request, user)
            messages.success(request, f"Registration successful! Welcome, {user.username}.")
            return redirect('dashboard') # Redirect to the new unified dashboard
        else:
            messages.error(request, "Please correct the errors below.")
            # If forms are invalid, they will be rendered with errors
            
    else: # GET request
        user_form = UserRegistrationForm()
        profile_form = None
        if role == 'donor':
            profile_form = DonorRegistrationForm()
        elif role == 'requester':
            profile_form = RequesterRegistrationForm()
        else:
            messages.error(request, "Invalid role for registration.")
            return redirect('home')

    return render(request, 'main/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'role': role
    })

def login_view(request, role):
    """
    Handles user login using Django's AuthenticationForm,
    checking if the user's profile role matches the requested role.
    """
    if request.user.is_authenticated:
        # If already logged in, redirect to dashboard.
        # Consider checking if the role matches, otherwise, allow logging out first.
        messages.info(request, "You are already logged in.")
        return redirect('dashboard') 

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if the user has a profile and if the role matches
                if hasattr(user, 'profile') and user.profile.role == role:
                    login(request, user)
                    messages.success(request, f"Logged in as {user.username} ({role.capitalize()}).")
                    return redirect('dashboard')
                else:
                    messages.error(request, f"Invalid credentials or incorrect role for {role.capitalize()}.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password. Please check your credentials.")
    else: # GET request
        form = AuthenticationForm()
        
    return render(request, 'main/login.html', {'form': form, 'role': role})

@login_required # Requires user to be logged in
def logout_view(request):
    """
    Logs out the current user and redirects to the home page.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

# --- Dashboard and Overview ---

@login_required # This decorator ensures only logged-in users can access it
def dashboard(request):
    """
    Displays the dashboard based on the user's role.
    """
    role = request.user.profile.role if hasattr(request.user, 'profile') else 'unknown'

    if role == 'admin':
        # Your existing dashboard logic for admin
        donors = Donor.objects.all()
        requesters = Requester.objects.all()
        
        total_donors = donors.count()
        total_requests = requesters.count()
        
        # Count donors by blood group
        blood_group_counts = Donor.objects.values('blood_group').annotate(count=Count('blood_group')).order_by('-count')

        context = {
            'donors': donors,
            'requesters': requesters,
            'total_donors': total_donors,
            'total_requests': total_requests,
            'blood_group_counts': blood_group_counts,
            'user_role': role
        }
        return render(request, 'main/admin_dashboard.html', context) # Adjusted template name for clarity
        
    elif role == 'donor':
        donor_profile = get_object_or_404(Donor, user=request.user)

        # Fetch all donation requests for this donor, newest first
        # Assuming related_name='donation_requests' on DonationRequest model's donor field
        donation_requests = donor_profile.donation_requests.filter(status='pending').order_by('-timestamp')
        
        context = {
            'donor': donor_profile,
            'requests': donation_requests,
            'user_role': role
        }
        return render(request, 'main/donor_dashboard.html', context) # Adjusted template name
        
    elif role == 'requester':
        # Now we fetch a LIST of requests, not just one profile
        user_requests = Requester.objects.filter(user=request.user).order_by('-date_needed')
        # Fetch notifications for all requests made by this user
        notifications = Notification.objects.filter(requester__in=user_requests).order_by('-timestamp')
        
        context = {
            'requests': user_requests, # Changed from 'requester' to 'requests'
            'notifications': notifications,
            'user_role': role
        }
        return render(request, 'main/requester_dashboard.html', context) # Adjusted template name
    else:
        messages.warning(request, "Your account does not have an assigned role. Please contact support.")
        logout(request) # Log out users with no valid role to prevent issues
        return redirect('home')

# --- Donor Management Views (Admin-only for add/delete) ---

@admin_required
def add_donor(request):
    """
    Handles adding a new donor.
    Requires admin authentication. Processes DonorForm.
    Note: This is for adding a Donor record that may or may not have a User linked yet.
    For full registration with user, use register_view with 'donor' role.
    """
    form = DonorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save() # Save the new donor to the database
        messages.success(request, "Donor added successfully.")
        return redirect('dashboard') # Redirect to dashboard after successful addition
    return render(request, 'main/add_donor.html', {'form': form})

@login_required # Now allows self-editing or admin editing
def edit_donor(request, pk):
    """
    Handles editing an existing donor.
    Allows access for Admins or the Donor themself.
    """
    donor = get_object_or_404(Donor, pk=pk)

    # SECURITY CHECK: Allow access if the user is an admin OR if the user owns this profile.
    if not (request.user.profile.role == 'admin' or request.user == donor.user):
        messages.error(request, "You do not have permission to access this page.")
        return redirect('dashboard') # or redirect('home')

    if request.method == 'POST':
        form = DonorForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, "Donor updated successfully.")
            return redirect('dashboard') # Redirect to their dashboard after a successful edit
    else:
        form = DonorForm(instance=donor)

    return render(request, 'main/edit_profile.html', { # Use generic edit_profile template
        'form': form,
        'role': 'donor' # Pass the role to the template for dynamic titles
    })

@admin_required
def delete_donor(request, pk):
    """
    Handles deleting a donor.
    Requires admin authentication. Shows a confirmation page on GET, deletes on POST.
    """
    donor = get_object_or_404(Donor, pk=pk) # Get donor object or raise 404
    
    if request.method == 'POST':
        # If the donor is linked to a user, consider deleting the user as well,
        # or handling the user account appropriately.
        # For simplicity, if linked, Cascade delete in models will handle User profile.
        donor.delete() # Delete the donor from the database
        messages.success(request, "Donor deleted successfully.")
        return redirect('dashboard') # Redirect back to the dashboard
    
    # On GET request, show a confirmation page before deleting
    return render(request, 'main/delete_donor_confirm.html', {'donor': donor})

# --- Requester Management Views (Admin-only for add) ---

@admin_required
def add_requester(request):
    """
    Handles adding a new blood request.
    Requires admin authentication. Processes RequesterForm.
    Note: Similar to add_donor, this is for adding a Requester record.
    For full registration with user, use register_view with 'requester' role.
    """
    form = RequesterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save() # Save the new request to the database
        messages.success(request, "Requester added successfully.")
        return redirect('dashboard') # Redirect to dashboard after successful addition
    return render(request, 'main/add_requester.html', {'form': form})

@login_required
def create_request_view(request):
    """
    Allows a logged-in requester to create a new blood request.
    """
    if request.user.profile.role != 'requester':
        messages.error(request, "You must be a requester to create a blood request.")
        return redirect('dashboard') # Redirect if user is not a requester

    if request.method == 'POST':
        form = RequesterForm(request.POST)
        if form.is_valid():
            # Associate the request with the logged-in user before saving
            new_request = form.save(commit=False)
            new_request.user = request.user
            new_request.save()
            messages.success(request, "Your blood request has been created successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RequesterForm()

    return render(request, 'main/create_request.html', {'form': form})

@login_required
def edit_requester(request, pk):
    """
    Handles editing an existing blood request.
    Allows access for Admins or the Requester themself.
    """
    requester = get_object_or_404(Requester, pk=pk)

    # SECURITY CHECK: Allow access if the user is an admin OR if the user owns this profile.
    if not (request.user.profile.role == 'admin' or request.user == requester.user):
        messages.error(request, "You do not have permission to access this page.")
        return redirect('dashboard') # or redirect('home')

    if request.method == 'POST':
        form = RequesterForm(request.POST, instance=requester)
        if form.is_valid():
            form.save()
            messages.success(request, "Requester updated successfully.")
            return redirect('dashboard') # Redirect to their dashboard after a successful edit
    else:
        form = RequesterForm(instance=requester)
        
    return render(request, 'main/edit_profile.html', { # Use generic edit_profile template
        'form': form,
        'role': 'requester' # Pass the role to the template
    })

@login_required # Changed from admin_required to login_required for broader access
def delete_requester(request, pk):
    """
    Handles deleting a blood request.
    Allows access for Admins or the Requester who owns the request.
    """
    requester_request = get_object_or_404(Requester, pk=pk)
    
    # SECURITY CHECK: Allow access only if user is an admin or the owner
    if not (request.user.profile.role == 'admin' or request.user == requester_request.user):
        messages.error(request, "You do not have permission to delete this request.")
        return redirect('dashboard') # or redirect('home')

    if request.method == 'POST':
        requester_request.delete()
        messages.success(request, "Blood request deleted successfully.")
        return redirect('dashboard')
        
    return render(request, 'main/delete_requester_confirm.html', {'request': requester_request})

# --- Search and Communication Views (Admin-only access for these, based on previous structure) ---

@admin_required
def search_blood(request):
    """
    Handles searching for donors by blood group.
    Filters donors based on a query parameter.
    """
    query = request.GET.get('q') # Get the search query from URL parameters
    donors = [] # Initialize donors list
    if query:
        # Filter donors where blood_group is exactly the query (case-insensitive)
        donors = Donor.objects.filter(blood_group__iexact=query) 
    return render(request, 'main/search.html', {'donors': donors, 'query': query})

@admin_required
def find_donors_for_requester(request, requester_id):
    """
    Finds and displays a list of matching donors for a specific requester.
    """
    requester = get_object_or_404(Requester, pk=requester_id)
    
    # Find donors with the same blood group
    matching_donors = Donor.objects.filter(blood_group=requester.blood_group)
    
    return render(request, 'main/find_donors.html', {
        'requester': requester,
        'donors': matching_donors
    })

@admin_required
def send_request_to_donor(request, donor_id, requester_id):
    """
    Sends a blood donation request to a specific donor via email
    AND creates an on-site request (DonationRequest object).
    """
    donor = get_object_or_404(Donor, pk=donor_id)
    requester = get_object_or_404(Requester, pk=requester_id)

    # Pre-populate the message for the admin
    message_body = (
        f"Dear {donor.name},\n\n"
        f"There is an urgent need for your blood type ({donor.blood_group}) for a patient named {requester.name}. "
        f"Please consider donating blood to save a life.\n\n"
        f"Requester's Location: {requester.location}\n"
        f"Date Needed: {requester.date_needed}\n\n"
        f"Thank you for your consideration.\n\n"
        f"Best regards,\n"
        f"Blood Bank Administration"
    )
    
    if request.method == 'POST':
        # Create the on-site donation request
        DonationRequest.objects.create(
            donor=donor,
            requester=requester,
            message=request.POST.get('message', message_body) # Use posted message if available, else default
        )
        messages.success(request, "On-site donation request created successfully.")

        # Get donor's email from the linked User model
        recipient_email = donor.user.email if donor.user and donor.user.email else None
        
        if recipient_email:
            try:
                send_mail(
                    f"Urgent Blood Donation Request for {requester.name}", # Subject
                    request.POST.get('message', message_body), # Use posted message if available, else default
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],  # Send to the donor's email address
                    fail_silently=False,
                )
            except Exception as e:
                messages.error(request, f"Failed to send email request: {e}")
                print(f"Error sending email to donor: {e}") # For debugging
        else:
            messages.warning(request, "Donor does not have a valid email address linked to their account. Email notification not sent.")
            
        return redirect('dashboard')

    return render(request, 'main/send_request_to_donor.html', {
        'donor': donor,
        'requester': requester,
        'message_body': message_body
    })

@admin_required
def send_donor_details_to_requester(request, requester_id, donor_id):
    """
    Sends donor's contact details to the requester via email AND
    creates an on-site notification.
    """
    requester = get_object_or_404(Requester, pk=requester_id)
    donor = get_object_or_404(Donor, pk=donor_id)

    # Pre-populate the message for the admin
    message_body = (
        f"Dear {requester.name},\n\n"
        f"We have found a potential blood donor for you. Here are their details:\n\n"
        f"Donor's Name: {donor.name}\n"
        f"Blood Group: {donor.blood_group}\n"
        f"Phone Number: {donor.phone}\n\n" # Assuming phone number is directly on Donor model
        f"Please contact them to coordinate the donation. We wish you the best.\n\n"
        f"Best regards,\n"
        f"Blood Bank Administration"
    )

    if request.method == 'POST':
        # Create the on-site notification
        Notification.objects.create(
            requester=requester,
            donor=donor,
            message=message_body # Use the pre-populated message
        )
        messages.success(request, "On-site notification created successfully.")

        # Email sending logic
        subject = f"Donor Information for Your Blood Request"
        recipient_email = requester.user.email if requester.user and requester.user.email else None
        
        if recipient_email:
            try:
                send_mail(
                    subject,
                    message_body, # Use the pre-populated message body
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],  # Send to the requester's email address
                    fail_silently=False,
                )
                messages.success(request, "Donor details sent successfully to the requester via email.")
            except Exception as e:
                messages.error(request, f"Failed to send donor details email: {e}")
                print(f"Error sending email to requester: {e}") # For debugging
        else:
            messages.warning(request, "Requester does not have a valid email address linked to their account. Email notification not sent.")
            
        return redirect('dashboard')

    # On GET request, render the form
    return render(request, 'main/send_donor_details_to_requester.html', {
        'requester': requester,
        'donor': donor,
        'message_body': message_body
    })

# --- New views for handling donation requests from Code2 ---

@login_required
def accept_request_view(request, request_id):
    """
    Marks a donation request as 'accepted' and notifies the requester.
    """
    donation_request = get_object_or_404(DonationRequest, pk=request_id)

    # Security Check: Ensure the logged-in user is the intended donor
    if request.user != donation_request.donor.user:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('dashboard')

    # Update the status
    donation_request.status = 'accepted'
    donation_request.save()

    # Create a notification for the requester with the donor's details
    message_to_requester = (
        f"Great news! Donor {donation_request.donor.name} has accepted your request. "
        f"You can contact them using the details below to coordinate:\n\n"
        f"Phone: {donation_request.donor.phone}"
    )
    Notification.objects.create(
        requester=donation_request.requester,
        donor=donation_request.donor,
        message=message_to_requester
    )

    messages.success(request, "Request accepted! The requester has been notified with your contact details.")
    return redirect('dashboard')


@login_required
def reject_request_view(request, request_id):
    """
    Marks a donation request as 'rejected'.
    """
    donation_request = get_object_or_404(DonationRequest, pk=request_id)

    # Security Check: Ensure the logged-in user is the intended donor
    if request.user != donation_request.donor.user:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('dashboard')

    # Update the status
    donation_request.status = 'rejected'
    donation_request.save()
    
    messages.info(request, "You have rejected the donation request.")
    return redirect('dashboard')