from django.contrib import admin, messages
from django.http import response
from .models import Customer, Feedback, Order, Item, ItemInst, Payment, PaymentDetail, TaxSummary, PaymentSummary, Inventory
from rangefilter.filter import DateRangeFilter
from django.urls import path
from django.contrib.auth.models import Group, User
from django.utils.translation import ngettext
from home.forms import ItemInstForm, OrderForm

class ItemInstInline(admin.TabularInline):
    form = ItemInstForm
    model = ItemInst
    readonly_fields = ('price_by_hour','price_by_day', 'duration',
                       'item_total', 'gst', 'cst', 'total','price')
    exclude = ('last_value',)
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    change_list_template = 'admin/order_summary_change_list.html'
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

    def changelist_view(self, request, extra_content=None):
        response = super().changelist_view(
            request,
            extra_content
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        return response


class PaymentAdmin(admin.ModelAdmin):
    change_list_template = 'admin/payment_change_list.html'
    readonly_fields = ('order', 'remaining', 'cst', 'gst',
                       'status', 'paid', 'order_status')

    def changelist_view(self, request, extra_content=None):
        response = super().changelist_view(
            request,
            extra_content
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        return response


def make_gst(modeladmin, request, queryset):
    updated = queryset.update(gst_status='Paid')
    modeladmin.message_user(request, ngettext(
        '%d order was successfully marked as GST paid.',
        '%d orders was successfully marked as GST paid.',
        updated,
    ) % updated, messages.SUCCESS)


make_gst.short_description = "Pay Tax"

#TODO

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
        customer_name = []
        grand_total = []
        for q in qs:
            gst.append(q.gst)
            cst.append(q.cst)
            order_id.append(q.id)
            item_total.append(q.total)
            gst_status.append(q.gst_status)
            customer_name.append(q.customer.name)
            grand_total.append(q.grand_total)

        response.context_data['details'] = zip(
            order_id, gst, cst, item_total, gst_status, customer_name, grand_total)
        response.context_data['gst_total'] = total_gst
        response.context_data['cst_total'] = total_cst
        response.context_data
        return response

    def has_add_permission(self, request):
        return False


class PaymentSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/pay_summary_change_list.html'

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

        order = Order.objects.get(id=order)
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
    change_list_template = 'admin/inventory_change_list.html'
    def changelist_view(self, request, extra_content=None):
        response = super().changelist_view(
            request,
            extra_content
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        return response


class ItemAdmin(admin.ModelAdmin):
    fields = ('name', 'price_by_hour', 'gst', 'cst', 'image','price_by_day')


class FeedbackAdmin(admin.ModelAdmin):
    pass


PRADNYA_DECORATORS = "Pradnya Decorators"
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(TaxSummary, TaxSummaryAdmin)
admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemInst)
admin.site.register(Payment, PaymentAdmin)
# admin.site.register(PaymentDetail)
admin.site.register(PaymentSummary, PaymentSummaryAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(Inventory, InventoryAdmin)
admin.site.site_header = PRADNYA_DECORATORS
admin.site.site_title = PRADNYA_DECORATORS
admin.site.index_title = PRADNYA_DECORATORS
