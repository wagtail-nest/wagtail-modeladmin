from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailModelAdminAppConfig(AppConfig):
    name = "wagtail_modeladmin"
    label = "wagtail_modeladmin"
    verbose_name = _("Wagtail ModelAdmin")
