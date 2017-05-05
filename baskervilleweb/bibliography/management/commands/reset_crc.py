
from django.core.management.base import BaseCommand

from bibliography import models

class Command(BaseCommand):

    #def add_arguments(self, parser):
    #    parser.add_argument('email')

    def handle(self, *args, **options):
        for book in models.Book.objects.all():
            book.update_crc()

