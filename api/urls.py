from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
# ssd
urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("register/", views.RegisterView.as_view(), name="register"),
    
    path("payroll/create/", views.PayrollCreateView.as_view(), name="payroll-create"),
    path('faculty-staff/', views.FacultyStaffListView.as_view(), name='faculty-staff-list'),
    
    path("payrolls/", views.PayrollListView.as_view(), name="payroll-list"),
    path('payrolls/<int:pk>/', views.PayrollDetailView.as_view(), name='payroll-detail'),
    path('generate-qr/', views.QrCodeGenerateView.as_view(), name='generate-qr'),
    
    path("payrolls/<int:id>/update/", views.PayrollOnlyUpdateView.as_view(), name="payroll-only-update"),
    path('payrolls/', views.PayrollListView.as_view(), name='payroll-list'),
    path('payroll/<int:id>/update-status-release/', views.PayrollStatusReleaseUpdateView.as_view(), name='payroll-update-status-release'),
    
    path("payroll/staff/<int:staff_id>/", views.PayrollStaffStatusView.as_view(), name="payroll-staff-status"),
]
