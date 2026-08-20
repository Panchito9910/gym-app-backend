"""User and Role models."""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.core.models import BaseModel


class Role(BaseModel):
    """Application role (admin, trainer, user...)."""

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """Manager for email-based authentication."""

    use_in_migrations = True

    def _create_user(self, email, user_name, first_name, last_name, password, **extra):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            userName=user_name,
            firstName=first_name,
            lastName=last_name,
            **extra,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, user_name, first_name, last_name, password=None, **extra):
        extra.setdefault('is_staff', False)
        extra.setdefault('is_superuser', False)
        return self._create_user(email, user_name, first_name, last_name, password, **extra)

    def create_superuser(self, email, user_name, first_name, last_name, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('is_active', True)
        return self._create_user(email, user_name, first_name, last_name, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model."""

    idRole = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        db_column='idRole',
    )
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    userName = models.CharField(max_length=60, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    status = models.BooleanField(default=True)
    lastLogin = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['userName', 'firstName', 'lastName']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['userName']),
        ]

    def __str__(self):
        return self.email

    @property
    def role_name(self) -> str:
        return self.idRole.name if self.idRole_id else ''

    @property
    def is_admin_role(self) -> bool:
        return self.role_name == 'admin'

    @property
    def is_trainer_role(self) -> bool:
        return self.role_name == 'trainer'

    @property
    def is_admin_or_trainer(self) -> bool:
        return self.is_admin_role or self.is_trainer_role

    def get_full_name(self) -> str:
        return f'{self.firstName} {self.lastName}'.strip()
