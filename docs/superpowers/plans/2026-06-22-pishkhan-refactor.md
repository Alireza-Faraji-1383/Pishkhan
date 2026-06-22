# Pishkhan Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor Pishkhan Hotel Reservation API — fix bugs, improve production readiness, enhance code quality, and write a bilingual README.

**Architecture:** Django REST Framework API with JWT auth, Celery + Redis for async tasks, PostgreSQL, and Redis caching. Two apps: `users` and `hotels`. Shared utilities in `core`.

**Tech Stack:** Python 3.13, Django 5.2, DRF 3.16, SimpleJWT, Celery 5.5, Redis 7, PostgreSQL 15, docker-compose.

---

### Task 1: Add .gitignore

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Create `.gitignore`**

Create `E:\projects\Pishkhan\.gitignore` with standard Django entries:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environment
.venv/
venv/
env/

# Django
*.log
db.sqlite3
db.sqlite3-journal
media/

# Environment variables
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Distribution
*.egg-info/
dist/
build/

# Coverage
htmlcov/
.coverage
.coverage.*
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore"
```

---

### Task 2: Remove Unused Dependencies

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Remove unused packages from `requirements.txt`**

Remove these three lines:
```
django-allauth==65.11.0
dj-rest-auth[with_social]==7.0.1
drf-nested-routers==0.93.5
```

Final `requirements.txt`:
```
django==5.2.5
djangorestframework==3.16.1
djangorestframework-simplejwt==5.5.1
django-cors-headers==4.7.0
drf-spectacular==0.28.0
celery==5.5.3
redis==6.4.0
psycopg2-binary==2.9.10
django-redis==6.0.0
django-cacheops==7.2
python-dotenv==1.0.1
gunicorn==23.0.0
```

Note: `python-dotenv` and `gunicorn` are added for production readiness (Task 5 and Task 6).

- [ ] **Step 2: Commit**

```bash
git add requirements.txt
git commit -m "chore: remove unused dependencies, add python-dotenv and gunicorn"
```

---

### Task 3: Fix Bug — RoomTypeAdminViewSet owner TypeError

**Files:**
- Modify: `hotels/views.py:127-128`

- [ ] **Step 1: Fix `perform_create` in `RoomTypeAdminViewSet`**

In `E:\projects\Pishkhan\hotels\views.py`, replace the `perform_create` method (lines 127-128):

**Before:**
```python
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

**After:**
```python
    def perform_create(self, serializer):
        serializer.save()
```

The `RoomType` model has no `owner` field — it belongs to a `Hotel`, which in turn has an `owner`. The `RoomTypeCreateSerializer` already accepts `hotel` as a field, and the `get_queryset` filters by `hotel__owner=self.request.user`, so the permission check is already handled.

- [ ] **Step 2: Commit**

```bash
git add hotels/views.py
git commit -m "fix: remove invalid owner field from RoomTypeAdminViewSet.perform_create"
```

---

### Task 4: Fix Bug — VerificationCode.code unique constraint

**Files:**
- Modify: `users/models.py:35`

- [ ] **Step 1: Remove `unique=True` from `VerificationCode.code`**

In `E:\projects\Pishkhan\users\models.py`, change line 35:

**Before:**
```python
    code = models.CharField(max_length=6, unique=True)
```

**After:**
```python
    code = models.CharField(max_length=6)
```

The validation is already handled in the view/serializer layer — `RequestVerificationCodeView` deletes all previous codes for a user before creating a new one, and `UserRegistrationSerializer` checks for an unused, non-expired code for a specific email. No DB-level uniqueness is needed.

- [ ] **Step 2: Create and run migration**

```bash
python manage.py makemigrations users
python manage.py migrate
```

- [ ] **Step 3: Commit**

```bash
git add users/models.py users/migrations/
git commit -m "fix: remove unique constraint from VerificationCode.code to prevent namespace exhaustion"
```

---

### Task 5: Environment Configuration (settings.py)

