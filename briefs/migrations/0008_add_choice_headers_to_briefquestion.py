from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("briefs", "0007_add_repeater_fields_to_briefquestion"),
    ]

    operations = [
        migrations.AddField(
            model_name="briefquestion",
            name="choices_header_left",
            field=models.CharField(blank=True, max_length=255, verbose_name="Заголовок левой колонки (мультивыбор)"),
        ),
        migrations.AddField(
            model_name="briefquestion",
            name="choices_header_right",
            field=models.CharField(blank=True, max_length=255, verbose_name="Заголовок правой колонки (мультивыбор)"),
        ),
    ]
