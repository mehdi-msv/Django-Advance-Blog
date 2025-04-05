from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from .serializers import (RegistrationSerializer, CustomAuthTokenSerializer,
                          ChangePasswordSerializer, ProfileSerializer)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ...models import Profile
from django.shortcuts import get_object_or_404
from .permissions import IsVerified
from django.core.mail import send_mail

class RegistrationAPIView(GenericAPIView):
    serializer_class = RegistrationSerializer
    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                'email': serializer.validated_data['email'],
            }
            return Response(data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    


class CustomObtainAuthToken(ObtainAuthToken):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = CustomAuthTokenSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
             
class DiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
    

class ChangePasswordAPIView(GenericAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data, context={'user': user})

        if serializer.is_valid():
            # Set new password
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()

            return Response({"success": "Password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        obj = get_object_or_404(Profile, user=self.request.user)
        return obj
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Profile updated successfully", "data": serializer.data})

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
class SendmailTest(GenericAPIView):
    def post(self, request, *args, **kwargs):
        send_mail(
            'Test Email',
            'This is a test email.',
            'noreply@example.com',
            ['your_email@example.com'],
            fail_silently=False,
        )
        return Response({"success": "Email sent successfully"}, status=status.HTTP_200_OK)