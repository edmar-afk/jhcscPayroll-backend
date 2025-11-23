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
    path('qr/<int:payroll_id>/', views.QrCodeView.as_view(), name='qr-code'),
    
    path("payrolls/<int:id>/update/", views.PayrollOnlyUpdateView.as_view(), name="payroll-only-update"),
    path('payrolls/', views.PayrollListView.as_view(), name='payroll-list'),
    path('payroll/<int:id>/update-status-release/', views.PayrollStatusReleaseUpdateView.as_view(), name='payroll-update-status-release'),
    
    path("payroll/staff/<int:staff_id>/", views.PayrollStaffStatusView.as_view(), name="payroll-staff-status"),
    path('payroll-details/staff/<int:staff_id>/', views.PayrollByStaffView.as_view(), name='payroll-by-staff'),
    path('payroll/<int:payroll_id>/government-shares/', views.GovernmentSharesView.as_view(), name='government-shares'),
    
    
    path('payroll/<int:payroll_id>/update/hr/', views.UpdateHRStatusView.as_view(), name='update_hr_status'),
    path('payroll/<int:payroll_id>/update/budget/', views.UpdateBudgetStatusView.as_view(), name='update_budget_status'),
    path('payroll/<int:payroll_id>/update/president/', views.UpdatePresidentStatusView.as_view(), name='update_president_status'),
    path('payroll/<int:payroll_id>/update/cashier/', views.UpdateCashierStatusView.as_view(), name='update_cashier_status'),
    
    path('payroll/<int:payroll_id>/status/', views.PayrollStatusDetailView.as_view()),
    
    
    path('delete-payroll/<int:payroll_id>/', views.PayrollDeleteView.as_view(), name='delete-payroll'),
    path('payroll/<int:payroll_id>/has_qr/', views.CheckQrCodeView.as_view(), name='check_qr_code'),
    
    path('send-payroll-sms/<int:payroll_id>/', views.PayrollStatusSmsSenderView.as_view(), name='send_payroll_sms'),
    
    path('payrolls/<int:pk>/download/', views.download_payroll_pdf, name='download-payroll'),

]
