from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from .models import Payroll
from .serializers import PayrollStatusSerializer, PayrollSerializer, UserSerializer, PayrollStatusReleaseSerializer, GovernmentSharesSerializer, GovernmentShares
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework import status, generics
from rest_framework.response import Response
from .models import Payroll, QrCode, PayrollStatus
from .serializers import QrCodeSerializer
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils import timezone
import pytz
import requests, random, time
from rest_framework import status, views





class PayrollStatusSmsSenderView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, payroll_id):
        print("========================================")
        print(f"📩 Received POST request to /api/send-payroll-sms/{payroll_id}/")
        print(f"➡️ Request data: {request.data}")

        payroll = get_object_or_404(Payroll, id=payroll_id)
        payroll_status = get_object_or_404(PayrollStatus, payroll=payroll)
        user = payroll.staff  # ✅ FIXED: use 'staff' instead of 'user'

        phone_number = user.last_name.strip()  # assuming last_name = mobile number
        print(f"✅ Found Payroll object: {payroll.id}")
        print(f"👤 Associated user: {user.username}")

        random_suffix = random.randint(1000, 9999)
        combined_id = f"{payroll.id}-{random_suffix}"
        current_datetime = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %I:%M %p")

        api_key = 'owia8oEaOkCBpSa9WqzDej8iGmbRvMfFB1qhwJl60de67e6e'
        name = user.first_name or "Employee"

        message = (
            f"Hello {name}, your payroll (ID: {combined_id}) has been updated.\n\n"
            f"💼 HR:\nStatus: {payroll_status.hr_status or 'N/A'}\n"
            f"Reason: {payroll_status.hr_reason or 'N/A'}\n"
            f"Updated: {payroll_status.hr_date_updated or 'N/A'}\n\n"
            f"💰 Budget:\nStatus: {payroll_status.budget_status or 'N/A'}\n"
            f"Reason: {payroll_status.budget_reason or 'N/A'}\n"
            f"Updated: {payroll_status.budget_date_updated or 'N/A'}\n\n"
            f"🏛️ President:\nStatus: {payroll_status.president_status or 'N/A'}\n"
            f"Reason: {payroll_status.president_reason or 'N/A'}\n"
            f"Updated: {payroll_status.president_date_updated or 'N/A'}\n\n"
            f"💵 Cashier:\nStatus: {payroll_status.cashier_status or 'N/A'}\n"
            f"Reason: {payroll_status.cashier_reason or 'N/A'}\n"
            f"Updated: {payroll_status.cashier_date_updated or 'N/A'}\n\n"
            f"📅 Notification sent on: {current_datetime}"
        )

        data = {
            'sims': [330],
            'random_sender': False,
            'mobile_numbers': [f'+63{phone_number[1:]}' if phone_number.startswith('0') else phone_number],
            'type': 'SMS',
            'message': message,
        }

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }

        print("➡️ Sending SMS Request")
        print(f"➡️ Payload: {data}")

        success_count = 0
        fail_count = 0
        fail_reasons = []

        try:
            response = requests.post(
                'https://smsgateway.rbsoft.org/api/v1/messages/send',
                json=data, headers=headers, timeout=10
            )
            print(f"✅ Response Status: {response.status_code}")
            print(f"✅ Response Text: {response.text}")

            if response.status_code in [200, 201]:
                success_count += 1
                print("🎉 SMS successfully sent!")
            else:
                fail_count += 1
                fail_reasons.append(response.text)
        except Exception as e:
            fail_count += 1
            fail_reasons.append({'error': str(e)})
            print(f"💥 Exception: {e}")

        time.sleep(1)
        print("========================================")

        return Response(
            {
                'payroll_id': combined_id,
                'sent_to': phone_number,
                'message': message,
                'success_count': success_count,
                'fail_count': fail_count,
                'fail_reasons': fail_reasons,
            },
            status=status.HTTP_200_OK if success_count > 0 else status.HTTP_400_BAD_REQUEST
        )




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    permission_classes = [AllowAny]

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['id'] = user.id  # ✅ include user id in token
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
        data['id'] = self.user.id  # ✅ include id in response
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


class PayrollByStaffView(generics.ListAPIView):
    serializer_class = PayrollSerializer

    def get_queryset(self):
        staff_id = self.kwargs['staff_id']
        return Payroll.objects.filter(staff_id=staff_id)
    

class QrCodeView(View):
    def get(self, request, payroll_id):
        qr_obj = get_object_or_404(QrCode, payroll_id=payroll_id)
        if not qr_obj.qr:
            raise Http404("QR Code not found")

        response = HttpResponse(qr_obj.qr, content_type="image/png")
        response['Content-Disposition'] = 'inline; filename="qr.png"'
        return response
    
    
