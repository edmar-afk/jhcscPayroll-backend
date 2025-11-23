from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Payroll(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    salary = models.TextField(blank=True, null=True)
    pera_aca = models.TextField(blank=True, null=True)
    monthly_income = models.TextField(blank=True, null=True)
    date_release = models.TextField(blank=True, null=True)
    deductions = models.TextField(blank=True, null=True)
    gsis_personal_share = models.TextField(blank=True, null=True)
    gsis_consolidated_loan = models.TextField(blank=True, null=True)
    gsis_mpl = models.TextField(blank=True, null=True)
    gsis_educ = models.TextField(blank=True, null=True)
    gsis_emergency = models.TextField(blank=True, null=True)
    phic = models.TextField(blank=True, null=True)
    hdmf_personal_share = models.TextField(blank=True, null=True)
    hdmf_salary_load = models.TextField(blank=True, null=True)
    ffasa = models.TextField(blank=True, null=True)
    valley_bank_load = models.TextField(blank=True, null=True)
    hdmf_mpl = models.TextField(blank=True, null=True)
    bir = models.TextField(blank=True, null=True)
    total_deductions = models.TextField(blank=True, null=True)
    net_monthly_income = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    ldaap_ada_no = models.TextField(blank=True, null=True)
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