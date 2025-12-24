from django.db import migrations, models


def set_default_schema(apps, schema_editor):
    BriefQuestion = apps.get_model('briefs', 'BriefQuestion')
    for q in BriefQuestion.objects.filter(name='competitors'):
        try:
            q.repeater_schema = [
                {"key": "url", "label": "Ссылка на сайт", "placeholder": "https://..."},
                {"key": "comment", "label": "Комментарий", "placeholder": "Комментарий"},
            ]
            if not q.repeater_min_rows:
                q.repeater_min_rows = 5
            q.save(update_fields=["repeater_schema", "repeater_min_rows"])
        except Exception:
            # best-effort; skip on error to avoid blocking migration
            pass


class Migration(migrations.Migration):

    dependencies = [
        ("briefs", "0006_add_grid_columns_to_briefblock"),
    ]

    operations = [
        migrations.AddField(
            model_name="briefquestion",
            name="repeater_schema",
            field=models.JSONField(blank=True, default=list, verbose_name="Схема репитера (список колонок)"),
        ),
        migrations.AddField(
            model_name="briefquestion",
            name="repeater_min_rows",
            field=models.PositiveIntegerField(default=5, verbose_name="Мин. строк в репитере"),
        ),
        migrations.RunPython(set_default_schema, reverse_code=migrations.RunPython.noop),
    ]
