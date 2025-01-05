from django.urls import path
from .views import GenerateTattooView, CheckTaskStatusView

urlpatterns = [
    # URL for generating the tattoo image
    path('generate-tattoo/', GenerateTattooView.as_view(), name='generate_tattoo'),

    # URL for checking the status of the task
    path('check-task-status/<str:task_id>/', CheckTaskStatusView.as_view(), name='check_task_status'),
]