**Files:**
- Modify: `config/settings.py`
- Create: `.env.example`

- [ ] **Step 1: Update `config/settings.py` for environment-based configuration**

Replace the top section of `config/settings.py` (lines 1-30) and Redis/CORS sections (lines 166-197).

**Add after line 15 (`BASE_DIR = ...`), before `SECRET_KEY`:**

```python
from dotenv import load_dotenv
load_dotenv()
```

**Replace line 25:**

**Before:**
```python
SECRET_KEY = 'django-insecure-h2_+w%1ge0$j9rnarzy=b*3hdg8-gf&=(j*-i0&78h0ct3(l+h'
```

**After:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-h2_+w%1ge0$j9rnarzy=b*3hdg8-gf&=(j*-i0&78h0ct3(l+h')
```

**Replace line 30:**

**Before:**
```python
ALLOWED_HOSTS = []
```

**After:**
```python
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

**Replace line 128:**

**Before:**
```python
TIME_ZONE = 'UTC'
```

**After:**
```python
TIME_ZONE = 'Asia/Tehran'
```

**Add a Redis helper variable** before the Redis section (around line 177):

```python
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
```

**Replace lines 177-178 (CELERY_BROKER_URL and CELERY_RESULT_BACKEND):**

**Before:**
```python
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
```

**After:**
```python
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:6379/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:6379/0'
```

**Replace lines 185-193 (CACHES):**

**Before:**
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

**After:**
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f'redis://{REDIS_HOST}:6379/1',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

**Replace line 196:**

**Before:**
```python
CACHEOPS_REDIS = "redis://redis:6379/1"
```

**After:**
```python
CACHEOPS_REDIS = f"redis://{REDIS_HOST}:6379/1"
```

- [ ] **Step 2: Create `.env.example`**

Create `E:\projects\Pishkhan\.env.example`:

```env
# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=postgres
DB_USER=postgres
DB_PASS=postgres
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis

# Email (optional - uses console backend by default)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-password
```

- [ ] **Step 3: Commit**

```bash
git add config/settings.py .env.example
git commit -m "feat: add environment-based configuration with dotenv support"
```

---

### Task 6: Docker Improvements

**Files:**
- Modify: `docker-compose.yml`
- Modify: `Dockerfile`

- [ ] **Step 1: Update `docker-compose.yml`**

Replace entire `docker-compose.yml` with:

```yaml
services:
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --reload
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: on-failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/schema/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - "POSTGRES_DB=postgres"
      - "POSTGRES_USER=postgres"
      - "POSTGRES_PASSWORD=postgres"
    restart: on-failure
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    restart: on-failure
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  worker:
    build: .
    command: celery -A config worker -l info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: on-failure

volumes:
  postgres_data:
```

Note: Using `env_file: .env` replaces inline environment variables. The `.env` file will contain the same DB/Redis defaults. For development, users can still override.

- [ ] **Step 2: Update `Dockerfile`**

Replace entire `Dockerfile` with:

```dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Note: `curl` is added for healthcheck support.

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml Dockerfile
git commit -m "feat: improve Docker setup with healthchecks, gunicorn, and env_file"
```

---

### Task 7: Refactor User Model (email-based auth)

**Files:**
- Modify: `users/models.py`
- Modify: `users/admin.py`
- Modify: `users/serializers.py`
- Modify: `users/views.py`
- Modify: `hotels/tests.py` (update `create_user` calls)
- Modify: `hotels/models.py` (update `__str__` methods that use `username`)

- [ ] **Step 1: Refactor `users/models.py`**

Replace entire `E:\projects\Pishkhan\users\models.py`:

```python
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """Custom manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CUSTOMER = 'customer'
    ROLE_HOTEL_OWNER = 'hotel_owner'

    ROLE_CHOICES = (
        (ROLE_CUSTOMER, 'مشتری'),
        (ROLE_HOTEL_OWNER, 'صاحب هتل'),
    )

    username = None
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
        verbose_name="نقش"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.email


class VerificationCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_codes'
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'کد تایید'
        verbose_name_plural = 'کدهای تایید'

    def is_expired(self):
        return timezone.now() > (self.created_at + timedelta(minutes=10))

    def __str__(self):
        return f'{self.user.email} - {self.code}'
```

- [ ] **Step 2: Create and run migration**

```bash
python manage.py makemigrations users
python manage.py migrate
```

- [ ] **Step 3: Refactor `users/admin.py`**

Replace entire `E:\projects\Pishkhan\users\admin.py`:

```python
from django.contrib import admin
from .models import VerificationCode, User
from django.contrib.auth import admin as auth_admin


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    list_display = ('email', 'role', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'role')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'role')}),
        ('مجوزها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخچه', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'role')}),
        ('مجوزها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    readonly_fields = ('last_login', 'date_joined')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(VerificationCode)
```

- [ ] **Step 4: Refactor `users/serializers.py`**

Replace entire `E:\projects\Pishkhan\users\serializers.py`:

```python
from rest_framework import serializers

from users.models import User, VerificationCode


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True, max_length=6)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'code']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'code': {'write_only': True},
        }

    def validate(self, data):
        email = data.get('email')
        code = data.get('code')

        try:
            verification_record = VerificationCode.objects.get(
                user__email=email, code=code, is_used=False
            )
            if verification_record.is_expired():
                raise serializers.ValidationError({'code': 'کد تایید منقضی شده است.'})

            self.context['verification_record'] = verification_record
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError({'code': 'کد تایید اشتباه است.'})

        return data

    def create(self, validated_data):
        email = validated_data['email']
        user, _ = User.objects.get_or_create(email=email, defaults={'is_active': False})

        user.first_name = validated_data.get('first_name', '')
        user.last_name = validated_data.get('last_name', '')
        user.set_password(validated_data['password'])
        user.is_active = True
        user.save()

        verification_record = self.context['verification_record']
        verification_record.is_used = True
        verification_record.save()

        return user


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = [
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions', 'last_login', 'date_joined'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance
```

Note: Removed `username` from `UserRegistrationSerializer.Meta.fields`. The user is now identified by email only.

- [ ] **Step 5: Refactor `users/views.py`**

Replace entire `E:\projects\Pishkhan\users\views.py`:

```python
import secrets
import string

from rest_framework.views import APIView
from rest_framework import status, generics, permissions

from core.mixins import StandardResponseMixin
from core.utils.responses import StandardResponse
from .tasks import send_verification_code_email

from users.models import User, VerificationCode
from users.serializers import (
    EmailVerificationSerializer,
    UserMeSerializer,
    UserRegistrationSerializer,
)


class RequestVerificationCodeView(APIView):
    """Send a 6-digit verification code to the given email address."""

    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'is_active': False}
        )

        if not created and user.is_active:
            return StandardResponse.error(
                message='کاربری با این ایمیل قبلاً ثبت‌نام کرده و فعال است.',
                status=status.HTTP_409_CONFLICT
            )

        # Delete previous unused codes for this user
        VerificationCode.objects.filter(user=user).delete()
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        VerificationCode.objects.create(user=user, code=code)
        send_verification_code_email.delay(email, code)

        return StandardResponse.success(
            message='کد تایید به ایمیل شما ارسال شد.',
            status=status.HTTP_200_OK
        )


class UserRegistrationView(StandardResponseMixin, generics.CreateAPIView):
    """Register a new user with email verification code."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return StandardResponse.success(
            message='ثبت‌نام شما با موفقیت تکمیل شد.',
            status=status.HTTP_200_OK
        )


class UserMeView(StandardResponseMixin, generics.RetrieveUpdateAPIView):
    """Get or update the current authenticated user's profile."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserMeSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user
```

Note: Added docstrings and improved formatting. The `username` references are gone.

- [ ] **Step 6: Update `hotels/tests.py` — change `create_user` calls**

In `E:\projects\Pishkhan\hotels\tests.py`, update all `User.objects.create_user(username='...', ...)` calls to `User.objects.create_user(email='...', ...)`.

**Replace line 15:**
```python
# Before:
self.user = User.objects.create_user(username='testuser', password='testpass')
# After:
self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
```

**Replace line 72:**
```python
# Before:
self.user = User.objects.create_user(username='testuser', password='testpass', role='customer')
self.owner = User.objects.create_user(username='hotelowner', password='testpass', role='hotel_owner')
# After:
self.user = User.objects.create_user(email='testuser@example.com', password='testpass', role='customer')
self.owner = User.objects.create_user(email='hotelowner@example.com', password='testpass', role='hotel_owner')
```

**Replace line 136:**
```python
# Before:
other_user = User.objects.create_user(username='otheruser', password='testpass', role='customer')
# After:
other_user = User.objects.create_user(email='otheruser@example.com', password='testpass', role='customer')
```

**Replace line 243:**
```python
# Before:
other_user = User.objects.create_user(username='otheruser', password='testpass', role='customer')
# After:
other_user = User.objects.create_user(email='otheruser@example.com', password='testpass', role='customer')
```

**Replace lines 297-298:**
```python
# Before:
self.user1 = User.objects.create_user(username='user1', password='testpass')
self.user2 = User.objects.create_user(username='user2', password='testpass')
# After:
self.user1 = User.objects.create_user(email='user1@example.com', password='testpass')
self.user2 = User.objects.create_user(email='user2@example.com', password='testpass')
```

- [ ] **Step 7: Update `hotels/models.py` — fix `__str__` that reference `username`**

In `E:\projects\Pishkhan\hotels\models.py`, replace lines 71-72:

**Before:**
```python
    def __str__(self):
        return f"رزرو برای {self.user.username} در اتاق {self.room_type.name}"
```

**After:**
```python
    def __str__(self):
        return f"رزرو برای {self.user.email} در اتاق {self.room_type.name}"
```

Replace lines 91-92:

**Before:**
```python
    def __str__(self):
        return f"نظر از {self.user.username} برای هتل {self.hotel.name}"
```

**After:**
```python
    def __str__(self):
        return f"نظر از {self.user.email} برای هتل {self.hotel.name}"
```

- [ ] **Step 8: Update `users/tasks.py` — remove unused import**

In `E:\projects\Pishkhan\users\tasks.py`, remove unused imports `get_object_or_404` and `User`:

**Before:**
```python
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import VerificationCode, User
```

**After:**
```python
from celery import shared_task
from django.core.mail import send_mail
```

- [ ] **Step 9: Run tests to verify everything still works**

```bash
python manage.py test hotels.tests -v 2
```

Expected: All existing tests pass (may need to adjust `client.login` calls to use email instead of username if the test client still uses username).

**Important:** Since we changed `USERNAME_FIELD` to `email`, Django's `client.login()` may need to use `email` parameter instead of `username`. Check if `self.client.login(username='testuser', password='testpass')` still works or needs to change to `self.client.login(email='testuser@example.com', password='testpass')`.

If tests fail on login, update all `self.client.login(username='...', password='...')` in `hotels/tests.py` to `self.client.login(email='...', password='...')`.

- [ ] **Step 10: Commit**

```bash
git add users/models.py users/admin.py users/serializers.py users/views.py users/tasks.py users/migrations/
git add hotels/models.py hotels/tests.py
git commit -m "refactor: email-based user authentication with CustomUserManager"
```

---

### Task 8: Register Review in Django Admin

**Files:**
- Modify: `hotels/admin.py`

- [ ] **Step 1: Add Review to `hotels/admin.py`**

Replace entire `E:\projects\Pishkhan\hotels\admin.py`:

```python
from django.contrib import admin
from .models import Hotel, RoomType, Reservation, Review


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'owner')
    search_fields = ('name', 'city', 'address')
    list_filter = ('city',)


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'price_per_night', 'capacity', 'inventory')
    list_filter = ('hotel',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'room_type', 'check_in_date', 'check_out_date', 'status')
    list_filter = ('status',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'rating', 'created_at')
    list_filter = ('rating', 'hotel')
    search_fields = ('comment',)
```

- [ ] **Step 2: Commit**

```bash
git add hotels/admin.py
git commit -m "feat: register Review model in Django admin"
```

---

### Task 9: Clean Up Unused Code

**Files:**
- Modify: `core/permissions.py`
- Delete: `plan.md`

- [ ] **Step 1: Remove `IsNotAuthenticated` from `core/permissions.py`**

Replace entire `E:\projects\Pishkhan\core\permissions.py`:

```python
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow safe methods for all; write methods only for object owner."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """Allow access only if the requesting user owns the object."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
```

- [ ] **Step 2: Delete stale `plan.md`**

```bash
rm plan.md
```

- [ ] **Step 3: Commit**

```bash
git add core/permissions.py
git rm plan.md
git commit -m "refactor: remove unused IsNotAuthenticated permission and stale plan.md"
```

---

### Task 10: Add English Comments to Hotel App

**Files:**
- Modify: `hotels/models.py`
- Modify: `hotels/serializers.py`
- Modify: `hotels/views.py`
- Modify: `hotels/permissions.py`
- Modify: `core/mixins.py`
- Modify: `core/exceptions.py`
- Modify: `core/utils/responses.py`

- [ ] **Step 1: Add comments to `hotels/models.py`**

Add docstrings to each model class. Keep Persian `verbose_name` unchanged. Add comments to methods:

```python
class Hotel(models.Model):
    """Hotel owned by a hotel_owner user."""

    owner = models.ForeignKey(...)
    # ... keep existing fields unchanged

    def average_rating(self):
        """Calculate the average rating across all reviews for this hotel."""
        # ... keep existing implementation

    def total_reviews(self):
        """Count total reviews for this hotel."""
        # ... keep existing implementation


class RoomType(models.Model):
    """A type of room available at a hotel."""

    # ... keep existing fields unchanged


class Reservation(models.Model):
    """A room reservation made by a user."""

    # ... keep existing fields unchanged


class Review(models.Model):
    """A review/rating left by a user for a hotel they have stayed at."""

    # ... keep existing fields unchanged
```

- [ ] **Step 2: Add comments to `hotels/views.py`**

Add docstrings to each ViewSet/class:

```python
class ReservationViewSet(StandardResponseMixin, ...):
    """Authenticated users can create, view, list, and cancel reservations."""

class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only listing of hotels with search and ordering."""

class RoomTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only listing of room types with search and ordering."""

class HotelAdminViewSet(viewsets.ModelViewSet):
    """Full CRUD for hotels, restricted to hotel_owner role."""

class RoomTypeAdminViewSet(viewsets.ModelViewSet):
    """Full CRUD for room types, restricted to hotel_owner role."""
```

Remove Persian inline comments (e.g., `# محاسبه قیمت و ساخت رزرو` → `# Calculate price and create reservation`).

- [ ] **Step 3: Add comments to `hotels/serializers.py`**

Add docstrings to key serializers:
```python
class CreateReservationSerializer(serializers.Serializer):
    """Validates reservation data: room type, dates, and availability."""

class RoomTypeCreateSerializer(serializers.ModelSerializer):
    """Used by hotel owners to create new room types."""

class CreateReviewSerializer(serializers.ModelSerializer):
    """Validates review creation: user must have stayed at the hotel."""
```

- [ ] **Step 4: Add comments to `hotels/permissions.py`**

```python
class IsHotelAdmin(permissions.BasePermission):
    """Restricts access to users with hotel_owner role who own the target object."""
```

- [ ] **Step 5: Add comments to `core/mixins.py`**

Add class docstring:
```python
class StandardResponseMixin:
    """Wraps all successful DRF responses in a standard {message, data} envelope."""
```

Remove Persian comment on line 3.

- [ ] **Step 6: Add comments to `core/exceptions.py`**

```python
def custom_exception_handler(exc, context):
    """Normalizes DRF exception responses into a consistent {errors: ...} format."""
```

- [ ] **Step 7: Add comments to `core/utils/responses.py`**

```python
class StandardResponse:
    """Utility class for building standardized API responses."""
```

- [ ] **Step 8: Commit**

```bash
git add hotels/models.py hotels/serializers.py hotels/views.py hotels/permissions.py
git add core/mixins.py core/exceptions.py core/utils/responses.py
git commit -m "docs: add English docstrings and comments across all modules"
```

---

### Task 11: Create .env for Development

**Files:**
- Create: `.env`

- [ ] **Step 1: Create `.env` with development defaults**

Create `E:\projects\Pishkhan\.env` (this file will be gitignored):

```env
SECRET_KEY=django-insecure-dev-key-for-local-development-only
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=postgres
DB_USER=postgres
DB_PASS=postgres
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
```

- [ ] **Step 2: Verify `.env` is not tracked by git**

```bash
git status
```

Expected: `.env` should NOT appear in the output (it's in `.gitignore`).

---

### Task 12: Run All Tests and Verify

- [ ] **Step 1: Run all tests**

```bash
python manage.py test -v 2
```

Expected: All tests pass.

- [ ] **Step 2: Verify Django admin loads**

```bash
python manage.py check
```

Expected: No issues found.

- [ ] **Step 3: Verify migrations are clean**

```bash
python manage.py showmigrations
```

Expected: All migrations applied, no unapplied migrations.

---

### Task 13: Write Bilingual README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

Create `E:\projects\Pishkhan\README.md` with the following content:

```markdown
# Pishkhan — Hotel Reservation API

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Django](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/docker-compose-available-blue.svg)](https://docs.docker.com/compose/)

A RESTful API for hotel reservation management built with Django and Django REST Framework.

---

## Features

- **User Authentication** — Email-based registration with verification codes and JWT tokens
- **Hotel Management** — Hotel owners can manage their hotels and room types
- **Room Reservation** — Users can reserve rooms with automatic inventory conflict detection
- **Reviews & Ratings** — Users can rate and review hotels they have stayed at
- **API Documentation** — Interactive Swagger UI and ReDoc documentation

## Tech Stack

| Technology | Purpose |
|---|---|
| Django 5.2 | Web framework |
| Django REST Framework 3.16 | REST API |
| SimpleJWT | JWT authentication |
| Celery + Redis | Async task queue (email sending) |
| PostgreSQL 15 | Database |
| Redis 7 | Caching and message broker |
| Docker Compose | Container orchestration |
| drf-spectacular | OpenAPI 3 documentation |

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Git](https://git-scm.com/)

### Run with Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/Alireza-Faraji-1383/Pishkhan.git
cd Pishkhan
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start all services:
```bash
docker compose up --build
```

4. The API will be available at `http://localhost:8000`

### API Documentation

| URL | Description |
|---|---|
| [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/) | Swagger UI |
| [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/) | ReDoc |
| [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/) | OpenAPI JSON Schema |

## Project Structure

```
Pishkhan/
├── config/              # Django project settings, URLs, Celery config
├── users/               # User authentication and registration
│   ├── models.py        # User and VerificationCode models
│   ├── views.py         # Registration, verification, and profile views
│   ├── serializers.py   # User data serialization
│   └── tasks.py         # Celery email task
├── hotels/              # Hotel and reservation management
│   ├── models.py        # Hotel, RoomType, Reservation, Review models
│   ├── views.py         # All hotel/reservation/review ViewSets
│   ├── serializers.py   # Hotel data serialization
│   ├── permissions.py   # Hotel admin permission class
│   └── tests.py         # Review model and API tests
├── core/                # Shared utilities
│   ├── mixins.py        # StandardResponseMixin for unified responses
│   ├── permissions.py   # IsOwner, IsOwnerOrReadOnly
│   ├── exceptions.py    # Custom DRF exception handler
│   └── utils/responses.py  # StandardResponse utility
├── docker-compose.yml   # Service orchestration
├── Dockerfile           # Container image definition
└── requirements.txt     # Python dependencies
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | insecure dev key |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `DB_NAME` | PostgreSQL database name | `postgres` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_PASS` | PostgreSQL password | `postgres` |
| `DB_HOST` | PostgreSQL host | `db` (Docker) / `localhost` (local) |
| `DB_PORT` | PostgreSQL port | `5432` |
| `REDIS_HOST` | Redis host | `redis` (Docker) / `localhost` (local) |

## License

This project is licensed under the MIT License.

---

# پیش‌خوان — API رزرو هتل

یک API استراحت‌گرا (RESTful) برای مدیریت رزرو هتل، ساخته‌شده با جنگو و فریم‌ورک استراحت جنگو.

## ویژگی‌ها

- **احراز هویت کاربر** — ثبت‌نام با ایمیل و کد تایید، توکن‌های JWT
- **مدیریت هتل** — صاحبان هتل می‌توانند هتل و انواع اتاق خود را مدیریت کنند
- **رزرو اتاق** — کاربران می‌توانند اتاق رزرو کنند، با تشخیص خودکار تداخل موجودی
- **نظرات و امتیازدهی** — کاربران می‌توانند به هتل‌هایی که اقامت داشته‌اند امتیاز و نظر بدهند
- **مستندات API** — مستندات تعاملی Swagger UI و ReDoc

## شروع سریع

### پیش‌نیازها

- [Docker](https://docs.docker.com/get-docker/) و Docker Compose
- [Git](https://git-scm.com/)

### اجرا با Docker Compose

1. مخزن را کلون کنید:
```bash
git clone https://github.com/Alireza-Faraji-1383/Pishkhan.git
cd Pishkhan
```

2. فایل محیطی را ایجاد کنید:
```bash
cp .env.example .env
```

3. سرویس‌ها را اجرا کنید:
```bash
docker compose up --build
```

4. API در آدرس `http://localhost:8000` در دسترس خواهد بود.

### مستندات API

| آدرس | توضیحات |
|---|---|
| [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/) | Swagger UI |
| [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/) | ReDoc |
| [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/) | الگوی OpenAPI |

## متغیرهای محیطی

| متغیر | توضیحات | پیش‌فرض |
|---|---|---|
| `SECRET_KEY` | کلید مخفی جنگو | کلید توسعه |
| `ALLOWED_HOSTS` | هاست‌های مجاز | `localhost,127.0.0.1` |
| `DB_NAME` | نام دیتابیس PostgreSQL | `postgres` |
| `DB_USER` | کاربر PostgreSQL | `postgres` |
| `DB_PASS` | رمز PostgreSQL | `postgres` |
| `DB_HOST` | هاست PostgreSQL | `db` (Docker) / `localhost` (محلی) |
| `DB_PORT` | پورت PostgreSQL | `5432` |
| `REDIS_HOST` | هاست Redis | `redis` (Docker) / `localhost` (محلی) |

## مجوز

این پروژه تحت لایسنس MIT منتشر شده است.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add bilingual README (English/Persian)"
```

---

### Task 14: Final Verification

- [ ] **Step 1: Run all tests one final time**

```bash
python manage.py test -v 2
```

Expected: All tests pass.

- [ ] **Step 2: Verify Django check passes**

```bash
python manage.py check --deploy
```

Expected: May show deployment warnings (expected for dev config), but no errors.

- [ ] **Step 3: Review git log**

```bash
git log --oneline
```

Expected: Clean commit history with all tasks committed.
