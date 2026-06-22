# Pishkhan Refactoring Design Spec

**Date:** 2026-06-22
**Scope:** Balanced refactoring — bug fixes, production readiness, and code quality improvements.
**No new features.** Existing functionality preserved.

---

## Part 1: Bug Fixes

### 1.1 RoomTypeAdminViewSet owner TypeError
- **File:** `hotels/views.py` — `RoomTypeAdminViewSet.perform_create`
- **Problem:** Passes `owner=self.request.user` but `RoomType` model has no `owner` field. Causes `TypeError` at runtime.
- **Fix:** Remove `owner` from `perform_create`. `RoomType` links to its owner via `RoomType.hotel.owner`.

### 1.2 User Email Uniqueness
- **File:** `users/models.py`
- **Problem:** `email` inherited from `AbstractUser` is not unique. Multiple users could share an email.
- **Fix:** Add `CustomUserManager` with email-based authentication. Set `email = models.EmailField(unique=True)`, `USERNAME_FIELD = 'email'`, `REQUIRED_FIELDS = []`. Remove `username` field or set it `null=True, blank=True`.

### 1.3 VerificationCode Code Namespace Exhaustion
- **File:** `users/models.py` — `VerificationCode.code`
- **Problem:** `unique=True` on 6-digit code. Expired codes still consume the namespace. After many registrations, code generation will fail with `IntegrityError`.
- **Fix:** Remove `unique=True` from `code` field. Validation logic already checks the latest unused code for a specific user; no DB-level uniqueness needed.

### 1.4 Review Not Registered in Admin
- **File:** `hotels/admin.py`
- **Problem:** `Review` model is not registered in Django admin.
- **Fix:** Register with `list_display = ('user', 'hotel', 'rating', 'created_at')` and `list_filter = ('rating',)`.

---

## Part 2: Production Readiness

### 2.1 Environment Configuration
- Add `python-dotenv` to `requirements.txt`
- `SECRET_KEY` from `os.environ.get('SECRET_KEY', 'django-insecure-...')` (keep dev default)
- `ALLOWED_HOSTS` from `os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')`
- `REDIS_HOST` from env var (default: `redis`)
- `DATABASE_URL` / individual DB params from env vars (keep current inline docker-compose env vars)
- Create `.env.example` listing all required environment variables

### 2.2 Timezone Consistency
- Change `TIME_ZONE` from `'UTC'` to `'Asia/Tehran'` (project is Persian/Iran-oriented)
- Ensure `CELERY_TIMEZONE` matches: `'Asia/Tehran'`
- Add `USE_TZ = True` to keep aware datetimes

### 2.3 Docker Improvements
- Add `HEALTHCHECK` to web service (`curl -f http://localhost:8000/api/schema/ || exit 1`)
- Add `HEALTHCHECK` to redis service
- Add `gunicorn` to `requirements.txt`
- Use `gunicorn config.wsgi:application --bind 0.0.0.0:8000` in docker-compose web service (keep `runserver` in dev override)

### 2.4 .gitignore
Create `.gitignore` with standard Django entries:
- `__pycache__/`, `*.pyc`, `.env`, `db.sqlite3`, `.venv/`, `*.egg-info/`, `.idea/`, `.vscode/`, `*.log`

---

## Part 3: Code Quality

### 3.1 Remove Unused Dependencies
Remove from `requirements.txt`:
- `django-allauth`
- `dj-rest-auth`

Decision: Keep `drf-nested-routers` (may be used in future) or remove. Will remove.

### 3.2 User Model Refactor
Replace the current `User` model:
```python
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
```
- Requires a new migration
- Update `users/serializers.py` and `users/views.py` to use email instead of username
- Update `users/admin.py` UserAdmin to work with email-based model

### 3.3 Standardize Response Handling
- Remove direct `StandardResponse.success()` / `StandardResponse.error()` calls in views
- All views use `StandardResponseMixin` which wraps responses in `finalize_response`
- Views return plain data or DRF Response objects; mixin handles the envelope

### 3.4 Remove Unused Code
- Remove `IsNotAuthenticated` from `core/permissions.py` (not used anywhere)
- Delete or update `plan.md` (stale document about Review feature that is already implemented)

### 3.5 Code Language
- Variable names, function names, and comments: **English**
- `verbose_name`, `help_text`, user-facing messages: **Persian (Farsi)**

### 3.6 Remove drf-nested-routers
- Remove from `requirements.txt`
- Not imported or used anywhere in the codebase

---

## Part 4: README

Create `README.md` with bilingual content:

### English Section
1. Project title: "Pishkhan — Hotel Reservation API"
2. Description and features list
3. Tech stack table
4. Quick Start (Docker Compose)
5. API Documentation (Swagger/ReDoc URLs)
6. Project structure overview
7. Environment variables table

### Persian Section (فارسی)
Translation of all above sections into Persian.

---

## Constraints
- No new features — only refactoring existing code
- All existing tests must continue to pass after changes
- No breaking changes to API endpoints (URLs remain the same)
- Response envelope format preserved
- Persian user-facing strings preserved
