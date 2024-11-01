from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import *
import requests
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .utils import Manage_S3_Media  

class ActivateUserView(APIView):
    """
    This view handles the user account activation by sending a request 
    to Djoser's activation endpoint with the uid and token.
    """
    permission_classes = [AllowAny] 
    def get(self, request, uid, token):
        activation_url = "http://localhost:8000/auth/users/activation/"
        data = {
            'uid': uid,
            'token': token}
        try:
            response = requests.post(activation_url, json=data, timeout=10)
            response.raise_for_status()  # Raises an exception for 4xx or 5xx HTTP errors
        except requests.exceptions.RequestException as e:
            return Response({"detail": "Error activating the user. Please try again later."},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({"detail": "User activated successfully."},status=status.HTTP_200_OK)
        return Response(
            {
                'detail': 'Activation failed. Please check the activation link or contact support.',
                'errors': response.json()},status=response.status_code)

class PasswordResetConfirmView(APIView):
    """
    This view handles the password reset confirmation by sending a request 
    to Djoser's password reset confirmation endpoint with the uid, token, and new password.
    """
    permission_classes = [AllowAny]

    def post(self, request, uid, token):
        # Get new passwords from request data
        new_password = request.data.get("new_password")
        re_new_password = request.data.get("re_new_password")
        if new_password != re_new_password:
            return Response(
                {"detail": "New passwords do not match."},status=status.HTTP_400_BAD_REQUEST)
        
        reset_confirm_url = "http://localhost:8000/auth/users/reset_password_confirm/"
        data = {
            'uid': uid,
            'token': token,
            'new_password': new_password,
            're_new_password': re_new_password
        }
        try:
            response = requests.post(reset_confirm_url, json=data, timeout=10)
            response.raise_for_status()  # Raises an exception for 4xx or 5xx HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")  # You may want to log this instead of print in production
            return Response(
                {"detail": "Error resetting the password. Please try again later."},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response(
                {"detail": "Password reset successfully."},status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'detail': 'Password reset failed. Please check the reset link or contact support.',
                    'errors': response.json()  # Include Djoser response errors if available
                },status=response.status_code)

class UserPhotoDeleteView(APIView):
    def delete(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        photo_type = request.data.get("photo_type")
        if photo_type not in ["personal_photo", "national_id_photo", "licence_photo"]:
            return Response({"error": "Invalid photo type."}, status=status.HTTP_400_BAD_REQUEST)
        file_field = getattr(user, photo_type, None)
        if not file_field or not file_field.name:
            return Response({"error": f"The {photo_type} for this User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        file_name = file_field.name
        try:
            Manage_S3_Media(file_name,'delete')
        except Exception as e:
            return Response({"error": f"Failed to delete file from S3: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        setattr(user, photo_type, None)
        user.save()

        return Response({"message": f"{photo_type} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class UserPhotoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user = request.user
        photo_fields = ['personal_photo', 'national_id_photo', 'licence_photo']
        empty_fields = [field for field in photo_fields if not getattr(user, field)]
        populated_fields = [field for field in photo_fields if getattr(user, field)]
        data_to_upload = {field: request.data[field] for field in empty_fields if field in request.data}
        if not data_to_upload:
            return Response(
                {"error": "All photo fields are already populated. Please delete existing photos before uploading new ones."},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = UserPhotoUploadSerializer(user, data=data_to_upload, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": f"Photos uploaded successfully for fields: {', '.join(data_to_upload.keys())}.",
                 "skipped": f"Already populated fields: {', '.join(populated_fields)}."},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveAPIView):
    queryset = XrideUser.objects.all()
    serializer_class = FullUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # Return the current authenticated user