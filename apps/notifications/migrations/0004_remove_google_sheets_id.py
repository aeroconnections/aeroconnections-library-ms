from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_librarysettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='librarysettings',
            name='google_sheets_id',
        ),
    ]
