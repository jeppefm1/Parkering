from django.contrib import admin
from .models import Tutorial
from tinymce.widgets import TinyMCE
from django.db import models
# Register your models here.

class TutorialAdmin(admin.ModelAdmin):
    fieldsets = [("Title/date", {"fields": ["title", "published"]}),
                 ("Content", {"fields": ["content"]})]
    formfield_overrides = {models.TextField: {'widget': TinyMCE()},}

admin.site.register(Tutorial, TutorialAdmin)
