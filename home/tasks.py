from os import name
from home.models import Inventory, Order, ItemInst
from datetime import date
from celery import shared_task

@shared_task(name="check_orders")
def check_order():
    for order in Order.objects.all():
        if order.till_date < date.today() and order.status != "Fulfilled":
            order.status = "Fulfilled"
            for iteminst in order.iteminst_set.all():
                iteminvent = Inventory.objects.get(id=iteminst.item.pk)
                iteminvent.rented-=iteminst.quantity
                iteminvent.save()
            order.save()
            print(order)
    print('CHECKED ORDERS')