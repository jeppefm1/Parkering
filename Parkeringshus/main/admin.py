from django.contrib import admin
from .models import Tutorial
# Register your models here.

class TutorialAdmin(admin.ModelAdmin):
    fieldsets = [("Title/date", {"fields": ["title", "published"]}),
                 ("Content", {"fields": ["content"]})]

admin.site.register(Tutorial, TutorialAdmin)
