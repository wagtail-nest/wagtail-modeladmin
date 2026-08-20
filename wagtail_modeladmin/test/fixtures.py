from django.conf import settings

FIXTURE_TEST_SPECIFIC = "test_specific.json"
FIXTURE_MODELADMINTEST = "modeladmintest_test.json"

if (
    hasattr(settings, "WAGTAIL_PAGE_MODEL")
    and settings.WAGTAIL_PAGE_MODEL != "wagtailcore.Page"
):
    FIXTURE_TEST_SPECIFIC = "test_specific_custombasepage.json"
    FIXTURE_MODELADMINTEST = "modeladmintest_test_custombasepage.json"