class GovernmentSharesView(generics.GenericAPIView):
    serializer_class = GovernmentSharesSerializer

    def get_queryset(self):
        payroll_id = self.kwargs['payroll_id']
        return GovernmentShares.objects.filter(payroll_id=payroll_id)

    def get(self, request, payroll_id):
        shares = self.get_queryset().first()
        if not shares:
            return Response({'detail': 'Government shares not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(shares)
        return Response(serializer.data)

    def post(self, request, payroll_id):
        try:
            payroll = Payroll.objects.get(id=payroll_id)
        except Payroll.DoesNotExist:
            return Response({'detail': 'Payroll not found.'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        data['payroll'] = payroll.id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(payroll=payroll)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, payroll_id):
        shares = self.get_queryset().first()
        if not shares:
            return Response({'detail': 'Government shares not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(shares, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    

class PayrollDeleteView(APIView):
    def delete(self, request, payroll_id):
        try:
            payroll = Payroll.objects.get(id=payroll_id)
            payroll.delete()
            return Response({"message": "Payroll deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Payroll.DoesNotExist:
            return Response({"error": "Payroll not found."}, status=status.HTTP_404_NOT_FOUND)
    
    
    
    
    
    
    
    
    
def format_datetime():
    manila_tz = pytz.timezone('Asia/Manila')
    dt = timezone.now().astimezone(manila_tz)
    formatted = dt.strftime('%b. %d, %Y, %I:%M%p')
    formatted = formatted.replace(' 0', ' ').lower()
    return formatted
 
    
class UpdateHRStatusView(APIView):
    def put(self, request, payroll_id):
        payroll_status, _ = PayrollStatus.objects.get_or_create(payroll_id=payroll_id)
        payroll_status.hr_status = request.data.get('hr_status', payroll_status.hr_status)
        payroll_status.hr_reason = request.data.get('hr_reason', payroll_status.hr_reason)
        payroll_status.hr_date_updated = format_datetime()
        payroll_status.save()
        serializer = PayrollStatusSerializer(payroll_status)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateBudgetStatusView(APIView):
    def put(self, request, payroll_id):
        payroll_status, _ = PayrollStatus.objects.get_or_create(payroll_id=payroll_id)
        payroll_status.budget_status = request.data.get('budget_status', payroll_status.budget_status)
        payroll_status.budget_reason = request.data.get('budget_reason', payroll_status.budget_reason)
        payroll_status.budget_date_updated = format_datetime()
        payroll_status.save()
        serializer = PayrollStatusSerializer(payroll_status)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdatePresidentStatusView(APIView):
    def put(self, request, payroll_id):
        payroll_status, _ = PayrollStatus.objects.get_or_create(payroll_id=payroll_id)
        payroll_status.president_status = request.data.get('president_status', payroll_status.president_status)
        payroll_status.president_reason = request.data.get('president_reason', payroll_status.president_reason)
        payroll_status.president_date_updated = format_datetime()
        payroll_status.save()
        serializer = PayrollStatusSerializer(payroll_status)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateCashierStatusView(APIView):
    def put(self, request, payroll_id):
        payroll_status, _ = PayrollStatus.objects.get_or_create(payroll_id=payroll_id)
        payroll_status.cashier_status = request.data.get('cashier_status', payroll_status.cashier_status)
        payroll_status.cashier_reason = request.data.get('cashier_reason', payroll_status.cashier_reason)
        payroll_status.cashier_date_updated = format_datetime()
        payroll_status.save()
        serializer = PayrollStatusSerializer(payroll_status)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PayrollStatusDetailView(APIView):
    def get(self, request, payroll_id):
        try:
            payroll_status = PayrollStatus.objects.get(payroll_id=payroll_id)
        except PayrollStatus.DoesNotExist:
            return Response({'error': 'PayrollStatus not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PayrollStatusSerializer(payroll_status)
        return Response(serializer.data, status=status.HTTP_200_OK)








class CheckQrCodeView(APIView):
    def get(self, request, payroll_id):
        try:
            qr_code = QrCode.objects.get(payroll_id=payroll_id)
            serializer = QrCodeSerializer(qr_code)
            return Response({
                "has_qr": True,
                "qr_data": serializer.data
            }, status=status.HTTP_200_OK)
        except QrCode.DoesNotExist:
            return Response({
                "has_qr": False,
                "message": "No QR code found for this payroll."
            }, status=status.HTTP_200_OK)