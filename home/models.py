from django.db.models.aggregates import Sum
from django.db import models
from django.core.exceptions import ValidationError

class Customer(models.Model):
    name = models.CharField(max_length=30)
    address = models.TextField()
    phone = models.BigIntegerField()

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=30)
    price_by_day = models.PositiveIntegerField(default=0,verbose_name='Price by day(₹)')
    price_by_hour = models.PositiveIntegerField(default=0,verbose_name='Price by hour(₹)')
    cst = models.PositiveIntegerField(verbose_name='CST(%)')
    gst = models.PositiveIntegerField(verbose_name='GST(%)')
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='images/',blank=True)

    @property
    def rented(self):
        item = ItemInst.objects.filter(item=self.id).exclude(order__status="Fulfilled").aggregate(Sum('quantity'))
        if item['quantity__sum'] is None:
            return 0

        return item['quantity__sum']
    @property
    def available(self):
        item = ItemInst.objects.filter(item=self.id).exclude(order__status="Fulfilled").aggregate(Sum('quantity'))
        total_sum = item['quantity__sum']
        if  total_sum is None:
            total_sum = 0

        return self.stock-self.rented


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
    ITEM_STATUS = (
        ('Incomplete', 'Incomplete'),
        ('Complete', 'Complete'),
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    last_value = models.IntegerField(default=0)
    by_hour = models.BooleanField(default=False)
    from_date = models.DateTimeField()
    till_date = models.DateTimeField()
    duration = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=15, default='Incomplete', choices=ITEM_STATUS)

    @property
    def price_by_day(self):
        return self.item.price_by_day

    @property
    def price_by_hour(self):
        return self.item.price_by_hour
        
    @property
    def price(self):
        if not self.by_hour:
            return abs(self.item.price_by_day * self.quantity)
        return abs(self.item.price_by_hour * self.quantity)

    @property
    def item_total(self):
        return abs(self.price*self.duration)

    @property
    def gst(self):
        return calculate_tax(self.item.gst,self.item_total)

    @property
    def cst(self):
        return calculate_tax(self.item.cst,self.item_total)

    @property
    def total(self):
        return abs(self.item_total+self.cst+self.gst)
            
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

#TODO

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


def calculate_tax(tax_percent, total):
    tax = abs((tax_percent/100)*total)
    return tax