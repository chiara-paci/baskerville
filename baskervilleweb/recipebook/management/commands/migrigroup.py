"""
Management utility to create superusers.
"""

from django.core.management.base import BaseCommand, CommandError

from recipebook import models

class Command(BaseCommand):
    help = 'Temporary'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        for grp in models.IngredientGroup.objects.all():
            print(grp)
            for i in grp.ingredients:
                print("    ",i)
                rel,created=models.IngredientIngredientGroupRelation.objects.get_or_create(ingredient=i,group=grp)
