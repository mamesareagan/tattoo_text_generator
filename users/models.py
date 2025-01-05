from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    User model that extends AbstractBaseUser and PermissionsMixin.

    Attributes:
        id (UUIDField): Primary key for the user, generated automatically.
        email (EmailField): Unique email address for the user.
        username (CharField): Unique username for the user.
        name (CharField): Full name of the user.
        is_active (BooleanField): Indicates whether the user account is active.
        is_staff (BooleanField): Indicates whether the user has staff privileges.
        date_joined (DateTimeField): Timestamp when the user account was created.

    Methods:
        __str__(): Returns the username of the user.
        get_full_name(): Returns the full name of the user.
        get_short_name(): Returns the username of the user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.username