from django.contrib import admin

from .models import Membership, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "name",
        "start_date",
        "end_date",
        "amount",
        "status",
    )

    search_fields = (
        "client__user__username",
        "client__user__email",
        "name",
    )

    list_filter = (
        "status",
        "start_date",
        "end_date",
    )

    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "membership",
        "amount",
        "payment_date",
        "payment_method",
        "status",
        "transaction_id",
    )

    search_fields = (
        "membership__client__user__username",
        "membership__client__user__email",
        "transaction_id",
    )

    list_filter = (
        "status",
        "payment_method",
        "payment_date",
    )

    ordering = (
        "-payment_date",
    )