

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('briefs', '0002_alter_briefanswer_value_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brief',
            options={'ordering': ('-created_at',), 'verbose_name': 'Бриф', 'verbose_name_plural': 'Брифы'},
        ),
        migrations.AlterModelOptions(
            name='briefanswer',
            options={'verbose_name': 'Ответ', 'verbose_name_plural': 'Ответы'},
        ),
        migrations.AlterModelOptions(
            name='briefblock',
            options={'ordering': ('position', 'id'), 'verbose_name': 'Блок', 'verbose_name_plural': 'Блоки'},
        ),
        migrations.AlterModelOptions(
            name='briefquestion',
            options={'ordering': ('position', 'id'), 'verbose_name': 'Вопрос', 'verbose_name_plural': 'Вопросы'},
        ),
        migrations.AlterModelOptions(
            name='briefquestionoption',
            options={'ordering': ('position', 'id'), 'verbose_name': 'Опция', 'verbose_name_plural': 'Опции'},
        ),
        migrations.AddField(
            model_name='briefquestion',
            name='is_multiple',
            field=models.BooleanField(default=False, verbose_name='Множественный выбор'),
        ),
        migrations.AlterField(
            model_name='brief',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения'),
        ),
        migrations.AlterField(
            model_name='brief',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='brief',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='brief',
            name='is_template',
            field=models.BooleanField(default=False, help_text='Отметьте, если этот бриф используется как шаблон', verbose_name='Шаблон'),
        ),
        migrations.AlterField(
            model_name='brief',
            name='public_uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='Уникальная публичная ссылка для заполнения брифа', unique=True, verbose_name='Публичный UUID'),
        ),
        migrations.AlterField(
            model_name='brief',
            name='source_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='derived_briefs', to='briefs.brief', verbose_name='Исходный шаблон'),
        ),
        migrations.AlterField(
            model_name='brief',
            name='status',
            field=models.CharField(choices=[('draft', 'Черновик'), ('completed', 'Завершён')], default='draft', max_length=16, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='brief',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='brief',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Обновлено'),
        ),
        migrations.AlterField(
            model_name='brief',
            name='webhook_url',
            field=models.URLField(blank=True, help_text='Адрес, на который отправятся данные после отправки брифа', verbose_name='URL вебхука'),
        ),
        migrations.AlterField(
            model_name='briefanswer',
            name='brief',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='briefs.brief', verbose_name='Бриф'),
        ),
        migrations.AlterField(
            model_name='briefanswer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='briefanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='briefs.briefquestion', verbose_name='Вопрос'),
        ),
        migrations.AlterField(
            model_name='briefanswer',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Обновлено'),
        ),
        migrations.AlterField(
            model_name='briefanswer',
            name='value',
            field=models.TextField(blank=True, null=True, verbose_name='Ответ'),
        ),
        migrations.AlterField(
            model_name='briefblock',
            name='brief',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='briefs.brief', verbose_name='Бриф'),
        ),
        migrations.AlterField(
            model_name='briefblock',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='briefblock',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='briefblock',
            name='position',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок'),
        ),
        migrations.AlterField(
            model_name='briefblock',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='briefblock',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Обновлено'),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='briefs.briefblock', verbose_name='Блок'),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='default_value',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Значение по умолчанию'),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='label',
            field=models.CharField(max_length=255, verbose_name='Текст вопроса'),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='name',
            field=models.SlugField(help_text='Латинское имя для связи и экспорта (slug)', max_length=128, verbose_name='Системное имя'),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='placeholder',
            field=models.CharField(blank=True, max_length=255, verbose_name='Плейсхолдер'),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='position',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок'),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='type',
            field=models.CharField(choices=[('string', 'Строка'), ('text', 'Текст'), ('int', 'Целое число'), ('float', 'Число'), ('select', 'Выбор из списка')], max_length=16, verbose_name='Тип вопроса'),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Обновлено'),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='webhook_variable_name',
            field=models.SlugField(blank=True, help_text='Ключ поля в JSON при отправке вебхука', max_length=128, verbose_name='Имя переменной для вебхука'),
        ),
        migrations.AlterField(
            model_name='briefquestionoption',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='briefquestionoption',
            name='label',
            field=models.CharField(max_length=255, verbose_name='Отображаемый текст'),
        ),
        migrations.AlterField(
            model_name='briefquestionoption',
            name='position',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок'),
        ),
        migrations.AlterField(
            model_name='briefquestionoption',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='briefs.briefquestion', verbose_name='Вопрос'),
        ),
        migrations.AlterField(
            model_name='briefquestionoption',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Обновлено'),
        ),
        migrations.AlterField(
            model_name='briefquestionoption',
            name='value',
            field=models.CharField(max_length=255, verbose_name='Значение'),
        ),
    ]
