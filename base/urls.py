from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lobby/', views.lobby, name='lobby'),
    path('room/', views.room, name='room'),
    path('recognize/', views.recognize, name='recognize'),
    path('speak/', views.speak, name='speak'),
]