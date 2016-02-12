
from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from import_export import resources

from feedback.models import FeedbackList

app_models = apps.get_app_config('feedback').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
