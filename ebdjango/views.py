from django.shortcuts import render
from django.utils import timezone

def home(request):
    # Get visit count from session
    visit_count = request.session.get('visit_count', 0) + 1
    request.session['visit_count'] = visit_count

    context = {
        'site_name': 'AWS Elastic Beanstalk Django 프로젝트',
        'tagline': 'AWS Elastic Beanstalk 과 SSL 인증를 통한 Https 세팅 및 AWS Route 53 커스텀 도메인 테스트. \nElastic Beanstalk은 자동으로 VPC, DB, S3, EC2 인스턴스 및 AWS 로드 밸런싱과 오토 스케일링을 자동으로 수행합니다. \n당연히 세팅 조정 가능 ㅋ',
        'current_time': timezone.now().strftime('%B %d, %Y %H:%M:%S'),
        'visit_count': visit_count,
    }
    return render(request, 'home.html', context) 