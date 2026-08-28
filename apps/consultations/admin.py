from django.contrib import admin

from .models import ConsultationRequest


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "doctor",
        "status",
        "created_at",
    )
    list_filter = ("doctor", "status", "created_at")
    search_fields = ("name", "phone", "email", "message")
    ordering = ("-created_at",)
    autocomplete_fields = ("doctor",)
    readonly_fields = ("created_at",)
    list_editable = ("status",)
    fieldsets = (
        (
            "اطلاعات درخواست",
            {
                "fields": (
                    "doctor",
                    "name",
                    "phone",
                    "email",
                    "message",
                    "status",
                )
            },
        ),
        ("تاریخ", {"fields": ("created_at",)}),
    )
