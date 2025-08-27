from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from .models import Payroll
from .serializers import PayrollSerializer, UserSerializer, PayrollStatusReleaseSerializer
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework import status, generics
from rest_framework.response import Response
from .models import Payroll, QrCode
from .serializers import QrCodeSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    permission_classes = [AllowAny]

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # add custom fields in response body
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['is_staff'] = self.user.is_staff
        data['is_superuser'] = self.user.is_superuser

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print("Incoming request data:", request.data)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)  # 👈 print the real reason
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        print("Validated data:", serializer.validated_data)
        user = serializer.save()
        return Response({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }, status=status.HTTP_201_CREATED)



class PayrollCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PayrollSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacultyStaffListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.filter(is_staff=False, is_superuser=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PayrollListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer


class QrCodeGenerateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = QrCodeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payroll_id = serializer.validated_data['payroll_id']
        try:
            payroll = Payroll.objects.get(id=payroll_id)
        except Payroll.DoesNotExist:
            return Response({'error': 'Payroll not found'}, status=status.HTTP_404_NOT_FOUND)

        # Generate QR code (example: encode payroll_no & total_amount_due)
        qr_data = f"Payroll ID: {payroll.id}, Payroll No: {payroll.payroll_no}, Amount Due: {payroll.total_amount_due}"
        qr_img = qrcode.make(qr_data)

        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        file_name = f"payroll_{payroll.id}_qr.png"
        qr_file = ContentFile(buffer.getvalue(), name=file_name)

        qr_instance, created = QrCode.objects.get_or_create(payroll=payroll)
        qr_instance.qr.save(file_name, qr_file, save=True)

        response_serializer = QrCodeSerializer(qr_instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PayrollDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer



class PayrollOnlyUpdateView(generics.UpdateAPIView):
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        print("📌 Incoming update data:", request.data)  # debug print
        kwargs['partial'] = True  # allow partial updates
        return super().update(request, *args, **kwargs)
    
    
class PayrollStatusReleaseUpdateView(generics.UpdateAPIView):
    queryset = Payroll.objects.all()
    serializer_class = PayrollStatusReleaseSerializer
    lookup_field = 'id'
    


class PayrollListView(generics.ListAPIView):
    queryset = Payroll.objects.all().order_by('-date_release')
    serializer_class = PayrollSerializer


class PayrollStaffStatusView(generics.ListAPIView):
    serializer_class = PayrollSerializer

    def get_queryset(self):
        staff_id = self.kwargs.get("staff_id")
        return Payroll.objects.filter(staff_id=staff_id).order_by("-date_prepared")
