from django.contrib.admin.options import ModelAdmin
from django.db.models.aggregates import Sum
from django.db.models.enums import IntegerChoices
from django.db.models.signals import post_save, pre_save, post_delete
from django.db import DefaultConnectionProxy, models
import datetime
from django.core.exceptions import ValidationError

class Customer(models.Model):
    name = models.CharField(max_length=30)
    address = models.TextField()
    phone = models.BigIntegerField()

    def __str__(self):
        return self.name
import os
from django.conf import settings

class Item(models.Model):
    name = models.CharField(max_length=30)
    price = models.PositiveIntegerField(verbose_name='Price(₹)')
    cst = models.PositiveIntegerField(verbose_name='CST(%)')
    gst = models.PositiveIntegerField(verbose_name='GST(%)')
    stock = models.PositiveIntegerField(default=0)
    rented = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='images/',blank=True)

    @property
    def available(self):
        return self.stock - self.rented
    

    def __str__(self):
        return self.name


class Order(models.Model):
    ORDER_STATUS = (
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Fulfilled', 'Fulfilled')
    )
    PAYMENT_STATUS = (
        ('Complete', 'Complete'),
        ('Incomplete', 'Incomplete'),
    )
    GST_STATUS = (
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    )
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name='customer name')
    from_date = models.DateField()
    till_date = models.DateField()
    status = models.CharField(
        max_length=10, choices=ORDER_STATUS, default='Pending')
    payment_status = models.CharField(
        max_length=10, default='Incomplete', choices=PAYMENT_STATUS)
    gst_status = models.CharField(
        max_length=10, default='Unpaid', choices=GST_STATUS)

    @property
    def total(self):
        total = 0
        if self.till_date == None:
            return 0

        for i in self.iteminst_set.filter(order=self.id):
            total += i.item_total
        return total

    @property
    def gst(self):
        gst = 0
        for i in self.iteminst_set.all():
            gst += i.gst
        self.total_gst = gst
        return gst

    @property
    def cst(self):
        cst = 0
        for i in self.iteminst_set.all():
            cst += i.cst
        self.total_cst = cst
        return cst

    @property
    def grand_total(self):
        g_total = 0
        for i in self.iteminst_set.filter(order=self.id):
            g_total += i.total
        return g_total

    

    def __str__(self):
        return f'Order#{self.id} {self.customer.name}'


class ItemInst(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    last_value = models.IntegerField(default=0)
    @property
    def duration(self):
        if self.order.till_date == None:
            return 0
        days = self.order.till_date-self.order.from_date
        return abs(days.days)

    @property
    def price(self):
        return abs(self.item.price * self.quantity)

    @property
    def item_total(self):
        return abs(self.price*self.duration)

    @property
    def item_price(self):
        return abs(self.item.price)

    @property
    def gst(self):
        return abs((self.item.gst/100)*self.item_total)

    @property
    def cst(self):
        return abs((self.item.cst/100)*self.item_total)

    @property
    def total(self):
        return abs(self.item_total+self.cst+self.gst)
    
    def clean(self) :
        item_invent = Item.objects.get(name = self.item.name)
        item_invent.rented += self.quantity-self.last_value
        if item_invent.rented > item_invent.stock:
            raise ValidationError('Item placed greater than in the inventory')
        item_invent.save()
        print(self.quantity-self.last_value)
        self.last_value = self.quantity
        print(self.order.status)
            
        

    def __str__(self):
        return str(self.item)


class Payment(models.Model):
    PAYMENT_METHOD = (
        ('Cheque', 'Cheque'),
        ('Cash', 'Cash')
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    date = models.DateField()
    method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD, blank=True)
    amount = models.PositiveIntegerField(
        default=0, blank=True, verbose_name='Amount(₹)')
    cheque_no = models.CharField(max_length=100, blank=True)

    def clean(self, *args, **kwargs):
        if self.amount > self.remaining:
            raise ValidationError(
                ('Amount entered is greater than remaining'), code='amount invalid')
        super(Payment, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Payment, self).save(*args, **kwargs)

    @property
    def remaining(self):
        return abs(self.order.grand_total - self.paid)

    @property
    def gst(self):
        return self.order.gst

    @property
    def cst(self):
        return self.order.cst

    @property
    def status(self):
        if self.paid - self.order.grand_total == 0.0:
            return 'Completed'
        elif self.paid == 0.0:
            return 'Unpaid'
        else:
            return 'Pending'

    @property
    def order_status(self):
        return self.order.status

    @property
    def paid(self):
        total = 0
        for i in self.paymentdetail_set.all():
            total += i.amount
        return total

    def __str__(self):
        return f'Order#{self.order.id} {self.order.customer.name}'

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    comment = models.TextField()
    def __str__(self):
        return self.name
class PaymentDetail(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    method = models.CharField(max_length=100, default='Cash')
    amount = models.IntegerField(default=0)
    cheque_no = models.CharField(max_length=100, blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Payment Details'

    def __str__(self) -> str:
        return str(self.payment)


class TaxSummary(Order):
    class Meta:
        proxy = True
        verbose_name = 'Tax Summary'
        verbose_name_plural = 'Tax Summary'


class PaymentSummary(Payment):
    class Meta:
        proxy = True
        verbose_name = 'Payment Summary'
        verbose_name_plural = 'Payment Summary'

class Inventory(Item):
    
    class Meta:
        proxy=True
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventory'


def create_payment(sender, instance, **kwargs):

    if sender == Order:
        if Payment.objects.filter(order=instance).count() >= 1:
            return
        else:
            payment = Payment.objects.create(
                order=instance, date=instance.from_date)
            payment.save()

    

def set_paid_zero(sender, instance, **kwargs):

    if sender == Payment:
        if instance.pk != None:

            if instance.amount > 0:
                details = PaymentDetail.objects.create(
                    payment=instance, method=instance.method, amount=instance.amount, cheque_no=instance.cheque_no)
                details.save()

                if instance.status == 'Completed':
                    order = Order.objects.get(id=instance.order.id)
                    order.payment_status = 'Complete'
                    order.save()

                instance.cheque_no = ''
                instance.amount = 0

def update_inventory(sender, instance, **kwargs):
    item_invent = Inventory.objects.get(id = instance.item.pk)
    if instance.order.status != "Fulfilled":
        item_invent.rented-=instance.quantity
        item_invent.save()
    


post_save.connect(create_payment, sender=Order)
pre_save.connect(set_paid_zero, sender=Payment)
post_delete.connect(update_inventory, sender=ItemInst)

