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
ALLOWED_HOSTS=clinic1618.ir,www.clinic1618.ir
CSRF_TRUSTED_ORIGINS=https://clinic1618.ir,https://www.clinic1618.ir
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

### بکاپ خودکار PostgreSQL در VPS

اسکریپت [docker/backup.sh](docker/backup.sh) از دیتابیس PostgreSQL و پوشه `media` (تصاویر بیماران، پزشکان و تصاویر آپلودشده توسط مدیر) بکاپ فشرده می‌گیرد و به‌صورت پیش‌فرض بکاپ‌های قدیمی‌تر از ۱۴ روز را حذف می‌کند. روی VPS اجرا کنید:

```bash
sudo mkdir -p /var/backups/doctor-platform
sudo chown "$USER":"$USER" /var/backups/doctor-platform
chmod +x docker/backup.sh
./docker/backup.sh
```

برای اجرای روزانه ساعت ۳ بامداد در Cron:

```bash
crontab -e
```

این خط را اضافه کنید:

```cron
0 3 * * * cd /path/to/Docters-website && /path/to/Docters-website/docker/backup.sh >> /var/backups/doctor-platform/backup.log 2>&1
```

مسیرهای نمونه را با مسیر واقعی پروژه جایگزین کنید. فایل‌های بکاپ حاوی اطلاعات حساس هستند و فقط با مجوز کاربر مالک ذخیره می‌شوند. برای بازیابی کامل، فایل `postgres_*.sql.gz` دیتابیس و فایل `media_*.tar.gz` تصاویر را هر دو نگه دارید.

### Nginx Reverse Proxy و SSL روی VPS

در VPS، Nginx سیستم عامل روی پورت‌های `80` و `443` قرار می‌گیرد. کانتینر Docker فقط روی `127.0.0.1:8000` قابل دسترسی است.

```nginx
server {
    listen 80;
    server_name clinic1618.ir www.clinic1618.ir;

    client_max_body_size 5M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d clinic1618.ir -d www.clinic1618.ir
sudo certbot renew --dry-run
```

سپس در `.env`:

```env
CSRF_TRUSTED_ORIGINS=https://clinic1618.ir,https://www.clinic1618.ir
SECURE_SSL_REDIRECT=True
```

## دیپلوی روی Liara با Nginx

این پروژه برای Liara به‌صورت یک Docker App آماده شده است: Nginx روی پورت `80` گوش می‌دهد، فایل‌های static و media را مستقیم سرو می‌کند و درخواست‌های دیگر را به Gunicorn روی پورت داخلی `8000` می‌فرستد.

1. در Liara یک اپلیکیشن Docker و یک دیتابیس PostgreSQL بسازید.
2. پروژه را به GitHub متصل کنید یا از ریشه پروژه اجرا کنید:

```bash
liara deploy --platform docker
```

3. در بخش Environment Variables این مقادیر را تنظیم کنید:

```env
SECRET_KEY=<کلید-قوی>
DEBUG=False
ALLOWED_HOSTS=clinic1618.ir,www.clinic1618.ir
CSRF_TRUSTED_ORIGINS=https://clinic1618.ir,https://www.clinic1618.ir
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<نام-دیتابیس>
DB_USER=<کاربر-دیتابیس>
DB_PASSWORD=<رمز-دیتابیس>
DB_HOST=<آدرس-داخلی-دیتابیس-لیارا>
DB_PORT=5432
USE_SQLITE=False
SERVE_MEDIA=False
SECURE_SSL_REDIRECT=True
```

4. در بخش Domains دامنه‌های `clinic1618.ir` و `www.clinic1618.ir` را اضافه کنید. رکوردهای DNS را طبق مقادیر نمایش‌داده‌شده توسط Liara تنظیم کنید، سپس گزینه SSL/HTTPS را برای دامنه فعال کنید. گواهی SSL در لایه Liara مدیریت می‌شود و نیازی به قرار دادن certificate یا key داخل Docker image نیست.

پس از فعال شدن SSL، درخواست‌های HTTP به HTTPS هدایت می‌شوند و هدر `X-Forwarded-Proto` توسط proxy به Django منتقل می‌شود.

پورت عمومی برنامه را `80` قرار دهید. اجرای migration و `collectstatic` هنگام شروع کانتینر انجام می‌شود. برای حفظ فایل‌های آپلودی، media را روی storage پایدار Liara یا فضای فایل متصل به اپلیکیشن قرار دهید؛ در غیر این صورت با rebuild کانتینر ممکن است تصاویر از بین بروند.

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
| `/doctors/<slug>/` | پروفایل پزشک |
| `/doctors/<slug>/consultation-form/` | فرم مستقل درخواست مشاوره پزشک |
| `/dashboard/` | پنل مدیریت |
| `/dashboard/doctors/` | مدیریت پزشکان (Superuser) |
| `/dashboard/articles/` | مدیریت مقالات (Superuser) |
| `/dashboard/managers/` | مدیریت مدیران (Superuser) |
