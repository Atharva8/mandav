import datetime
from django.db.models.aggregates import Sum
from home.models import ItemInst, Order
from django.utils import timezone

class CheckInventory:
    #Outer : Item Instances that contain the given from date and till date
    #Inner : Item Instances that are in the range of the given from date and till date
    #Qty : Quantity
    def __init__(self,iteminstance) -> None:
        self.from_date = iteminstance['from_date']
        self.till_date = iteminstance['till_date']
        self.iteminstance_id = iteminstance['id']
        self.item = iteminstance['item']
        self.all_item_instances = ItemInst.objects.filter(item=self.item.id)
        if self.check_if_exists():
            self.all_item_instances = self.all_item_instances.exclude(pk=self.iteminstance_id.id)
        self.quantity = iteminstance['quantity']
        self.by_hour = iteminstance['by_hour']

    def check_if_exists(self):
        if self.iteminstance_id is None:
            return False
        return True

    def check_available(self) -> bool:
        available_qty = self.get_available()
        if available_qty < self.quantity:
            return False
        return True

    def get_available(self) -> int:
        total_qty = self._get_total_qty()
        return self.item.stock - total_qty

    def _get_total_qty(self):
        if self.by_hour:
            total = self.all_item_instances.filter(from_date__lt=self.till_date, till_date__gt=self.from_date)
            day = self.all_item_instances.filter(from_date=timezone.make_aware(datetime.datetime.combine(self.from_date.date(),datetime.time())), till_date=timezone.make_aware(datetime.datetime.combine(self.till_date.date(),datetime.time())))
                       
            return self._get_qty(total)+self._get_qty(day)
        else:
            total = self.all_item_instances.filter(from_date__date__lte=self.till_date.date(), till_date__date__gte=self.from_date.date())
            return self._get_qty(total)

         

    def _get_qty(self,queryset):
        qty = queryset.aggregate(Sum('quantity'))['quantity__sum'] 
        return 0 if not qty else qty


class ValidateItemInst:
    def __init__(self, instance):
        self.instance = instance
        self.from_date = instance['from_date']
        self.till_date = instance['till_date']
        self.by_hour = instance['by_hour']
        self.order_from_date = instance['order'].from_date
        self.order_till_date = instance['order'].till_date
    def check_tilldate_smaller_than_fromdate(self):
        return self.till_date<self.from_date
    
    def check_min_hour(self):
        if self.by_hour and self.check_equal_dates():
            delta_time = self.till_date-self.from_date
            return int(delta_time.total_seconds())>= 60*60
        return False

    def check_equal_dates(self):
        return self.from_date.date() == self.till_date.date()

    def check_in_order_range(self):
        return self.from_date.date() >= self.order_from_date and self.till_date.date() <= self.order_till_date