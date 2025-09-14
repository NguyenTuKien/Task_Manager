from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0003_event_invitation_and_notification_event_fk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='role',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='is_completed',
        ),
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.CharField(max_length=16, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('overdue', 'Overdue')], default='pending'),
        ),
    ]
