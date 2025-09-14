from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=64)
    message = models.TextField()
    task = models.ForeignKey('Task', null=True, blank=True, on_delete=models.SET_NULL, related_name='notifications')
    event = models.ForeignKey('Event', null=True, blank=True, on_delete=models.SET_NULL, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.type}: {self.message[:40]}"


class Task(models.Model):
    COMPLETE_CHOICES = (
        ('complete', 'Complete'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue')
    )
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    due_date = models.DateField()
    completed = models.CharField(max_length=16, choices=COMPLETE_CHOICES, default='pending')

    assignees = models.ManyToManyField(
        User,
        through='Assignment',
        through_fields=('task', 'user'),
        related_name='assigned_tasks'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} {self.due_date.strftime('%Y-%m-%d')}"

class Assignment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    assigned_by = models.ForeignKey(User, null=True, blank=True, related_name='given_assignments', on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('task', 'user')  # avoid duplicate assignment

    def __str__(self):
        return f"{self.task.title} - {self.user.username} - {self.status}"

class Event(models.Model):

    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('ended', 'Ended')
    )
    title = models.CharField(max_length=100)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events_hosted', null=True, blank=True)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    guests = models.ManyToManyField(
        User,
        through='Invitation',
        related_name='events_invited'
    )

    def __str__(self):
        return f"{self.title} {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}"


class Invitation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='invitations')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    invited_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('event', 'guest')  # mỗi người 1 lời mời duy nhất

    def __str__(self):
        return f"{self.guest.username} invited to {self.event.title} [{self.status}]"

class Note(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    owner = models.ForeignKey(User, null=True, blank=True, related_name='notes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
