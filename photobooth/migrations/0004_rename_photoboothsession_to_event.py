# Generated manually to rename PhotoboothSession to Event

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("photobooth", "0003_alter_photoboothsession_code"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE photobooth_photoboothsession RENAME TO photobooth_event;",
            reverse_sql="ALTER TABLE photobooth_event RENAME TO photobooth_photoboothsession;",
        ),
    ]
