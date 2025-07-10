from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    skill_score = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 11)],
        help_text="학생의 실력 점수 (1-10)"
    )
    
    class Meta:
        ordering = ['-skill_score', 'name']  # 실력 점수 내림차순, 이름 오름차순으로 정렬

    def __str__(self):
        return f"{self.name} (점수: {self.skill_score})" 