from django.contrib import admin, messages
from django.core.checks.messages import  ERROR
from django.core.exceptions import ObjectDoesNotExist
from django.http import response
from django.shortcuts import redirect
from home.models import *
from rangefilter.filter import DateRangeFilter
from django.urls import path
from django.contrib.auth.models import Group, User
from django.utils.translation import ngettext
from home.forms import ItemInstForm, OrderForm
from django.db.models import Sum

class ItemInstInline(admin.TabularInline):
    form = ItemInstForm
    model = ItemInst
    readonly_fields = ('price_by_hour', 'price_by_day', 'duration',
                       'item_total', 'gst', 'cst', 'total', 'price')
    exclude = ('last_value',)
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    change_list_template = 'admin/order_summary.html'
    inlines = [
        ItemInstInline,
    ]

    fieldsets = (
        ("", {
            'fields': ('customer', ('from_date', 'till_date'), 'total', 'discount','calculated_discount','gst', 'cst', 'grand_total', 'status', 'payment_status', 'gst_status')
        }),
    )

    readonly_fields = ('total', 'gst', 'cst', 'grand_total',
                       'payment_status', 'gst_status','calculated_discount')


class PaymentAdmin(admin.ModelAdmin):
    change_list_template = 'admin/payment_summary.html'
    readonly_fields = ('order', 'remaining', 'cst', 'gst',
                       'status', 'paid', 'order_status')


def make_gst(modeladmin, request, queryset):
    updated = queryset.update(gst_status='Paid')
    modeladmin.message_user(request, ngettext(
        '%d order was successfully marked as GST paid.',
        '%d orders was successfully marked as GST paid.',
        updated,
    ) % updated, messages.SUCCESS)


make_gst.short_description = "Pay Tax"


class TaxSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/tax_summary.html'
    list_filter = (
        ('from_date', DateRangeFilter),
        ('status'),
        ('payment_status'),
        ('gst_status')
    )
    actions = [make_gst]

    def changelist_view(self, request, extra_content=None):
        response = super().changelist_view(
            request,
            extra_context=extra_content
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        
        response.context_data['total_gst'] = qs.aggregate(Sum('gst'))['gst__sum']
        response.context_data['total_cst'] = qs.aggregate(Sum('cst'))['cst__sum']
        return response

    def has_add_permission(self, request):
        return False


class PaymentSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/invoice.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('paysummary/<int:order>',
                 self.changelist_view, name='paysummary'),
        ]
        return my_urls + urls

    def changelist_view(self, request, extra_content=None, order=0):
        response = super().changelist_view(
            request,
            extra_context=extra_content
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        
        response.context_data['title'] = 'Invoice'
        try:
            order = Order.objects.get(id=order)
        except Order.DoesNotExist:
            messages.add_message(request=request,level=ERROR,message='Next order does not exist')
            
            return redirect('/admin/home/taxsummary/')
        
        response.context_data['payments'] = qs.get(
            order=order).paymentdetail_set.all()
        response.context_data['order'] = order
        response.context_data['iteminst'] = order.iteminst_set.all()
        return response

    def get_model_perms(self, request): return {}

    def has_add_permission(self, request):
        return False


class InventoryAdmin(admin.ModelAdmin):
    fields = ('name', 'stock', 'rented', 'available',)
    readonly_fields = ('name', 'rented', 'available',)
    change_list_template = 'admin/inventory_summary.html'


class ItemAdmin(admin.ModelAdmin):
    fields = ('name', 'price_by_hour', 'price_by_day','gst', 'cst', 'image', )


PRADNYA_DECORATORS = "Pradnya Decorators"
admin.site.register(Feedback)
admin.site.register(TaxSummary, TaxSummaryAdmin)
admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemInst)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentSummary, PaymentSummaryAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(Inventory, InventoryAdmin)
admin.site.site_header = PRADNYA_DECORATORS
admin.site.site_title = PRADNYA_DECORATORS
admin.site.index_title = PRADNYA_DECORATORS
