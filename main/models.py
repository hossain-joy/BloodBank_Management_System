from django.db import models
from django.contrib.auth.models import User # Import Django's User model

# Create a Profile model to store user roles
class Profile(models.Model):
    USER_ROLES = [
        ('admin', 'Admin'),
        ('donor', 'Donor'),
        ('requester', 'Requester'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Link to the User model
    role = models.CharField(max_length=10, choices=USER_ROLES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Donor model
class Donor(models.Model):
    # Link a Donor record to a user account
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ]
    
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.blood_group})"

# Requester model
class Requester(models.Model):
    # Changed from OneToOneField to ForeignKey to allow a user to have multiple requests
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='requests')
    name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=Donor.BLOOD_GROUPS)
    phone = models.CharField(max_length=15)
    reason = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)
    date_needed = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} requested {self.blood_group}"

# Notification model
class Notification(models.Model):
    requester = models.ForeignKey(Requester, on_delete=models.CASCADE, related_name='notifications')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.requester.name} about {self.donor.name}"
    
# DonationRequest model (merged with status field from Code2)
class DonationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donation_requests')
    requester = models.ForeignKey(Requester, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending') # Added from Code2
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Updated __str__ to include status from Code2
        return f"Request to {self.donor.name} for {self.requester.name} ({self.status})"