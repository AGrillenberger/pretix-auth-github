from django.urls import path

from .views import return_view, start_view

urlpatterns = [
    path('_github/start', start_view, name='start'),
    path('_github/return', return_view, name='return'),
]
