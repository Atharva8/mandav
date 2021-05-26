from django.db.models.signals import post_delete, pre_delete, post_save, pre_save
from django.dispatch import receiver
from home.models import Item, ItemInst, Payment, Order, PaymentDetail
from cloudinary.api import delete_resources


@receiver(post_save, sender=Order)
def create_payment(sender, instance, **kwargs):
    if sender == Order:
        if Payment.objects.filter(order=instance).count() >= 1:
            return
        else:
            payment = Payment.objects.create(
                order=instance, date=instance.from_date)
            payment.save()


@receiver([pre_save], sender=ItemInst)
def set_duration(sender, instance, **kwargs):
    delta = 0
    if instance.by_hour:
        delta = int(((instance.till_date-instance.from_date).seconds)/3600)
    else:
        delta = instance.till_date-instance.from_date
        delta = abs(delta.days)+1
    instance.duration = delta


@receiver([pre_save], sender=Payment)
def set_paid_zero(sender, instance, **kwargs):

    if sender == Payment and instance.pk != None and instance.amount > 0:

        details = PaymentDetail.objects.create(
            payment=instance, method=instance.method, amount=instance.amount, cheque_no=instance.cheque_no)
        details.save()

        if instance.status == 'Completed':
            order = Order.objects.get(id=instance.order.id)
            order.payment_status = 'Complete'
            order.save()

        instance.cheque_no = ''
        instance.amount = 0


"This function updates ItemInst's GST, CST, Total and Price fields"


@receiver(pre_save, sender=ItemInst)
def iteminst_update_fields(sender, instance, **kwargs):
    "Item Instance Calculation"
    # Calculate Price
    price = instance.item.price_by_hour if instance.by_hour else instance.item.price_by_day
    instance.price = iteminst_calculate_price(price, instance.quantity)

    # Calculate total without Tax
    instance.item_total = iteminst_calculate_itotal(
        instance.price, instance.duration)

    # Calculate Tax
    instance.gst = calculate_tax(instance.item.gst, instance.item_total)
    instance.cst = calculate_tax(instance.item.cst, instance.item_total)

    # Calculate Total with Tax
    instance.total = calculate_grand_total(
        instance.item_total, instance.cst, instance.gst)

    "Order Updates"
    #Check if item instance already exists
    #If it does, calculate difference between the current values and 
    #existing values and add that to the order
    if instance.id:
        item = ItemInst.objects.get(id=instance.id)
        instance.order.gst += instance.gst-item.gst
        instance.order.cst += instance.cst-item.cst
        instance.order.total += instance.item_total-item.item_total
        instance.order.grand_total += instance.total-item.total
        instance.order.save()
    else:
        instance.order.gst += instance.gst
        instance.order.cst += instance.cst
        instance.order.total += instance.item_total
        instance.order.grand_total += instance.total
        instance.order.save()


# Item Inst Helper Functions
def iteminst_calculate_price(price, quantity):
    return abs(price*quantity)


def iteminst_calculate_itotal(price, duration):
    return abs(price*duration)


def calculate_tax(tax_percent, total):
    tax = abs((tax_percent/100)*total)
    return tax


def calculate_grand_total(item_total, cst, gst):
    return abs(item_total+gst+cst)


"Update Order after Iteminst is deleted"


@receiver(pre_delete, sender=ItemInst)
def update_order(sender, instance, **kwargs):
    instance.order.gst -= instance.gst
    instance.order.cst -= instance.cst
    instance.order.total -= instance.item_total
    instance.order.grand_total -= instance.total
    instance.order.save()


@receiver(pre_delete, sender=Item)
def delete_item_image(sender, instance, **kwargs):
    res = delete_resources([instance.image])
    print(res)



