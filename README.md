# Pishkhan (پیش‌خوان)

A RESTful API for hotel reservation management built with Django and Django REST Framework.

## Features

- **User Authentication** — Email-based registration with verification codes and JWT authentication
- **Hotel Management** — CRUD operations for hotels and room types by hotel owners
- **Reservation System** — Atomic booking with conflict detection and automatic price calculation
- **Review System** — Rate and review hotels with one-review-per-user enforcement
- **API Documentation** — Interactive Swagger UI and ReDoc (OpenAPI 3)
- **Async Tasks** — Celery-powered email sending via Redis
- **Standardized Responses** — Unified `{message, data}` response format with Persian error messages

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.13 | Core language |
| Django 5.2 | Web framework |
| Django REST Framework | REST API |
| SimpleJWT | JWT authentication |
| Celery | Async task queue |
| Redis | Caching & message broker |
| PostgreSQL | Database |
| Docker Compose | Container orchestration |
| Gunicorn | Production WSGI server |

## Project Structure

```
Pishkhan/
├── config/          # Django project settings, URLs, Celery config
├── users/           # User auth, registration, verification
├── hotels/          # Hotel, room, reservation, review management
├── core/            # Shared utilities, permissions, mixins
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py
```

## Getting Started

### Docker (Recommended)

```bash
git clone https://github.com/Alireza-Faraji-1383/Pishkhan.git
cd Pishkhan
cp .env.example .env
docker compose up --build
```

### Local Development

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
cp .env.example .env          # Edit with your local DB/Redis config

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
celery -A config worker -l info  # In a separate terminal
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register/send-code/` | POST | Send verification code to email |
| `/api/auth/register/` | POST | Complete registration with code |
| `/api/auth/token/` | POST | Get JWT token pair |
| `/api/auth/token/refresh/` | POST | Refresh JWT access token |
| `/api/auth/me/` | GET/PUT/PATCH | User profile |
| `/api/hotels/hotels/` | GET | List hotels (public) |
| `/api/hotels/hotels/{id}/` | GET | Hotel detail (public) |
| `/api/hotels/room-types/` | GET | List room types (public) |
| `/api/hotels/HotelAdmin/` | CRUD | Manage hotels (hotel_owner) |
| `/api/hotels/RoomTypeAdmin/` | CRUD | Manage room types (hotel_owner) |
| `/api/hotels/reservations/` | CRUD | Manage reservations |
| `/api/hotels/reservations/{id}/cancel/` | POST | Cancel reservation |
| `/api/hotels/reviews/` | CRUD | Manage reviews |
| `/api/schema/swagger-ui/` | GET | Swagger UI |
| `/api/schema/redoc/` | GET | ReDoc |

## Testing

```bash
python manage.py test -v 2
```

## Environment Variables

See `.env.example` for required environment variables:

- `SECRET_KEY` — Django secret key
- `DEBUG` — Enable/disable debug mode
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` — PostgreSQL config
- `REDIS_HOST`, `REDIS_PORT` — Redis config
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD` — SMTP email config

## License

This project is open source. See the repository for license details.
