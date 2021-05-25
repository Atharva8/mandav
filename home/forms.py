from django import forms
from home.models import ItemInst, Order
from django.core.exceptions import ValidationError
from home.inventory import check_dates, check_inventory, check_time, equal_dates

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


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





