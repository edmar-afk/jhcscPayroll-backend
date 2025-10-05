from django.contrib import admin
from .models import Payroll, QrCode


admin.site.register(Payroll)
admin.site.register(QrCode)