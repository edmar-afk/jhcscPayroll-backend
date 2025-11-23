from django.contrib import admin
from .models import Payroll, QrCode, PayrollStatus, GovernmentShares


admin.site.register(Payroll)
admin.site.register(QrCode)
admin.site.register(PayrollStatus)
admin.site.register(GovernmentShares)