from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("briefs", "0004_add_description_to_briefquestionoption"),
    ]

    operations = [
        migrations.AddField(
            model_name="briefquestion",
            name="show_in_header",
            field=models.BooleanField(default=False, verbose_name="Отобразить в шапке"),
        ),
        migrations.AddField(
            model_name="briefquestion",
            name="header_position",
            field=models.PositiveIntegerField(default=0, verbose_name="Порядок в шапке"),
        ),
        migrations.AddField(
            model_name="briefquestion",
            name="header_icon",
            field=models.CharField(max_length=255, blank=True, verbose_name="Иконка (путь к static)"),
        ),
    ]
