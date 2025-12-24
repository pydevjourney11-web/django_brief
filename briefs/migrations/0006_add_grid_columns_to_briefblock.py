from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("briefs", "0005_add_header_fields_to_briefquestion"),
    ]

    operations = [
        migrations.AddField(
            model_name="briefblock",
            name="grid_columns",
            field=models.PositiveIntegerField(default=0, verbose_name="Колонки (0=авто, 1..3 вручную)"),
        ),
    ]
