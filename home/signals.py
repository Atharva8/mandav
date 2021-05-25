from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from home.models import ItemInst, Payment, Order, PaymentDetail


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
