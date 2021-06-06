from django import forms
from django.core.exceptions import ValidationError
from home.models import ItemInst, Order
from home.validation import CheckInventory, ValidateItemInst

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class ItemInstForm(forms.ModelForm):
    class Meta:
        model = ItemInst
        fields = '__all__'

    def clean(self):
        cleaned_data = self.cleaned_data
        checkinventory = CheckInventory(iteminstance=cleaned_data)
        validate_iteminst = ValidateItemInst(instance=cleaned_data)

        if not checkinventory.check_available():
            raise ValidationError('Item not available in inventory')

        if validate_iteminst.check_tilldate_smaller_than_fromdate():
            raise ValidationError('Till date smaller than From date.')

        if validate_iteminst.by_hour:
            if not validate_iteminst.check_equal_dates():
                raise ValidationError('From date and Till date are not equal.')
                
            if not validate_iteminst.check_min_hour():
                raise ValidationError('Duration Must be Minimum a hour.')

        if not validate_iteminst.check_in_order_range():
            raise ValidationError('From Date and Till Date not in range of Order')