from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from api_misvoti.models import MiVotiUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not MiVotiUser.objects.filter(username="pensubitoadmin").exists():
            MiVotiUser.objects.create_superuser("pensubitoadmin", "11-10390@usb.ve", "pensubitoadmin1234")