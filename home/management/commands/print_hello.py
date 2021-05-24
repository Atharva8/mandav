from django.core.management.base import BaseCommand, CommandError
from home.models import Item
class Command(BaseCommand):
    help = 'Prints Hello'


    def handle(self, *args, **options):
        item = Item.objects.all()[0]
        item.stock +=1 
        item.save()
        self.stdout.write("Hello")