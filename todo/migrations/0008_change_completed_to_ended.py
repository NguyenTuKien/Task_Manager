# Generated manually to change event status from 'completed' to 'ended'

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0007_alter_event_status'),
    ]

    operations = [
        # First, update any existing events with 'completed' status to 'ended'
        migrations.RunSQL(
            "UPDATE todo_event SET status = 'ended' WHERE status = 'completed';",
            reverse_sql="UPDATE todo_event SET status = 'completed' WHERE status = 'ended';"
        ),
        # Then update the field choices
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(
                choices=[
                    ('upcoming', 'Upcoming'), 
                    ('ongoing', 'Ongoing'), 
                    ('ended', 'Ended')
                ], 
                default='upcoming', 
                max_length=16
            ),
        ),
    ]
