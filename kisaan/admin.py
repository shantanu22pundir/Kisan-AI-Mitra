from django.contrib import admin
from .models import UserSubmission

@admin.register(UserSubmission)
class UserSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
