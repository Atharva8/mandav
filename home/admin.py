from django.contrib import admin, messages
from django.http import response
from .models import Customer, Order, Item, ItemInst, Payment, PaymentDetail, TaxSummary, PaymentSummary, Inventory
from rangefilter.filter import DateRangeFilter
from django.urls import path
from django.contrib.auth.models import Group, User
from django.utils.translation import ngettext


class ItemInstInline(admin.TabularInline):
    model = ItemInst
    readonly_fields = ('item_price', 'duration',
                       'item_total', 'gst', 'cst', 'total',)
    exclude = ('last_value',)
    extra = 1


class OrderAdmin(admin.ModelAdmin):

    inlines = [
        ItemInstInline,
    ]

    fieldsets = (
        ("", {
            'fields': ('customer', ('from_date', 'till_date'), 'total', 'gst', 'cst', 'grand_total', 'status', 'payment_status', 'gst_status')
        }),
    )

    readonly_fields = ('total', 'gst', 'cst', 'grand_total',
                       'payment_status', 'gst_status')


class PaymentAdmin(admin.ModelAdmin):

    readonly_fields = ('remaining', 'cst', 'gst',
                       'status', 'paid', 'order_status')


def make_gst(modeladmin, request, queryset):
    updated = queryset.update(gst_status='Paid')
    modeladmin.message_user(request, ngettext(
        '%d order was successfull marked as gst paid.',
        '%d orders was successfull marked as gst paid.',
        updated,
    ) % updated, messages.SUCCESS)


make_gst.short_description = "Pay Tax"


class TaxSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/gst_summary_change_list.html'
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

        total_gst = 0
        total_cst = 0
        for i in qs:
            total_gst += i.gst
            total_cst += i.cst

        gst = []
        cst = []
        order_id = []
        item_total = []
        gst_status = []
        for q in qs:
            gst.append(q.gst)
            cst.append(q.cst)
            order_id.append(q.id)
            item_total.append(q.total)
            gst_status.append(q.gst_status)

        response.context_data['details'] = zip(order_id, gst, cst, item_total,gst_status)
        response.context_data['gst_total'] = total_gst
        response.context_data['cst_total'] = total_cst
        return response


class PaymentSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/pay_summary_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('yo/<int:order>', self.changelist_view, name='yo'),
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

        order = Order.objects.get(id=order)
        response.context_data['payments'] = qs.get(
            order=order).paymentdetail_set.all()
        response.context_data['order'] = order
        return response

    def get_model_perms(self, request): return {}


class InventoryAdmin(admin.ModelAdmin):
    fields = ('stock','rented','available',)
    readonly_fields = ('rented','available',)

class ItemAdmin(admin.ModelAdmin):
    fields = ('name','price','gst','cst')
admin.site.register(TaxSummary, TaxSummaryAdmin)
admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemInst)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentDetail)
admin.site.register(PaymentSummary, PaymentSummaryAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(Inventory, InventoryAdmin)
admin.site.site_header = "Event Rental Admin"
admin.site.site_title = "Event Rental Portal"
admin.site.index_title = "Event Rental"
