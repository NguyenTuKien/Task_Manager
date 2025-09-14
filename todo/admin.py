from django.contrib import admin
from .models import Task, Assignment, Event, Note, Notification, Invitation


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ('user', 'status', 'assigned_by', 'assigned_at', 'accepted_at', 'completed_at')
    readonly_fields = ('assigned_at', 'accepted_at', 'completed_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'due_date', 'completed', 'created_at', 'updated_at')
    list_filter = ('completed', 'due_date', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AssignmentInline]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'user', 'status', 'assigned_by', 'assigned_at', 'accepted_at', 'completed_at')
    list_filter = ('status', 'assigned_at', 'accepted_at', 'completed_at')
    search_fields = ('task__title', 'user__username', 'user__email', 'assigned_by__username', 'assigned_by__email')
    readonly_fields = ('assigned_at', 'accepted_at', 'completed_at')


class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 0
    fields = ('guest', 'status', 'invited_at', 'responded_at')
    readonly_fields = ('invited_at', 'responded_at')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'host', 'status', 'start_time', 'end_time', 'created_at', 'updated_at')
    list_filter = ('status', 'start_time', 'end_time', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'host__username', 'host__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [InvitationInline]


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type', 'task', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('message', 'user__username', 'user__email', 'type', 'task__title')
    readonly_fields = ('created_at',)


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'guest', 'status', 'invited_at', 'responded_at')
    list_filter = ('status', 'invited_at', 'responded_at')
    search_fields = ('event__title', 'guest__username', 'guest__email')
    readonly_fields = ('invited_at', 'responded_at')


