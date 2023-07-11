from django.apps import AppConfig


class WagtailModelAdminTestAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    label = "modeladmintest"
    name = "wagtail_modeladmin.test"
    verbose_name = "Wagtail ModelAdmin tests"
