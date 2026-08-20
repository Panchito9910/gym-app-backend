"""Serializers for users."""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Role, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'status', 'created', 'updated']
        read_only_fields = ['id', 'created', 'updated']


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(source='idRole', read_only=True)
    roleId = serializers.PrimaryKeyRelatedField(
        source='idRole',
        queryset=Role.objects.filter(status=True),
        write_only=True,
        required=False,
    )
    fullName = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'firstName',
            'lastName',
            'fullName',
            'userName',
            'email',
            'status',
            'lastLogin',
            'role',
            'roleId',
            'created',
            'updated',
        ]
        read_only_fields = ['id', 'lastLogin', 'created', 'updated', 'fullName', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password], style={'input_type': 'password'}
    )
    passwordConfirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'userName', 'email', 'password', 'passwordConfirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['passwordConfirm']:
            raise serializers.ValidationError({'passwordConfirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('passwordConfirm')
        password = validated_data.pop('password')
        user_role, _ = Role.objects.get_or_create(name='user', defaults={'description': 'Regular user'})
        user = User.objects.create(idRole=user_role, **validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True, style={'input_type': 'password'})
    newPassword = serializers.CharField(
        write_only=True, required=True, validators=[validate_password], style={'input_type': 'password'}
    )

    def validate_currentPassword(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
