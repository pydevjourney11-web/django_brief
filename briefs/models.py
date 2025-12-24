import uuid

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        abstract = True


class Brief(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        COMPLETED = "completed", "Завершён"

    public_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="Публичный UUID",
        help_text="Уникальная публичная ссылка для заполнения брифа",
    )
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    webhook_url = models.URLField(
        blank=True,
        verbose_name="URL вебхука",
        help_text="Адрес, на который отправятся данные после отправки брифа",
    )
    is_template = models.BooleanField(
        default=False,
        verbose_name="Шаблон",
        help_text="Отметьте, если этот бриф используется как шаблон",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Статус",
    )
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")

    source_template = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_briefs",
        verbose_name="Исходный шаблон",
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Бриф"
        verbose_name_plural = "Брифы"

    def __str__(self) -> str:
        return self.title


class BriefBlock(TimeStampedModel):
    brief = models.ForeignKey(Brief, on_delete=models.CASCADE, related_name="blocks", verbose_name="Бриф")
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    grid_columns = models.PositiveIntegerField(default=0, verbose_name="Колонки (0=авто, 1..3 вручную)")
    position = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ("position", "id")
        verbose_name = "Блок"
        verbose_name_plural = "Блоки"
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

    block = models.ForeignKey(BriefBlock, on_delete=models.CASCADE, related_name="questions", verbose_name="Блок")
    name = models.SlugField(
        max_length=128,
        verbose_name="Системное имя",
        help_text="Латинское имя для связи и экспорта (slug)",
    )
    type = models.CharField(max_length=16, choices=QuestionType.choices, verbose_name="Тип вопроса")
    is_multiple = models.BooleanField(default=False, verbose_name="Множественный выбор")
    show_in_header = models.BooleanField(default=False, verbose_name="Отобразить в шапке")
    header_position = models.PositiveIntegerField(default=0, verbose_name="Порядок в шапке")
    header_icon = models.CharField(max_length=255, blank=True, verbose_name="Иконка (путь к static)")
    repeater_schema = models.JSONField(default=list, blank=True, verbose_name="Схема репитера (список колонок)")
    repeater_min_rows = models.PositiveIntegerField(default=5, verbose_name="Мин. строк в репитере")
    choices_header_left = models.CharField(max_length=255, blank=True, verbose_name="Заголовок левой колонки (мультивыбор)")
    choices_header_right = models.CharField(max_length=255, blank=True, verbose_name="Заголовок правой колонки (мультивыбор)")
    label = models.CharField(max_length=255, verbose_name="Текст вопроса")
    placeholder = models.CharField(max_length=255, blank=True, verbose_name="Плейсхолдер")
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="Значение по умолчанию")
    webhook_variable_name = models.SlugField(
        max_length=128,
        blank=True,
        verbose_name="Имя переменной для вебхука",
        help_text="Ключ поля в JSON при отправке вебхука",
    )
    position = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ("position", "id")
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
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
        verbose_name="Вопрос",
    )
    value = models.CharField(max_length=255, verbose_name="Значение")
    label = models.CharField(max_length=255, verbose_name="Отображаемый текст")
    description = models.TextField(blank=True, verbose_name="Пояснение")
    position = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ("position", "id")
        verbose_name = "Опция"
        verbose_name_plural = "Опции"
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
    brief = models.ForeignKey(Brief, on_delete=models.CASCADE, related_name="answers", verbose_name="Бриф")
    question = models.ForeignKey(BriefQuestion, on_delete=models.CASCADE, related_name="answers", verbose_name="Вопрос")
    value = models.TextField(null=True, blank=True, verbose_name="Ответ")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        constraints = [
            models.UniqueConstraint(
                fields=("brief", "question"),
                name="uq_brief_question_answer",
            )
        ]

    def __str__(self) -> str:
        return f"{self.brief.title} / {self.question.label}"
