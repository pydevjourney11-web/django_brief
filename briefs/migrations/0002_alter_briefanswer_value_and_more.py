

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('briefs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='briefanswer',
            name='value',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='briefquestion',
            name='default_value',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
