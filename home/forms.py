from django import forms
from django.forms import fields
from home.models import Inventory, Item, ItemInst, Order
from django.core.exceptions import ValidationError
from django.db.models import Sum
import pytz
import datetime
from django.utils import timezone


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def clean(self):
        pass


class ItemInstForm(forms.ModelForm):
    class Meta:
        model = ItemInst
        fields = '__all__'

    def clean(self):
        item = self.cleaned_data
        order_fromdate = item['order'].from_date
        order_tilldate = item['order'].till_date

        """Check if item date is in the range of order date"""
        if not (check_dates(order_fromdate, order_tilldate, item["from_date"].date()) and check_dates(order_fromdate, order_tilldate, item["till_date"].date())):
            raise ValidationError(message="Check your dates")

        "Check if item quantity in inventory"
        check_inventory(item)

        """Check Equal Dates"""
        if not(equal_dates(item['from_date'], item['till_date'])) and item['by_hour'] == True:
            raise ValidationError(message='Dates are not equal')

        """Duration Checking(Min 1 hr)"""
        if not(check_time(item['from_date'], item['till_date'])) and item['by_hour'] == True:
            raise ValidationError(message='Duration must be atleast one hour.')


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
        raise ValidationError('Item greater than in stock')

    if item.available < item_inst['quantity']:
        total = ItemInst.objects.filter(till_date__date=from_date.date(), by_hour=True).exclude(
            id=item_id).filter(till_date__lte=from_date).aggregate(Sum('quantity'))['quantity__sum']
        if total == None:
            total = 0
        if item_inst['id'] == None:
            existing_qty = 0
        else:
            existing_qty = ItemInst.objects.get(id=item_inst['id'].id).quantity

        if total+item.available < item_inst['quantity']-existing_qty:
            raise ValidationError('Item greater than available')


"Item Inventory Check for by_day implementation"


def inventory_by_day(item_inst):
    from_date = timezone.make_aware(convert_utc(
        item_inst['from_date']), timezone=pytz.utc)
    total = ItemInst.objects.filter(till_date__lt=from_date).aggregate(
        Sum('quantity'))['quantity__sum']
    item = Item.objects.get(id=item_inst['item'].id)
    if item_inst['id'] == None:
        existing_qty = 0
    else:
        existing_qty = ItemInst.objects.get(id=item_inst['id'].id).quantity

    if total+item.available < item_inst['quantity']-existing_qty:
        raise ValidationError('Item greater than available')


