from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, password_validation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'name', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    def validate_password(self, value):
        try:
            password_validation.validate_password(value, self.instance)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user
    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid login credentials")
        
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        update_last_login(None, user)
        
        return {
            'email': user.email,
            'token': token,
            'refresh': str(refresh)
        }    