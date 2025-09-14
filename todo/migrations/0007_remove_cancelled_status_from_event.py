# Generated manually to remove cancelled status from Event model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0006_alter_invitation_status'),
    ]

    operations = [
        # First, update any existing events with 'cancelled' status to be deleted
        migrations.RunSQL(
            "DELETE FROM todo_event WHERE status = 'cancelled';",
            reverse_sql="-- Cannot reverse deletion"
        ),
        # Then update the field choices (Django will handle this automatically)
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(
                choices=[
                    ('upcoming', 'Upcoming'), 
                    ('ongoing', 'Ongoing'), 
                    ('completed', 'Completed')
                ], 
                default='upcoming', 
                max_length=16
            ),
        ),
    ]
