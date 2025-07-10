from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.chatbot_logic import ChatbotLogic
import json

chatbot = ChatbotLogic()

def index(request):
    """홈페이지 뷰"""
    return render(request, 'chatbot/index.html')

def chat_home(request):
    """챗봇 페이지 뷰"""
    return render(request, 'chatbot/chat.html')

def faq_home(request):
    """FAQ 페이지 뷰"""
    return render(request, 'chatbot/faq.html')

def team_home(request):
    return render(request, 'team_manager/index.html')

@csrf_exempt
def message(request):
    """메시지 처리 뷰"""
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('message')
        
        # 응답 생성
        response = chatbot.get_response(query)
        
        return JsonResponse({
            'message': response['message'],
            'confidence': response['confidence'],
            'suggestions': response['suggestions'] if 'suggestions' in response else []
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

def game(request):
    response = render(request, 'chatbot/game.html')
    # 보안 헤더 추가
    response['Content-Security-Policy'] = "frame-ancestors 'self' https://*.addictinggames.com https://*.chromedino.com https://*.playsnake.org"
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response 