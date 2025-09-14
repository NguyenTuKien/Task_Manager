from rest_framework import serializers
from .models import Task, Event, Note, User, Assignment, Notification, Invitation


class TaskSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'owner', 'owner_username', 'description', 'due_date', 'completed', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'owner']

class AssignmentSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    task_description = serializers.CharField(source='task.description', read_only=True)
    task_due_date = serializers.DateField(source='task.due_date', read_only=True)
    task_completed = serializers.CharField(source='task.completed', read_only=True)
    task_owner = serializers.IntegerField(source='task.owner.id', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'task', 'task_title', 'task_description', 'task_due_date', 
            'task_completed', 'task_owner', 'user', 'user_username', 
            'status', 'completed_at', 'assigned_at', 'accepted_at', 
            'assigned_by', 'assigned_by_username'
        ]
        read_only_fields = ['completed_at', 'assigned_at', 'accepted_at']

class EventSerializer(serializers.ModelSerializer):
    host_username = serializers.CharField(source='host.username', read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'status', 'host', 'host_username', 'created_at', 'updated_at']
        read_only_fields = ['host', 'created_at', 'updated_at']

class NoteSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'owner', 'owner_username', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'type', 'message', 'task', 'is_read', 'created_at']
        read_only_fields = ['user', 'created_at']

class InvitationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_start = serializers.DateTimeField(source='event.start_time', read_only=True)
    event_end = serializers.DateTimeField(source='event.end_time', read_only=True)
    event_description = serializers.CharField(source='event.description', read_only=True)
    event_host = serializers.CharField(source='event.host.username', read_only=True)
    event_status = serializers.CharField(source='event.status', read_only=True)
    host_username = serializers.CharField(source='event.host.username', read_only=True)
    
    class Meta:
        model = Invitation
        fields = ['id', 'event', 'event_title', 'event_start', 'event_end', 'event_description', 'event_status', 'event_host', 'host_username', 'guest', 'status', 'invited_at', 'responded_at']
        read_only_fields = ['invited_at', 'responded_at']

