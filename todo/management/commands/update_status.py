from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from todo.models import Task, Assignment, Event, Invitation


class Command(BaseCommand):
    help = 'Update status of tasks, assignments, events, and invitations based on current time'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        today = now.date()

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No actual updates will be made')
            )

        # Update Tasks - mark as overdue if past due_date and not completed
        # Also include tasks due today but past end of day (if current time is past midnight)
        overdue_tasks = Task.objects.filter(
            due_date__lte=today,  # Changed from __lt to __lte to include today
            completed__in=['pending']
        )
        
        # Filter out tasks due today if we're still early in the day
        # (Optional: keep tasks due today as overdue only after a certain hour)
        if now.hour < 23:  # Before 11 PM, don't mark today's tasks as overdue yet
            overdue_tasks = overdue_tasks.exclude(due_date=today)
        
        tasks_count = overdue_tasks.count()
        if tasks_count > 0:
            if dry_run:
                self.stdout.write(f'Would update {tasks_count} tasks to overdue status')
                for task in overdue_tasks:
                    self.stdout.write(f'  - Task: {task.title} (due: {task.due_date})')
            else:
                overdue_tasks.update(completed='overdue')
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {tasks_count} tasks to overdue status')
                )

        # Update Assignments - mark as overdue if task is past due_date and not completed
        overdue_assignments = Assignment.objects.filter(
            task__due_date__lt=today,
            task__completed__in=['pending', 'overdue'],  # Only if task is not completed
            status='pending'
        )
        
        assignments_count = overdue_assignments.count()
        if assignments_count > 0:
            if dry_run:
                self.stdout.write(f'Would update {assignments_count} assignments to overdue status')
                for assignment in overdue_assignments:
                    self.stdout.write(f'  - Assignment: {assignment.task.title} to {assignment.user.username} (due: {assignment.task.due_date})')
            else:
                overdue_assignments.update(status='overdue')
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {assignments_count} assignments to overdue status')
                )

        # Update Assignments - mark as completed if task is completed but assignment is still pending
        completed_task_assignments = Assignment.objects.filter(
            task__completed='complete',
            status='pending'
        )
        
        completed_assignments_count = completed_task_assignments.count()
        if completed_assignments_count > 0:
            if dry_run:
                self.stdout.write(f'Would update {completed_assignments_count} assignments to completed status (task already completed)')
                for assignment in completed_task_assignments:
                    self.stdout.write(f'  - Assignment: {assignment.task.title} to {assignment.user.username}')
            else:
                completed_task_assignments.update(status='completed', completed_at=now)
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {completed_assignments_count} assignments to completed status')
                )

        # Update Events - check for ongoing and completed events
        # Events that should be ongoing (current time is between start_time and end_time)
        ongoing_events = Event.objects.filter(
            start_time__lte=now,
            end_time__gt=now,
            status='upcoming'
        )
        
        ongoing_count = ongoing_events.count()
        if ongoing_count > 0:
            if dry_run:
                self.stdout.write(f'Would update {ongoing_count} events to ongoing status')
                for event in ongoing_events:
                    self.stdout.write(f'  - Event: {event.title} (started: {event.start_time})')
            else:
                ongoing_events.update(status='ongoing')
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {ongoing_count} events to ongoing status')
                )

        # Events that should be completed (current time is past end_time)
        completed_events = Event.objects.filter(
            end_time__lt=now,
            status__in=['upcoming', 'ongoing']
        )
        
        completed_events_count = completed_events.count()
        if completed_events_count > 0:
            if dry_run:
                self.stdout.write(f'Would update {completed_events_count} events to ended status')
                for event in completed_events:
                    self.stdout.write(f'  - Event: {event.title} (ended: {event.end_time})')
            else:
                completed_events.update(status='ended')
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {completed_events_count} events to ended status')
                )

        # Note: Invitations don't need automatic status updates as they depend on user actions
        # However, we could potentially mark them as "expired" if the event has passed
        # and they are still pending, but this might not be desired behavior

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Status update completed at {now.strftime("%Y-%m-%d %H:%M:%S")}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('Dry run completed - no changes were made')
            )
