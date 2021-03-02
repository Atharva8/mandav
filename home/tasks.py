from background_task import background
from .models import Inventory, ItemInst, Order
import datetime
@background(schedule=1)
def notify_user():
    # lookup user by id and send them a message
    for order in Order.objects.all():
        if order.till_date < datetime.date.today() and order.status != "Fulfilled":
            order.status = "Fulfilled"
            for iteminst in order.iteminst_set.all():
                iteminvent = Inventory.objects.get(id=iteminst.item.pk)
                iteminvent.rented-=iteminst.quantity
                iteminvent.save()
                print(iteminst)
            order.save()

