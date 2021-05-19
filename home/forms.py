from django import forms
from django.forms import fields
from home.models import Item, ItemInst, Order
from django.core.exceptions import ValidationError
from django.db.models import Sum
import json
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
        print(item)
        
        if item['id'] is not None:
            items = ItemInst.objects.exclude(id=item['id'].id).all()
            total = ItemInst.objects.exclude(id=item['id'].id).all().aggregate(Sum('quantity'))['quantity__sum']
        else:
            items = ItemInst.objects.all()
        
            total = ItemInst.objects.all().aggregate(Sum('quantity'))['quantity__sum']
            print(ItemInst.objects.all())
            
        if total == None:
            total = 0
        total += item["quantity"]
        item_inventory = Item.objects.get(id=item["item"].id).stock
    
        if total > item_inventory:
             raise ValidationError(message='Item placed greater than Inventory')
        