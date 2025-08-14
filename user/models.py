from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, nama, password=None, **extra_fields):
        if not email:
            raise ValueError('Email harus diisi')
        email = self.normalize_email(email)
        user = self.model(email=email, nama=nama, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nama, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nama, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nama = models.CharField(max_length=50)
    no_hp = models.CharField(max_length=20, unique=True, blank=True, null=True)
    alamat = models.TextField(blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    tgl_bergabung = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=timezone.now)  # gunakan default, bukan auto_now

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nama']
    
    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.email
