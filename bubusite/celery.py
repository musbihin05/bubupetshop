import os
from celery import Celery

# Atur default Django settings module untuk program 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bubusite.settings')

app = Celery('bubusite')

# Menggunakan string di sini berarti konfigurasi tidak perlu
# diserialisasi ke child process.
# namespace='CELERY' berarti semua kunci konfigurasi Celery harus diawali dengan 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Temukan dan muat tasks dari semua aplikasi Django terdaftar
app.autodiscover_tasks()
