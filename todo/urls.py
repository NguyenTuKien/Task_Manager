from django.urls import path
from . import views

urlpatterns = [
    # Tasks
    path('tasks/', views.tasks_list_create, name='tasks_list_create'),
    path('tasks/<int:pk>/', views.task_detail_update_delete, name='task_detail_update_delete'),
    path('tasks/<int:pk>/send-notification/', views.task_send_notification, name='task_send_notification'),
    path('tasks/<int:pk>/check/', views.task_check, name='task_check'),

    # Assignments
    path('assignments/', views.assignments_list_create, name='assignments_list_create'),
    path('assignments/<int:pk>/', views.assignment_detail_update_delete, name='assignment_detail_update_delete'),
    path('assignments/<int:pk>/complete/', views.assignment_complete, name='assignment_complete'),

    # Events
    path('events/', views.events_list_create, name='events_list_create'),
    path('events/<int:pk>/', views.event_detail_update_delete, name='event_detail_update_delete'),
    path('events/<int:pk>/invite/', views.event_invite, name='event_invite'),
    path('events/<int:pk>/count-guests/', views.event_count_guests, name='event_count_guests'),
    path('events/<int:pk>/send-reminder/', views.event_send_reminder, name='event_send_reminder'),
    path('events/<int:pk>/update-status/', views.event_update_status, name='event_update_status'),
    path('events/<int:pk>/cancel/', views.event_cancel, name='event_cancel'),

    # Invitations
    path('invitations/<int:pk>/accept/', views.invitation_accept, name='invitation_accept'),
    path('invitations/<int:pk>/decline/', views.invitation_decline, name='invitation_decline'),

    # Notes
    path('notes/', views.notes_list_create, name='notes_list_create'),
    path('notes/<int:pk>/', views.note_detail_update_delete, name='note_detail_update_delete'),

    # Users
    path('users/', views.users_list, name='users_list'),

    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
    path('invitations/', views.invitations_list, name='invitations_list'),

    #Login
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('me/', views.me_view, name='me'),
    path('debug/csrf/', views.csrf_debug, name='csrf_debug'),
    path('logout/', views.logout_view, name='logout'),

]