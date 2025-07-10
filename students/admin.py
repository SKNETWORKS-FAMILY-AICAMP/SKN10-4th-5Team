from django.contrib import admin
from .models import Cohort, Student

@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('number', 'start_date', 'end_date')
    search_fields = ('number',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'cohort', 'personality', 'average_score', 'created_at')
    list_filter = ('cohort', 'personality')
    search_fields = ('name',)
    fieldsets = (
        ('기본 정보', {
            'fields': ('cohort', 'name')
        }),
        ('평가 항목', {
            'fields': (
                'leadership',
                'personality',
                'motivation',
                'achievement',
                'instructor_rating',
                'peer_rating'
            )
        }),
    )