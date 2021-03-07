from django.db.models.aggregates import Count, Sum
from django.http.response import HttpResponse
from django.shortcuts import render
from home.models import Inventory, Item,Customer,Order, Payment, Feedback
from django.contrib.auth.decorators import login_required
import datetime
import random

def index(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        comments = request.POST.get('comments')
        feedback = Feedback.objects.create(name=name,email=email,comment=comments)
        feedback.save()    

    feedbacks = list(Feedback.objects.all())
    random_items = random.sample(feedbacks, 3)
    print(random_items)
    items = Item.objects.all()
    return render(request,'home/index.html',context={'items':items,'feedbacks':random_items})

@login_required(login_url='/admin/login/?next=/admin/')
def dashboard(request):
    
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    gst_unpaid = 0
    cst_unpaid = 0
    for payment in Payment.objects.all():
        if payment.status == 'Completed':
            if payment.order.gst_status == 'Unpaid':
                gst_unpaid+=payment.gst
                cst_unpaid+=payment.cst

    dt = datetime.date.today()
    upcoming_orders = []
    todays_orders = Order.objects.filter(from_date=str(dt)).count()
    for order in Order.objects.all():
        if order.from_date > dt:
            upcoming_orders.append(order)

    orders_month_count = []
    for month in range(1,13):
        orders_month_count.append(Order.objects.filter(from_date__month=str(month)).count())
    print(orders_month_count)
    inventory = Inventory.objects.all()
    context={
        'total_customers':total_customers,
        'total_orders':total_orders,
        'gst_unpaid':gst_unpaid,
        'cst_unpaid':cst_unpaid,
        'todays_orders':todays_orders,
        'upcoming_orders':len(upcoming_orders),
        'inventory':inventory,
        'orders_month_count':orders_month_count
    }
    return render(request,'home/dashboard.html',context=context)