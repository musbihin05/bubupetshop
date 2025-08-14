from django.core.management.base import BaseCommand
from user.models import User

class Command(BaseCommand):
    help = 'Seed user data'

    def handle(self, *args, **kwargs):
        users = [
            {'email': 'user1@example.com', 'nama': 'User Satu', 'no_hp': '081234567890', 'password': 'password123'},
            {'email': 'user2@example.com', 'nama': 'User Dua', 'no_hp': '081234567891', 'password': 'password123'},
        ]

        # Create superuser if not exists
        superuser_email = 'admin@mail.com'
        if not User.objects.filter(email=superuser_email).exists():
            User.objects.create_superuser(
          email=superuser_email,
          nama='Admin',
          password='admin',
          no_hp='081234567899'
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser {superuser_email} created"))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser {superuser_email} already exists"))
        for u in users:
            if not User.objects.filter(email=u['email']).exists():
                user = User.objects.create_user(email=u['email'], nama=u['nama'], password=u['password'], no_hp=u['no_hp'])
                self.stdout.write(self.style.SUCCESS(f"User {u['email']} created"))
            else:
                self.stdout.write(self.style.WARNING(f"User {u['email']} already exists"))
