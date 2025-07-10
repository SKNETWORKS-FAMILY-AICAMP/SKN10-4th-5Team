from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Cohort
from datetime import date
from django.template.defaulttags import register

@register.filter
def add_days(value, days):
    """템플릿에서 날짜에 일수를 더하는 필터"""
    from datetime import datetime, timedelta
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d").date()
    return value + timedelta(days=days)

def student_list(request):
    # 모든 기수 가져오기
    cohorts = Cohort.objects.all()
    
    # 선택된 기수 (없으면 가장 최근 기수)
    selected_cohort_id = request.GET.get('cohort')
    if selected_cohort_id:
        selected_cohort = Cohort.objects.get(id=selected_cohort_id)
    else:
        selected_cohort = cohorts.first()  # 가장 최근 기수
    
    # 선택된 기수의 학생들 가져오기 (기본 이름순 정렬)
    students = Student.objects.filter(cohort=selected_cohort).order_by('name')
    
    # 선택된 기수의 통계 가져오기
    cohort_stats = selected_cohort.get_overview_stats() if selected_cohort else None
    
    if selected_cohort:
        # 진행률 계산
        today = date.today()
        total_days = (selected_cohort.end_date - selected_cohort.start_date).days
        elapsed_days = (today - selected_cohort.start_date).days
        progress = min(max(int((elapsed_days / total_days) * 100), 0), 100)
        
        # 4등분 날짜 계산
        quarter_duration = total_days // 4
        half_duration = total_days // 2
        three_quarter_duration = (total_days * 3) // 4
        
        context = {
            'cohorts': cohorts,
            'selected_cohort': selected_cohort,
            'students': students,
            'cohort_stats': cohort_stats,
            'progress': progress,
            'days_remaining': max((selected_cohort.end_date - today).days, 0),
            'quarter_duration': quarter_duration,
            'half_duration': half_duration,
            'three_quarter_duration': three_quarter_duration,
        }
    else:
        context = {
            'cohorts': cohorts,
            'selected_cohort': selected_cohort,
            'students': students,
            'cohort_stats': cohort_stats,
        }
    return render(request, 'students/student_list.html', context)

def add_student(request):
    if request.method == 'POST':
        cohort_id = request.POST.get('cohort_id')
        cohort = Cohort.objects.get(id=cohort_id)
        
        # 폼에서 데이터 가져오기
        Student.objects.create(
            cohort=cohort,
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            age=request.POST.get('age'),
            is_major=request.POST.get('is_major') == 'on',
            leadership=request.POST.get('leadership'),
            personality=request.POST.get('personality'),
            motivation=request.POST.get('motivation'),
            achievement=request.POST.get('achievement'),
            instructor_rating=request.POST.get('instructor_rating'),
            peer_rating=request.POST.get('peer_rating'),
        )
        return redirect(f'/students/?cohort={cohort_id}')
    
    # GET 요청인 경우
    cohort_id = request.GET.get('cohort_id')
    cohort = Cohort.objects.get(id=cohort_id)
    return render(request, 'students/add_student.html', {'cohort': cohort})

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        # 폼에서 데이터 가져와서 수정
        student.name = request.POST.get('name')
        student.gender = request.POST.get('gender')
        student.age = request.POST.get('age')
        student.is_major = request.POST.get('is_major') == 'on'
        student.leadership = request.POST.get('leadership')
        student.personality = request.POST.get('personality')
        student.motivation = request.POST.get('motivation')
        student.achievement = request.POST.get('achievement')
        student.instructor_rating = request.POST.get('instructor_rating')
        student.peer_rating = request.POST.get('peer_rating')
        
        # 새로운 필드들 추가
        student.first_counseling = request.POST.get('first_counseling')
        student.second_counseling = request.POST.get('second_counseling')
        student.third_counseling = request.POST.get('third_counseling')
        student.special_note = request.POST.get('special_note')
        
        student.save()
        return redirect(f'/students/?cohort={student.cohort.id}')
    
    return render(request, 'students/edit_student.html', {'student': student})

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    cohort_id = student.cohort.id
    student.delete()
    return redirect(f'/students/?cohort={cohort_id}')

def view_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/view_student.html', {'student': student})

