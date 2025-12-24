from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Brief,
    BriefAnswer,
    BriefBlock,
    BriefQuestion,
    BriefQuestionOption,
)

admin.site.site_header = "Управление брифами"
admin.site.site_title = "Админка брифов"
admin.site.index_title = "Главная админки"


class BriefBlockInline(admin.TabularInline):
    model = BriefBlock
    extra = 0
    fields = ("position", "title", "description")
    ordering = ("position", "id")


@admin.register(Brief)
class BriefAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "is_template",
        "status",
        "completed_at",
        "public_link",
        "progress_link",
        "public_uuid",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_template", "status", "created_at")
    search_fields = ("title", "public_uuid")
    readonly_fields = ("public_uuid", "created_at", "updated_at", "completed_at")
    empty_value_display = "—"

    fieldsets = (
        (
            "Основное",
            {
                "fields": (
                    "title",
                    "description",
                    "status",
                    "is_template",
                    "source_template",
                )
            },
        ),
        (
            "Публичная ссылка",
            {"fields": ("public_uuid",)},
        ),
        (
            "Автоматизация",
            {"fields": ("webhook_url",), "classes": ("collapse",)},
        ),
        (
            "Системные",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "completed_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = (BriefBlockInline,)

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)

        return (
            (
                "Основное",
                {
                    "fields": (
                        "title",
                        "description",
                        "status",
                        "is_template",
                        "source_template",
                    )
                },
            ),
            (
                "Публичная ссылка",
                {"fields": ("public_uuid",)},
            ),
        )

    @admin.display(description="Публичная ссылка")
    def public_link(self, obj: Brief) -> str:
        url = reverse("briefs:brief_fill", args=(obj.public_uuid,))
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">открыть</a>', url)

    @admin.display(description="Заполненность")
    def progress_link(self, obj: Brief) -> str:
        url = reverse("briefs_admin:admin_brief_progress", args=(obj.pk,))
        return format_html('<a href="{}">смотреть</a>', url)


class BriefQuestionInline(admin.TabularInline):
    model = BriefQuestion
    extra = 0
    fields = (
        "position",
        "name",
        "type",
        "is_multiple",
        "show_in_header",
        "header_position",
        "header_icon",
        "label",
        "placeholder",
        "default_value",
        "webhook_variable_name",
    )
    ordering = ("position", "id")


@admin.register(BriefBlock)
class BriefBlockAdmin(admin.ModelAdmin):
    list_display = ("id", "brief", "position", "title")
    list_filter = ("brief",)
    search_fields = ("title", "brief__title")
    list_editable = ("position",)
    ordering = ("brief", "position", "id")
    readonly_fields = ("created_at", "updated_at")
    empty_value_display = "—"

    inlines = (BriefQuestionInline,)


class BriefQuestionOptionInline(admin.TabularInline):
    model = BriefQuestionOption
    extra = 0
    fields = ("position", "value", "label", "description")
    ordering = ("position", "id")


@admin.register(BriefQuestion)
class BriefQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "block", "position", "name", "type", "is_multiple", "show_in_header", "header_position", "label")
    list_filter = ("type", "block__brief")
    search_fields = ("name", "label", "block__title", "block__brief__title")
    list_editable = ("position",)
    ordering = ("block", "position", "id")
    readonly_fields = ("created_at", "updated_at")
    empty_value_display = "—"
    prepopulated_fields = {"name": ("label",)}

    inlines = (BriefQuestionOptionInline,)


@admin.register(BriefQuestionOption)
class BriefQuestionOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "position", "value", "label", "description")
    list_filter = ("question__block__brief",)
    search_fields = ("value", "label", "description", "question__label")
    ordering = ("question", "position", "id")
    readonly_fields = ("created_at", "updated_at")
    empty_value_display = "—"


@admin.register(BriefAnswer)
class BriefAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "brief", "question", "updated_at")
    list_filter = ("brief", "question__type")
    search_fields = ("brief__title", "question__label", "question__name")
    readonly_fields = ("created_at", "updated_at")
    empty_value_display = "—"
