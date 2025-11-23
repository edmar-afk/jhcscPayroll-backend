# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Payroll, QrCode, GovernmentShares, PayrollStatus


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name", 'is_staff', 'is_superuser')
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],  # here username = email
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )
        user.set_password(validated_data["password"])  # 🔑 hash password
        user.save()
        return user



class PayrollSerializer(serializers.ModelSerializer):
    staff = UserSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source="staff"
    )

    class Meta:
        model = Payroll
        fields = [
            "id",
            "staff",
            "staff_id",
            "salary",
            'pera_aca',
            'monthly_income',
            "date_release",
            "deductions",
            "gsis_personal_share",
            "gsis_consolidated_loan",
            "gsis_mpl",
            "gsis_educ",
            "gsis_emergency",
            "phic",
            "hdmf_personal_share",
            "hdmf_salary_load",
            "ffasa",
            "valley_bank_load",
            "hdmf_mpl",
            "bir",
            "total_deductions",
            "net_monthly_income",
            "date",
            "ldaap_ada_no",
            "status",
        ]



class QrCodeSerializer(serializers.ModelSerializer):
    payroll_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = QrCode
        fields = ['id', 'payroll_id', 'qr']
        read_only_fields = ['qr']
        
        
class PayrollStatusReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = ['status', 'date_release']
        


class GovernmentSharesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernmentShares
        fields = ['id', 'payroll', 'sss', 'gsis']
        
        
class PayrollStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollStatus
        fields = '__all__'