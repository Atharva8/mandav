from django.core.management.base import BaseCommand
from home.models import Item, ItemInst
import datetime
from home.inventory import convert_utc
import pytz
from django.utils import timezone
import logging
import time

logger = logging.getLogger('inventory')

class Command(BaseCommand):
    help = 'Monitors and Updates Inventory'

    def add_arguments(self, parser):
        parser.add_argument('-hour',
                            '--hour',
                            action='store_true',
                            help='toggle hour or day')

    def handle(self, *args, **options):
        toggle = options['hour']

        if toggle:
            self.monitor_hour()
        else:
            self.monitor_day()

    def monitor_day(self):
        items = ItemInst.objects.exclude(order__status="Fulfilled").filter(status="Incomplete").filter(by_hour=False).all()
        count=0
        for item in items:
            if datetime.datetime.today().date() > item.till_date.date():
                item.status = 'Complete'
                item.save()
                count+=1
        logger.info('Marked [%s] ItemInst as Complete',count)
                

    
    def monitor_hour(self):
        items = ItemInst.objects.exclude(order__status="Fulfilled").filter(status="Incomplete").filter(by_hour=True).all()
        current = timezone.make_aware(convert_utc(datetime.datetime.now()),tzinfo=pytz.utc)
        count=0
        for item in items:
            if current > item.till_date:
                item.status = 'Complete'
                item.save()
                count+=1
        logger.info('Marked [%s] ItemInst as Complete',count)
