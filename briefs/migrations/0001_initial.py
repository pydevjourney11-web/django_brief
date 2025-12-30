
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brief',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('public_uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('webhook_url', models.URLField(blank=True)),
                ('is_template', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('completed', 'Завершён')], default='draft', max_length=16)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('source_template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='derived_briefs', to='briefs.brief')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='BriefBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('position', models.PositiveIntegerField(default=0)),
                ('brief', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='briefs.brief')),
            ],
            options={
                'ordering': ('position', 'id'),
            },
        ),
        migrations.CreateModel(
            name='BriefQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.SlugField(max_length=128)),
                ('type', models.CharField(choices=[('string', 'Строка'), ('text', 'Текст'), ('int', 'Целое число'), ('float', 'Число'), ('select', 'Выбор из списка')], max_length=16)),
                ('label', models.CharField(max_length=255)),
                ('placeholder', models.CharField(blank=True, max_length=255)),
                ('default_value', models.CharField(blank=True, null=True, max_length=255)),
                ('webhook_variable_name', models.SlugField(blank=True, max_length=128)),
                ('position', models.PositiveIntegerField(default=0)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='briefs.briefblock')),
            ],
            options={
                'ordering': ('position', 'id'),
            },
        ),
        migrations.CreateModel(
            name='BriefQuestionOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255)),
                ('position', models.PositiveIntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='briefs.briefquestion')),
            ],
            options={
                'ordering': ('position', 'id'),
            },
        ),
        migrations.CreateModel(
            name='BriefAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.TextField(blank=True, null=True)),
                ('brief', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='briefs.brief')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='briefs.briefquestion')),
            ],
        ),
        migrations.AddConstraint(
            model_name='briefquestionoption',
            constraint=models.UniqueConstraint(fields=('question', 'position'), name='uq_question_option_position'),
        ),
        migrations.AddConstraint(
            model_name='briefquestionoption',
            constraint=models.UniqueConstraint(fields=('question', 'value'), name='uq_question_option_value'),
        ),
        migrations.AddConstraint(
            model_name='briefquestion',
            constraint=models.UniqueConstraint(fields=('block', 'position'), name='uq_block_question_position'),
        ),
        migrations.AddConstraint(
            model_name='briefquestion',
            constraint=models.UniqueConstraint(fields=('block', 'name'), name='uq_block_question_name'),
        ),
        migrations.AddConstraint(
            model_name='briefblock',
            constraint=models.UniqueConstraint(fields=('brief', 'position'), name='uq_brief_block_position'),
        ),
        migrations.AddConstraint(
            model_name='briefanswer',
            constraint=models.UniqueConstraint(fields=('brief', 'question'), name='uq_brief_question_answer'),
        ),
    ]
