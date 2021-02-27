from django.core.management.base import BaseCommand
from django_seed import Seed
from users.models import User

# from rooms import models as room_models


class Command(BaseCommand):

    help = "This command create many users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", default=2, type=int, help="how many users do you want to create"
        )

    def handle(self, *args, **options):
        number = options.get(
            "number",
        )
        seeder = Seed.seeder()
        seeder.add_entity(
            User,
            number,
            {"is_staff": False, "is_superuser": False},
        )
        seeder.execute()
        self.stdout.write(self.style.SUCCESS(f"{number} Users were created"))
