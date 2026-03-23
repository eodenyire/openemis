from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer

# Web Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        serializer = LoginSerializer(data={'username': username, 'password': password})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # Redirect based on user type
            if user.user_type == 'admin':
                return redirect('admin_dashboard')
            elif user.user_type == 'teacher':
                return redirect('teacher_dashboard')
            elif user.user_type == 'student':
                return redirect('student_dashboard')
            elif user.user_type == 'parent':
                return redirect('parent_dashboard')
            elif user.user_type == 'librarian':
                return redirect('librarian_dashboard')
            elif user.user_type == 'accountant':
                return redirect('accountant_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'accounts/login.html')

@login_required
def dashboard_view(request):
    user_type = request.user.user_type
    template_name = f'accounts/{user_type}_dashboard.html'
    return render(request, template_name, {'user': request.user})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# API Views
@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user