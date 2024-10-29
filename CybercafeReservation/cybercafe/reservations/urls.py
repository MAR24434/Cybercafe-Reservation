from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # Login page (index)
    path('signup/', views.signup_view, name='signup'),  # Sign-up page
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('reservation/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservation/<int:reservation_id>/download/<str:file_type>/', views.download_file, name='download_file'),
    path('reservation/make/', views.make_reservation, name='make_reservation'),  # New route for making reservations
    path('manage-account/', views.manage_account_view, name='manage_account'),
    path('account-detail/<int:account_id>/', views.account_detail_view, name='account_detail'),
    path('account/admin/add-account/', views.add_account_view, name='add_account'),
    path('update-account/<int:account_id>/', views.update_account_view, name='update_account'),  # Update view
    path('delete-account/<int:account_id>/', views.delete_account_view, name='delete_account'),
    path('manage-services/', views.manage_services_view, name='manage_services'),
    path('add_pc_rental/', views.add_or_edit_pc_rental_view, name='add_or_edit_pc_rental'),
    path('edit_pc_rental/<int:rental_id>/', views.add_or_edit_pc_rental_view, name='add_or_edit_pc_rental'),
    path('add_printing_option/', views.add_or_edit_printing_option_view, name='add_or_edit_printing_option'),
    path('edit_printing_option/<int:option_id>/', views.add_or_edit_printing_option_view, name='add_or_edit_printing_option'),
    path('delete-pc-rental/<int:rental_id>/', views.delete_pc_rental_view, name='delete_pc_rental'),
    path('delete-printing-option/<int:option_id>/', views.delete_printing_option_view, name='delete_printing_option'),
    path('payment/<int:reservation_id>/', views.payment_page, name='payment_page'),
    path('delete-reservation/<int:reservation_id>/', views.delete_reservation, name='delete_reservation'),
    path('generate_report/', views.generate_report_view, name='generate_report'),
    path('download_report/', views.download_report, name='download_report'),
    path('logout/', views.logout_view, name='logout'),
]
