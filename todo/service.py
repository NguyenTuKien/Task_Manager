from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Task, Assignment, Notification, Event, Invitation

User = get_user_model()

class TaskService:
    def __init__(self, task: Task):
        self.task = task

    def send_notification(self) -> int:
        count = 0
        for assignee in self.task.assignees.all():
            owner_name = self.task.owner.username if self.task.owner else 'someone'
            if self.task.due_date:
                due_text = f" and due date is {self.task.due_date.strftime('%Y-%m-%d')}"
            else:
                due_text = ""
            assignee.notifications.create(
                message=f"The task {self.task.title} is created by {owner_name}{due_text}.",
                type='task_created',
                task=self.task,
            )
            count += 1
        return count

    def refresh_status(self):
        remaining_qs = self.task.assignments.exclude(
            status__in=['rejected', 'removed']
        ).exclude(status='completed')

        if not remaining_qs.exists():
            # Chỉ đánh dấu complete nếu có ít nhất một assignment hoàn thành
            if self.task.assignments.filter(status='completed').exists():
                if self.task.completed != 'complete':
                    self.task.completed = 'complete'
                    self.task.save(update_fields=['completed'])
                    if self.task.owner:
                        self.task.owner.notifications.create(
                            message=f"All assignees have completed the task {self.task.title}.",
                            type='task_completed',
                            task=self.task,
                        )
            return

        today = timezone.now().date()
        if self.task.due_date and self.task.due_date < today:
            if self.task.completed != 'overdue':
                self.task.completed = 'overdue'
                self.task.save(update_fields=['completed'])
            for assignment in remaining_qs:
                assignment.user.notifications.create(
                    message=f"The task {self.task.title} is overdue. Please complete it.",
                    type='task_overdue',
                    task=self.task,
                )
        else:
            for assignment in remaining_qs:
                if self.task.due_date:
                    due_text = f" is due on {self.task.due_date.strftime('%Y-%m-%d')}"
                else:
                    due_text = ""
                assignment.user.notifications.create(
                    message=f"Reminder: Task {self.task.title}{due_text}.",
                    type='task_due',
                    task=self.task,
                )

class AssignmentService:
    def __init__(self, assignment: Assignment):
        self.assignment = assignment
    
    def complete(self):
        if self.assignment.status != 'completed':
            self.assignment.status = 'completed'
            self.assignment.completed_at = timezone.now()
            self.assignment.save(update_fields=['status', 'completed_at'])

            self.assignment.user.notifications.create(
                message=f"You have completed your assignment on task {self.assignment.task.title}.",
                type='assignment_completed',
                task=self.assignment.task,
            )

            # Sau khi 1 assignee xong, cập nhật trạng thái Task
            TaskService(self.assignment.task).refresh_status()

class EventService:
    def __init__(self, event: Event):
        self.event = event

    def invite(self):
        for guest in self.event.guests.all():
            Invitation.objects.get_or_create(event=self.event, guest=guest, defaults={'status': 'pending'})
            guest.notifications.create(
                message=f"You have been invited to {self.event.title} on {self.event.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {self.event.end_time.strftime('%Y-%m-%d %H:%M:%S')}.",
                type='event_invited',
                event=self.event,
            )
        # Thông báo cho host (user)
        self.event.host.notifications.create(
            message=f"You have invited {self.event.guests.count()} guests to {self.event.title}.",
            type='event_invited_host',
            event=self.event,
        )
        self.event.save()

    def count_guests(self):
        # Chỉ đếm khách đã accept
        return self.event.invitations.filter(status='accepted').count()

    def send_reminder(self):
        # Nhắc host
        self.event.host.notifications.create(
            message=f"Reminder: You host the event {self.event.title} on {self.event.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {self.event.end_time.strftime('%Y-%m-%d %H:%M:%S')}.",
            type='event_reminder',
            event=self.event,
        )
        # Nhắc các guest đã accept
        for inv in self.event.invitations.select_related('guest').filter(status='accepted'):
            inv.guest.notifications.create(
                message=f"Reminder: You have an event {self.event.title} on {self.event.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {self.event.end_time.strftime('%Y-%m-%d %H:%M:%S')}.",
                type='event_reminder',
                event=self.event,
            )

    def update_status(self):
        now = timezone.now()
        # Removed cancelled status check since events are now deleted instead of cancelled
        if self.event.start_time > now:
            self.event.status = 'upcoming'
        elif self.event.start_time <= now <= self.event.end_time:
            self.event.status = 'ongoing'
            # Thông báo cho host
            self.event.host.notifications.create(
                message=f"Your event {self.event.title} has started.",
                type='event_started',
                event=self.event,
            )
            # Thông báo cho các guest đã accept
            for inv in self.event.invitations.select_related('guest').filter(status='accepted'):
                inv.guest.notifications.create(
                    message=f"The event {self.event.title} has started.",
                    type='event_started',
                    event=self.event,
                )
        else:
            self.event.status = 'ended'
            # Thông báo cho host
            self.event.host.notifications.create(
                message=f"Your event {self.event.title} has ended.",
                type='event_ended',
                event=self.event,
            )
            # Thông báo cho các guest đã accept
            for inv in self.event.invitations.select_related('guest').filter(status='accepted'):
                inv.guest.notifications.create(
                    message=f"The event {self.event.title} has ended.",
                    type='event_ended',
                    event=self.event,
                )
        self.event.save(update_fields=['status'])

    # Removed cancel() method - events are now deleted instead of cancelled

class InvitationService:
    def __init__(self, invitation: Invitation):
        self.invitation = invitation

    def accept(self):
        self.invitation.status = 'accepted'
        self.invitation.responded_at = timezone.now()
        self.invitation.save(update_fields=['status', 'responded_at'])
        # Thông báo cho guest
        self.invitation.guest.notifications.create(
            message=f"You have accepted the invitation to {self.invitation.event.title}.",
            type='invitation_accepted',
            event=self.invitation.event,
        )
        # Thông báo cho host
        self.invitation.event.host.notifications.create(
            message=f"{self.invitation.guest.username} has accepted the invitation to {self.invitation.event.title}.",
            type='invitation_accepted_host',
            event=self.invitation.event,
        )

    def decline(self):
        self.invitation.status = 'rejected'
        self.invitation.responded_at = timezone.now()
        self.invitation.save(update_fields=['status', 'responded_at'])
        # Thông báo cho guest
        self.invitation.guest.notifications.create(
            message=f"You have rejected the invitation to {self.invitation.event.title}.",
            type='invitation_rejected',
            event=self.invitation.event,
        )
        # Thông báo cho host
        self.invitation.event.host.notifications.create(
            message=f"{self.invitation.guest.username} has rejected the invitation to {self.invitation.event.title}.",
            type='invitation_rejected_host',
            event=self.invitation.event,
        )

class NotificationService:
    def __init__(self, user):  # user: User
        self.user = user

    def mark_all_read(self) -> int:
        return Notification.objects.filter(user=self.user, is_read=False).update(is_read=True)