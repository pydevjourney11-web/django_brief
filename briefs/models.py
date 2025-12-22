import uuid

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Brief(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        COMPLETED = "completed", "Завершён"

    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    webhook_url = models.URLField(blank=True)
    is_template = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    completed_at = models.DateTimeField(null=True, blank=True)

    source_template = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_briefs",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title


class BriefBlock(TimeStampedModel):
    brief = models.ForeignKey(Brief, on_delete=models.CASCADE, related_name="blocks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("position", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("brief", "position"),
                name="uq_brief_block_position",
            )
        ]

    def __str__(self) -> str:
        return f"{self.brief.title}: {self.title}"


class BriefQuestion(TimeStampedModel):
    class QuestionType(models.TextChoices):
        STRING = "string", "Строка"
        TEXT = "text", "Текст"
        INT = "int", "Целое число"
        FLOAT = "float", "Число"
        SELECT = "select", "Выбор из списка"

    block = models.ForeignKey(BriefBlock, on_delete=models.CASCADE, related_name="questions")
    name = models.SlugField(max_length=128)
    type = models.CharField(max_length=16, choices=QuestionType.choices)
    label = models.CharField(max_length=255)
    placeholder = models.CharField(max_length=255, blank=True)
    default_value = models.CharField(max_length=255, null=True, blank=True)
    webhook_variable_name = models.SlugField(max_length=128, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("position", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("block", "position"),
                name="uq_block_question_position",
            ),
            models.UniqueConstraint(
                fields=("block", "name"),
                name="uq_block_question_name",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.block.title}: {self.label}"


class BriefQuestionOption(TimeStampedModel):
    question = models.ForeignKey(
        BriefQuestion,
        on_delete=models.CASCADE,
        related_name="options",
    )
    value = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("position", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("question", "position"),
                name="uq_question_option_position",
            ),
            models.UniqueConstraint(
                fields=("question", "value"),
                name="uq_question_option_value",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.question.label}: {self.label}"


class BriefAnswer(TimeStampedModel):
    brief = models.ForeignKey(Brief, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(BriefQuestion, on_delete=models.CASCADE, related_name="answers")
    value = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("brief", "question"),
                name="uq_brief_question_answer",
            )
        ]

    def __str__(self) -> str:
        return f"{self.brief.title} / {self.question.label}"
