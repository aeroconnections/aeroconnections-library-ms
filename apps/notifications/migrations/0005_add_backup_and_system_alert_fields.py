from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_remove_google_sheets_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='librarysettings',
            name='backup_enabled',
            field=models.BooleanField(default=False, help_text='Enable automatic daily backups'),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='backup_hour',
            field=models.PositiveIntegerField(default=2, help_text='Hour of day for backup (0-23)'),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='backup_mount_options',
            field=models.CharField(blank=True, help_text='Mount options (optional)', max_length=500),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='backup_mount_path',
            field=models.CharField(blank=True, help_text='Mount path for NFS or SMB (e.g., /mnt/backup or //server/share)', max_length=500),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='backup_mount_type',
            field=models.CharField(choices=[('local', 'Local'), ('nfs', 'NFS'), ('smb', 'SMB/CIFS')], default='local', max_length=10),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='backup_retention_days',
            field=models.PositiveIntegerField(default=14, help_text='Number of days to keep backups'),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='smb_domain',
            field=models.CharField(blank=True, help_text='SMB domain (optional)', max_length=100),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='smb_password',
            field=models.CharField(blank=True, help_text='SMB password', max_length=100),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='smb_server',
            field=models.CharField(blank=True, help_text='SMB server address (e.g., //server/library-backups)', max_length=255),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='smb_username',
            field=models.CharField(blank=True, help_text='SMB username', max_length=100),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='system_alert_enabled',
            field=models.BooleanField(default=False, help_text='Enable system alert notifications'),
        ),
        migrations.AddField(
            model_name='librarysettings',
            name='system_alert_webhook_url',
            field=models.URLField(blank=True, help_text='Webhook URL for system alerts (separate from notifications)', max_length=500),
        ),
    ]
