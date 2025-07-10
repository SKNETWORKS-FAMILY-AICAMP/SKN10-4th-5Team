from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from .team_maker import run_team_optimization
import pandas as pd
import io
import json
import requests
from django.views.decorators.csrf import csrf_exempt

DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"  # 디스코드 웹훅 URL을 설정해야 합니다

def index(request):
    """팀 관리 메인 페이지"""
    return render(request, 'team_manager/index.html')

def upload_csv(request):
    """CSV 파일 업로드 처리"""
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            csv_file = request.FILES['file']
            use_project_preference = request.POST.get('useProjectPreference') == 'true'
            
            # 항상 가중치 전달
            custom_weights = {
                'skillWeight': float(request.POST.get('skillWeight', 2.0)),
                'preferenceWeight': float(request.POST.get('preferenceWeight', 1.0)),
                'previousTeamWeight': float(request.POST.get('previousTeamWeight', 1.0)),
                'projectWeight': float(request.POST.get('projectWeight', 1.0))
            }
            
            # CSV 파일 처리
            csv_content = csv_file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))
            student_names = df['name'].tolist()
            skills = df['skill_score'].tolist()
            
            results, max_score, team_projects = run_team_optimization(
                csv_content=csv_content,
                use_project_preference=use_project_preference,
                custom_weights=custom_weights
            )
            
            if not results:
                return JsonResponse({'success': False, 'error': '팀 구성에 실패했습니다.'})

            formatted_results = []
            for idx, (assignment, score) in enumerate(results):
                formatted_results.append({
                    'combinationNumber': idx + 1,
                    'totalCombinations': len(results),
                    'satisfactionScore': score,
                    'maxPossibleScore': max_score,
                    'assignment': assignment,
                    'studentNames': student_names,
                    'skills': skills,
                    'teamProjects': team_projects[idx] if use_project_preference else None
                })
            
            return JsonResponse({
                'success': True,
                'combinations': formatted_results
            })
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'파일 처리 중 오류가 발생했습니다: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': '올바른 요청이 아닙니다.'
    })

@csrf_exempt
def send_discord(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message')
            
            payload = {
                "content": message
            }
            
            response = requests.post("https://discord.com/api/webhooks/1368444730144329790/dOKiecA6wBBOH1gfKmHYF7bka_lQZProJECpEw580Hc8ajGw6vSeSf0dr5i3_bARr-qP", json=payload)
            
            if response.status_code == 204:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Discord API returned status code: {response.status_code}'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})