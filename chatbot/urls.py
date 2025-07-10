from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat_home, name='chat_home'),
    path('faq/', views.faq_home, name='faq_home'),  # FAQ 페이지 추가
    path('message/', views.message, name='chat_message'),
    path('game/', views.game, name='game'),
] 


# path('', views.index, name='index'),  # 홈페이지
#     path('chat/', views.chat_home, name='chat_home'),  # 챗봇 페이지
#     path('message/', views.message, name='message'),  #