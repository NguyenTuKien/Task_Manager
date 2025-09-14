from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0003_event_invitation_and_notification_event_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='owner',
            field=models.ForeignKey(null=True, blank=True, related_name='notes', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]