
from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from import_export import resources

from feedback import models


class Admin(admin.ModelAdmin):
    list_display = ('text', 'enabled')

admin.site.register(models.QuestionsEvent, Admin)
admin.site.register(models.QuestionsUser, Admin)
admin.site.register(models.QuestionsDay, Admin)