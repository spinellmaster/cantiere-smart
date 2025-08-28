from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Project

class Command(BaseCommand):
    help = "Crea utente admin e un progetto demo"

    def handle(self, *args, **options):
        # Admin demo
        if not User.objects.filter(username='admin@demo.it').exists():
            User.objects.create_user(
                username='admin@demo.it',
                email='admin@demo.it',
                password='admin123',
                first_name='Admin',
                last_name='Demo',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS("Creato utente admin: admin@demo.it / admin123"))
        else:
            self.stdout.write("Utente admin già presente")

        # Progetto demo
        if not Project.objects.filter(name='Ristrutturazione Via Etnea').exists():
            Project.objects.create(
                name='Ristrutturazione Via Etnea',
                client_name='Impresa Rossi',
                budget_eur=50000,
                description='Cantiere pilota',
                status='active'
            )
            self.stdout.write(self.style.SUCCESS("Creato progetto demo"))
        else:
            self.stdout.write("Progetto demo già presente")
