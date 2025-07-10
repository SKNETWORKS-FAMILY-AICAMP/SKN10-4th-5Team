from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Cohort(models.Model):
    number = models.IntegerField(unique=True, help_text="기수 번호 (예: 10, 11)")
    start_date = models.DateField(help_text="기수 시작일")
    end_date = models.DateField(help_text="기수 종료일")
    
    class Meta:
        ordering = ['-number']  # 최신 기수가 먼저 나오도록
        
    def __str__(self):
        return f"{self.number}기"

    def get_overview_stats(self):
        """기수 전체 통계 반환"""
        students = self.students.all()
        total_students = students.count()
        
        if total_students == 0:
            return None
            
        stats = {
            'total_students': total_students,
            'gender_ratio': {
                'male': students.filter(gender='M').count(),
                'female': students.filter(gender='F').count(),
            },
            'major_ratio': {
                'major': students.filter(is_major=True).count(),
                'non_major': students.filter(is_major=False).count(),
            },
            'avg_age': sum(s.age for s in students) / total_students,
            'personality_distribution': {
                '매우 내향적': students.filter(personality=1).count(),
                '내향적': students.filter(personality=2).count(),
                '중간': students.filter(personality=3).count(),
                '외향적': students.filter(personality=4).count(),
                '매우 외향적': students.filter(personality=5).count(),
            },
            'score_averages': {
                'leadership': sum(s.leadership for s in students) / total_students,
                'motivation': sum(s.motivation for s in students) / total_students,
                'achievement': sum(s.achievement for s in students) / total_students,
                'instructor_rating': sum(s.instructor_rating for s in students) / total_students,
                'peer_rating': sum(s.peer_rating for s in students) / total_students,
            },
            'total_average': sum(s.average_score for s in students) / total_students,
        }
        return stats

class Student(models.Model):
    PERSONALITY_CHOICES = [
        (1, '매우 내향적'),
        (2, '내향적'),
        (3, '중간'),
        (4, '외향적'),
        (5, '매우 외향적'),
    ]
    
    GENDER_CHOICES = [
        ('M', '남자'),
        ('F', '여자'),
    ]

    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='students')
    name = models.CharField(max_length=100, help_text="학생 이름")
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='M',
        help_text="성별"
    )
    age = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="나이",
        default=20
    )
    is_major = models.BooleanField(
        default=False,
        help_text="전공 여부"
    )
    
    # 리더십 (1-10)
    leadership = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="리더십 점수 (1-10)",
        default=5
    )
    
    # 사회성/성격 (1-5)
    personality = models.IntegerField(
        choices=PERSONALITY_CHOICES,
        help_text="사회성/성격 점수 (1: 매우 내향적 ~ 5: 매우 외향적)",
        default=3
    )
    
    # 학업 의지 (1-10)
    motivation = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="학업 의지 점수 (1-10)",
        default=5
    )
    
    # 성취도 평가 (1-10)
    achievement = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="성취도 평가 점수 (1-10)",
        default=5
    )
    
    # 강사 평가 (1-10)
    instructor_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="강사 평가 점수 (1-10)",
        default=5
    )
    
    # 협업 선호도 (1-10)
    peer_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="수강생들간 협업 선호도 (1-10)",
        default=5
    )
    
    # 상담 관련 필드 추가
    first_counseling = models.TextField(
        null=True, 
        blank=True,
        help_text="1차 상담 내용"
    )
    
    second_counseling = models.TextField(
        null=True, 
        blank=True,
        help_text="2차 상담 내용"
    )
    
    third_counseling = models.TextField(
        null=True, 
        blank=True,
        help_text="3차 상담 내용"
    )
    
    special_note = models.TextField(
        null=True, 
        blank=True,
        help_text="특이사항"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['cohort', 'name']
        unique_together = ['cohort', 'name']  # 같은 기수 내에서 이름 중복 방지
    
    def __str__(self):
        return f"[{self.cohort}] {self.name}"

    @property
    def average_score(self):
        """전체 평균 점수 계산 (성격 점수 제외)"""
        scores = [
            self.leadership,
            self.motivation,
            self.achievement,
            self.instructor_rating,
            self.peer_rating
        ]
        return sum(scores) / len(scores)