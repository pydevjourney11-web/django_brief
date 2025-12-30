
set -e

python manage.py migrate --noinput
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python - <<'PY'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','brief_project.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User=get_user_model()
username=os.environ.get('DJANGO_SUPERUSER_USERNAME')
email=os.environ.get('DJANGO_SUPERUSER_EMAIL')
password=os.environ.get('DJANGO_SUPERUSER_PASSWORD')
u, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True})
if not created:
    if email:
        u.email=email
    u.is_staff=True
    u.is_superuser=True
if password:
    u.set_password(password)
u.save()
print('superuser_ready', u.username)
PY
fi

python manage.py collectstatic --noinput

exec gunicorn brief_project.wsgi:application --bind 0.0.0.0:8000
