"""
Management utility to create superusers.
"""

from django.conf import settings

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Used to import a photo.'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            'photo',
            dest="photo", 
        )

    def handle(self, *args, **options):
        pass

