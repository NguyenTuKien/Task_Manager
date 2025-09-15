# Python
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Task, Assignment, Event, Note, Notification, Invitation
from .serializers import (
    TaskSerializer,
    AssignmentSerializer,
    EventSerializer,
    NoteSerializer,
    NotificationSerializer,
    InvitationSerializer,
)
from .service import TaskService, AssignmentService, NotificationService, EventService, InvitationService
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .forms import LoginForm, SignupForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@csrf_protect
def login_view(request):
    """JSON-based login endpoint (replaces template rendering). GET issues CSRF token."""
    get_token(request)  # ensure csrftoken cookie
    if request.method == 'GET':
        if request.user.is_authenticated:
            return JsonResponse({'authenticated': True, 'username': request.user.username, 'id': request.user.id})
        return JsonResponse({'authenticated': False})

    # POST: accept form-encoded or JSON
    data = request.POST
    if request.content_type and 'application/json' in request.content_type.lower():
        import json
        try:
            data = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            data = {}

    form = LoginForm(data if hasattr(data, 'get') else data)
    if form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'username': user.username, 'id': user.id})
    return JsonResponse({'success': False, 'errors': {'__all__': ['Sai username hoặc password.']}}, status=400)


@csrf_protect
def signup_view(request):
    """JSON-based signup endpoint issuing CSRF token."""
    get_token(request)
    if request.method == 'GET':
        if request.user.is_authenticated:
            return JsonResponse({'authenticated': True, 'username': request.user.username, 'id': request.user.id})
        return JsonResponse({'authenticated': False})

    data = request.POST
    if request.content_type and 'application/json' in request.content_type.lower():
        import json
        try:
            data = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            data = {}

    form = SignupForm(data if hasattr(data, 'get') else data)
    if form.is_valid():
        user = form.save()
        # auto login
        authed = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
        if authed is not None:
            login(request, authed)
    return JsonResponse({'success': True, 'username': user.username, 'id': user.id})

    # serialize errors
    errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
    return JsonResponse({'success': False, 'errors': errors}, status=400)

@api_view(['GET'])
def me_view(request):
    if request.user.is_authenticated:
        return Response({'authenticated': True, 'username': request.user.username, 'id': request.user.id})
    return Response({'authenticated': False})

@api_view(['GET'])
def csrf_debug(request):
    return Response({
        'CSRF_TRUSTED_ORIGINS': settings.CSRF_TRUSTED_ORIGINS,
        'CORS_ALLOWED_ORIGINS': getattr(settings, 'CORS_ALLOWED_ORIGINS', []),
        'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
        'received_origin': request.headers.get('Origin'),
    })

@csrf_protect
def logout_view(request):
    """Session logout -> POST. GET just returns state and ensures CSRF cookie."""
    get_token(request)
    if request.method == 'POST':
        if request.user.is_authenticated:
            auth_logout(request)
        return JsonResponse({'success': True})
    return JsonResponse({'detail': 'Logout endpoint', 'authenticated': request.user.is_authenticated})
# ===== Tasks =====
@api_view(['GET', 'POST'])

def tasks_list_create(request):
    if request.method == 'GET':
        # Only show tasks the current user owns (hide tasks where user is only an assignee)
        qs = Task.objects.filter(owner=request.user).select_related('owner')
        serializer = TaskSerializer(qs, many=True)
        return Response(serializer.data)
    # POST: create new task owned by current user
    assignees = request.data.pop('assignees', [])  # Extract assignees list
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        task = serializer.save(owner=request.user)
        
        # Create assignments for selected users
        if assignees:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            for user_id in assignees:
                try:
                    user = User.objects.get(id=user_id)
                    Assignment.objects.create(
                        task=task,
                        user=user,
                        assigned_by=request.user
                    )
                except User.DoesNotExist:
                    continue
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])


