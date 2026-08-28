# Django Doctor Consultation Platform

پلتفرم معرفی پزشکان و دریافت درخواست مشاوره — Django + PostgreSQL 16 + Docker

## اجرا با Docker (پیشنهادی برای VPS)

### ۱. تنظیم Environment

```bash
cp .env.example .env
```

مقادیر `.env` را ویرایش کنید:

```env
SECRET_KEY=<کلید-قوی>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
DB_PASSWORD=<رمز-قوی>
SERVE_MEDIA=True
SECURE_SSL_REDIRECT=False
```

### ۲. Build و Run

```bash
docker compose up -d --build
```

### ۳. Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

سایت: `http://localhost:8000`

### ۴. دستورات مفید

```bash
docker compose logs -f web
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose down
docker compose down -v   # حذف volumeها
```

## اجرای محلی (بدون Docker)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # USE_SQLITE=True

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## دیپلوی روی VPS

### Docker Compose

```bash
git clone <repo> && cd doctor-platform
cp .env.example .env
# edit .env — ALLOWED_HOSTS, SECRET_KEY, DB_PASSWORD, CSRF_TRUSTED_ORIGINS
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

### Nginx Reverse Proxy (نمونه)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 5M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

SSL با Certbot:

```bash
certbot --nginx -d yourdomain.com
```

سپس در `.env`:

```env
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
SECURE_SSL_REDIRECT=True
```

## مدیریت مدیران (Dashboard)

فقط **Superuser** به این بخش دسترسی دارد:

| مسیر | عملکرد |
|------|--------|
| `/dashboard/managers/` | لیست مدیران Staff |
| `/dashboard/managers/create/` | ایجاد مدیر جدید |
| `/dashboard/managers/<id>/assign/` | تخصیص پزشک به مدیر |
| `/dashboard/managers/<id>/delete/` | حذف مدیر |

## ساختار Docker

```
Dockerfile              — Python 3.11 slim + Gunicorn
docker-compose.yml      — web + postgres:16-alpine
docker/entrypoint.sh    — wait DB → migrate → collectstatic → gunicorn
```

Volumeها:
- `postgres_data` — دیتابیس
- `media_data` — آپلود تصاویر

## تست

```bash
python manage.py test
```

## URLها

| مسیر | توضیح |
|------|-------|
| `/` | صفحه اصلی |
| `/doctors/` | لیست پزشکان |
| `/doctors/<slug>/` | پروفایل + فرم مشاوره |
| `/dashboard/` | پنل مدیریت |
| `/admin/` | Django Admin |
