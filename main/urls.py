from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication URLs ---
    path('', views.home_view, name='home'),
    path('login/<str:role>/', views.login_view, name='login'),
    path('register/<str:role>/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # --- Dashboard URL ---
    path('dashboard/', views.dashboard, name='dashboard'),

    # --- Donor Management URLs ---
    path('add-donor/', views.add_donor, name='add_donor'),
    path('edit-donor/<int:pk>/', views.edit_donor, name='edit_donor'),
    path('delete-donor/<int:pk>/', views.delete_donor, name='delete_donor'),

    # --- Requester Management URLs ---
    path('add-requester/', views.add_requester, name='add_requester'), # For Admin to add requests
    path('create-request/', views.create_request_view, name='create_request'), # For Requesters to create their own requests
    path('requester/edit/<int:pk>/', views.edit_requester, name='edit_requester'),
    path('delete-requester/<int:pk>/', views.delete_requester, name='delete_requester'),

    # --- Search and Communication URLs ---
    path('search/', views.search_blood, name='search_blood'),
    path('requester/<int:requester_id>/find-donors/', views.find_donors_for_requester, name='find_donors'),
    path('send-request/donor/<int:donor_id>/requester/<int:requester_id>/', views.send_request_to_donor, name='send_request_to_donor'),
    path('send-details/requester/<int:requester_id>/donor/<int:donor_id>/', views.send_donor_details_to_requester, name='send_donor_details_to_requester'),

    # --- Donation Request Actions ---
    path('request/<int:request_id>/accept/', views.accept_request_view, name='accept_request'),
    path('request/<int:request_id>/reject/', views.reject_request_view, name='reject_request'),
]