def task_detail_update_delete(request, pk):
    task = get_object_or_404(Task.objects.select_related('owner'), pk=pk)

    if request.method == 'GET':
        return Response(TaskSerializer(task).data)

    if request.method == 'PATCH':
        if task.owner != request.user:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if task.owner != request.user:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    task.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def task_send_notification(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.owner and task.owner != request.user:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    total = task.assignees.count()
    if total == 0:
        return Response({'detail': 'No assignees to notify.'}, status=status.HTTP_400_BAD_REQUEST)

    sent = TaskService(task).send_notification()
    return Response({'detail': f'Notifications sent to {sent} assignees.'})


@api_view(['POST'])
def task_check(request, pk):
    task = get_object_or_404(Task, pk=pk)
    TaskService(task).refresh_status()
    return Response({'detail': 'Task status refreshed.'})

# ===== Assignments =====
@api_view(['GET', 'POST'])
def assignments_list_create(request):
    if request.method == 'GET':
        # Only show assignments where current user is the assignee (hide those merely owned/assigned by user)
        qs = Assignment.objects.filter(user=request.user).select_related('task', 'user', 'assigned_by')
        serializer = AssignmentSerializer(qs, many=True)
        return Response(serializer.data)

    serializer = AssignmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(assigned_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
def assignment_detail_update_delete(request, pk):
    assignment = get_object_or_404(
        Assignment.objects.select_related('task', 'user', 'assigned_by'), pk=pk
    )

    if request.method == 'GET':
        return Response(AssignmentSerializer(assignment).data)

    if request.method == 'PATCH':
        serializer = AssignmentSerializer(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    assignment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['POST'])
def assignment_complete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if assignment.user != request.user:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    AssignmentService(assignment).complete()
    return Response({'detail': 'Assignment completed.'})

# ===== Events =====
@api_view(['GET', 'POST'])
def events_list_create(request):
    if request.method == 'GET':
        # Only show events the user hosts (hide events where user is only a guest)
        qs = Event.objects.filter(host=request.user)
        serializer = EventSerializer(qs, many=True)
        return Response(serializer.data)
    # POST: create event setting current user as host
    guests = request.data.pop('guests', [])  # Extract guests list
    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
        event = serializer.save(host=request.user)
        
        # Create invitations for selected guests
        if guests:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            for user_id in guests:
                try:
                    user = User.objects.get(id=user_id)
                    Invitation.objects.create(
                        event=event,
                        guest=user
                    )
                except User.DoesNotExist:
                    continue
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
def event_detail_update_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'GET':
        return Response(EventSerializer(event).data)

    if request.method == 'PATCH':
        if request.user != event.host:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.user != event.host:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    event.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def event_invite(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.host:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    EventService(event).invite()
    return Response({'detail': 'Invitations processed and notifications sent.'})


@api_view(['GET'])

def event_count_guests(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.host:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    count = EventService(event).count_guests()
    return Response({'count': count})


@api_view(['POST'])
def event_send_reminder(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.host:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    EventService(event).send_reminder()
    return Response({'detail': 'Reminders sent to host and accepted guests.'})


@api_view(['POST'])
def event_update_status(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.host:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    EventService(event).update_status()
    return Response({'detail': 'Event status updated.'})


@api_view(['DELETE'])
def event_cancel(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.host:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    
    # Delete the event instead of cancelling it
    event_title = event.title
    event.delete()
    
    return Response({'detail': f'Event "{event_title}" has been deleted.'})


# ===== Invitations =====
@api_view(['POST'])

def invitation_accept(request, pk):
    invitation = get_object_or_404(Invitation, pk=pk)
    if request.user != invitation.guest:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    InvitationService(invitation).accept()
    return Response({'detail': 'Invitation accepted.'})


@api_view(['POST'])
def invitation_decline(request, pk):
    invitation = get_object_or_404(Invitation, pk=pk)
    if request.user != invitation.guest:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    InvitationService(invitation).decline()
    return Response({'detail': 'Invitation rejected.'})

# ===== Notes =====
@api_view(['GET', 'POST'])
def notes_list_create(request):
    if request.method == 'GET':
        qs = Note.objects.filter(owner=request.user)
        serializer = NoteSerializer(qs, many=True)
        return Response(serializer.data)

    serializer = NoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
def note_detail_update_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)

    if request.method == 'GET':
        return Response(NoteSerializer(note).data)

    if request.method == 'PATCH':
        if note.owner != request.user:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if note.owner != request.user:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    note.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# ===== Notifications (của user hiện tại) =====
@api_view(['GET'])
def notifications_list(request):
    qs = Notification.objects.filter(user=request.user).select_related('task')
    serializer = NotificationSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['GET'])

def invitations_list(request):
    # Only invitations where current user is the guest
    qs = Invitation.objects.filter(guest=request.user).select_related('event', 'guest')
    serializer = InvitationSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def notification_mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    return Response({'detail': 'Notification marked as read.'})


@api_view(['POST'])

def notifications_mark_all_read(request):
    updated = NotificationService(request.user).mark_all_read()
    return Response({'detail': f'{updated} notifications marked as read.'})


@api_view(['GET'])
def users_list(request):
    """Get list of all users for assignments and invitations"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    users = User.objects.exclude(id=request.user.id).values('id', 'username')
    return Response(list(users))