from django_extensions.management.jobs import MinutelyJob
from home.models import Item
class Job(MinutelyJob):
    help = "Hello"

    def execute(self):
        item = Item.objects.all()[0]
        item.stock+=1
        item.save()
        print("HI Worlds")