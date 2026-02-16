from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:conversation_id>/', views.index, name='conversation'),
    path('send/', views.send_message, name='send_message'),
    path('upload/', views.upload_image, name='upload_image'),
    path('new/', views.new_conversation, name='new_conversation'),
    path('rename/<int:conversation_id>/', views.rename_conversation, name='rename_conversation'),
    path('delete/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    path('weather/', views.get_weather_data, name='get_weather_data'),
]
