import datetime
from django.core.exceptions import ValidationError
from django.db.models import Sum
import pytz
import datetime
from django.utils import timezone
from home.models import Item, ItemInst
import logging
import time

logger = logging.getLogger('inventory')


def check_dates(order_from_date, order_till_date, item_date):
    return order_from_date <= item_date <= order_till_date


def equal_dates(from_date, till_date):
    return from_date.date() == till_date.date()


def check_time(from_date, till_date):
    return int((till_date-from_date).seconds) >= 3600


def check_inventory(item=None):

    if item['by_hour'] == True:
        inventory_by_hour(item)
    else:
        inventory_by_day(item)


"Convert given date to utc"


def convert_utc(date):
    timestamp = date.timestamp()
    return datetime.datetime.utcfromtimestamp(timestamp)


"""Item Inventory Check for by_hour implementation"""


def inventory_by_hour(item_inst):
    from_date = timezone.make_aware(convert_utc(
        item_inst['from_date']), timezone=pytz.utc)
    item_id = item_inst['item'].id
    item = Item.objects.get(id=item_id)

    if item.stock < item_inst['quantity']:
        logger.error('Item greater than in stock')
        raise ValidationError('Item greater than in stock')

    if item.available < item_inst['quantity']:
        start_time = time.time()
        total = ItemInst.objects.filter(till_date__date=from_date.date(), by_hour=True).exclude(
            id=item_id).filter(till_date__lte=from_date).aggregate(Sum('quantity'))['quantity__sum']
        delta = time.time()-start_time
        logger.info('Finished ItemInst query in [%s]', delta)

        if total == None:
            total = 0
        if item_inst['id'] == None:
            existing_qty = 0
        else:
            existing_qty = ItemInst.objects.get(id=item_inst['id'].id).quantity

        if total+item.available < item_inst['quantity']-existing_qty:
            logger.error(
                'Item greater than available [%s]', item_inst['quantity']-existing_qty)
            raise ValidationError('Item greater than available', code=101)


"Item Inventory Check for by_day implementation"


def inventory_by_day(item_inst):
    from_date = timezone.make_aware(convert_utc(
        item_inst['from_date']), timezone=pytz.utc)
    start_time = time.time()
    total = ItemInst.objects.filter(till_date__lt=from_date).aggregate(
        Sum('quantity'))['quantity__sum']
    delta = time.time()-start_time
    logger.info('Finished ItemInst query in [%s]', delta)
    item = Item.objects.get(id=item_inst['item'].id)
    if item_inst['id'] == None:
        existing_qty = 0
    else:
        existing_qty = ItemInst.objects.get(id=item_inst['id'].id).quantity
    if total is None:
        total = 0

    if total+item.available < item_inst['quantity']-existing_qty:
        logger.error(
            'Item greater than available [%s]', item_inst['quantity']-existing_qty)
        raise ValidationError('Item greater than available', code=101)
