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

    inlines = (BriefBlockInline,)

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
    ordering = ("brief", "position", "id")
    readonly_fields = ("created_at", "updated_at")

    inlines = (BriefQuestionInline,)


class BriefQuestionOptionInline(admin.TabularInline):
    model = BriefQuestionOption
    extra = 0
    fields = ("position", "value", "label")
    ordering = ("position", "id")


@admin.register(BriefQuestion)
class BriefQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "block", "position", "name", "type", "label")
    list_filter = ("type", "block__brief")
    search_fields = ("name", "label", "block__title", "block__brief__title")
    ordering = ("block", "position", "id")
    readonly_fields = ("created_at", "updated_at")

    inlines = (BriefQuestionOptionInline,)


@admin.register(BriefQuestionOption)
class BriefQuestionOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "position", "value", "label")
    list_filter = ("question__block__brief",)
    search_fields = ("value", "label", "question__label")
    ordering = ("question", "position", "id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(BriefAnswer)
class BriefAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "brief", "question", "updated_at")
    list_filter = ("brief", "question__type")
    search_fields = ("brief__title", "question__label", "question__name")
    readonly_fields = ("created_at", "updated_at")
