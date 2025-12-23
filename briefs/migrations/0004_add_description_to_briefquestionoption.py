from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("briefs", "0003_alter_brief_options_alter_briefanswer_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="briefquestionoption",
            name="description",
            field=models.TextField(
                verbose_name="Пояснение",
                blank=True,
                default="",
            ),
            preserve_default=False,
        ),
    ]
