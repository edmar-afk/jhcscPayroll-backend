from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Payroll(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    payroll_no = models.TextField(blank=True, null=True)
    fixed_rate = models.TextField(blank=True, null=True)
    salary_adjustment = models.TextField(blank=True, null=True)
    salary_after_adjustment = models.TextField(blank=True, null=True)
    overtime_pay = models.TextField(blank=True, null=True)
    total_salary_overtime = models.TextField(blank=True, null=True)
    absent = models.TextField(blank=True, null=True)
    late = models.TextField(blank=True, null=True)
    deductions = models.TextField(blank=True, null=True)
    total_amount_due = models.TextField(blank=True, null=True)
    check_no = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    gross_compensation = models.TextField(blank=True, null=True)
    date_prepared = models.DateField(blank=True, null=True)
    date_release = models.DateField(blank=True, null=True)
    status = models.TextField(default='Pending')


class GovernmentShares(models.Model):
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE)
    sss = models.TextField()
    gsis = models.TextField()


class QrCode(models.Model):
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE)
    qr = models.FileField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png'])]
    )


class PayrollStatus(models.Model):
    payroll = models.ForeignKey('Payroll', on_delete=models.CASCADE)

    hr_status = models.TextField(blank=True, null=True)
    hr_reason = models.TextField(blank=True, null=True)
    hr_date_updated = models.TextField(blank=True, null=True)
    
    budget_status = models.TextField(blank=True, null=True)
    budget_reason = models.TextField(blank=True, null=True)
    budget_date_updated = models.TextField(blank=True, null=True)
    
    president_status = models.TextField(blank=True, null=True)
    president_reason = models.TextField(blank=True, null=True)
    president_date_updated = models.TextField(blank=True, null=True)
    
    cashier_status = models.TextField(blank=True, null=True)
    cashier_reason = models.TextField(blank=True, null=True)
    cashier_date_updated = models.TextField(blank=True, null=True)