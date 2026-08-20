from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    TitleFieldPanel,
)
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

from wagtail_modeladmin.test.models import EVENT_AUDIENCE_CHOICES, EventPageForm


class SimplePage(Page):
    content = models.TextField()
    page_description = "A simple page description"

    content_panels = [
        TitleFieldPanel("title", classname="title"),
        FieldPanel("content"),
    ]

    def get_admin_display_title(self):
        return "%s (simple page)" % super().get_admin_display_title()


class BusinessIndex(Page):
    """Can be placed anywhere, can only have Business children"""

    subpage_types = [
        "modeladmintest_pages.BusinessChild",
        "modeladmintest_pages.BusinessSubIndex",
    ]


class BusinessSubIndex(Page):
    """Can be placed under BusinessIndex, and have BusinessChild children"""

    # BusinessNowherePage is 'incorrectly' added here as a possible child.
    # The rules on BusinessNowherePage prevent it from being a child here though.
    subpage_types = [
        "modeladmintest_pages.BusinessChild",
        "modeladmintest_pages.BusinessNowherePage",
    ]
    parent_page_types = [
        "modeladmintest_pages.BusinessIndex",
        "modeladmintest_pages.BusinessChild",
    ]


class BusinessChild(Page):
    """Can only be placed under Business indexes, no children allowed"""

    subpage_types = []
    parent_page_types = [
        "modeladmintest_pages.BusinessIndex",
        "modeladmintest_pages.BusinessSubIndex",
    ]
    page_description = _("A lazy business child page description")


class BusinessNowherePage(Page):
    """Not allowed to be placed anywhere"""

    parent_page_types = []


class VenuePage(Page):
    address = models.CharField(max_length=300)
    capacity = models.IntegerField()


class EventIndex(Page):
    intro = RichTextField(blank=True, max_length=50)
    ajax_template = "tests/includes/event_listing.html"

    def get_events(self):
        return self.get_children().live().type(EventPage)

    def get_paginator(self):
        return Paginator(self.get_events(), 4)

    def get_context(self, request, page=1):
        # Pagination
        paginator = self.get_paginator()
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)

        # Update context
        context = super().get_context(request)
        context["events"] = events
        return context

    def route(self, request, path_components):
        if self.live and len(path_components) == 1:
            try:
                return self.serve(request, page=int(path_components[0]))
            except (TypeError, ValueError):
                pass

        return super().route(request, path_components)

    def get_sitemap_urls(self, request=None):
        # Add past events url to sitemap
        return super().get_sitemap_urls(request=request) + [
            {
                "location": self.full_url + "past/",
                "lastmod": self.latest_revision_created_at,
            }
        ]

    def get_cached_paths(self):
        return super().get_cached_paths() + ["/past/"]

    content_panels = [
        TitleFieldPanel("title", classname="title"),
        FieldPanel("intro"),
    ]


class EventPage(Page):
    date_from = models.DateField("Start date", null=True)
    date_to = models.DateField(
        "End date",
        null=True,
        blank=True,
        help_text="Not required if event is on a single day",
    )
    time_from = models.TimeField("Start time", null=True, blank=True)
    time_to = models.TimeField("End time", null=True, blank=True)
    audience = models.CharField(max_length=255, choices=EVENT_AUDIENCE_CHOICES)
    location = models.CharField(max_length=255)
    body = RichTextField(blank=True)
    cost = models.CharField(max_length=255)
    signup_link = models.URLField(blank=True)
    feed_image = models.ForeignKey(
        "modeladmintest.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    categories = ParentalManyToManyField("modeladmintest.EventCategory", blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("get_audience_display"),
        index.SearchField("location"),
        index.SearchField("body"),
        index.FilterField("url_path"),
    ]

    password_required_template = "tests/event_page_password_required.html"
    base_form_class = EventPageForm

    content_panels = [
        TitleFieldPanel("title", classname="title"),
        FieldPanel("date_from"),
        FieldPanel("date_to"),
        FieldPanel("time_from"),
        FieldPanel("time_to"),
        FieldPanel("location"),
        FieldPanel("audience", help_text="Who this event is for"),
        FieldPanel("cost"),
        FieldPanel("signup_link"),
        InlinePanel("carousel_items", label="Carousel items"),
        FieldPanel("body"),
        InlinePanel(
            "speakers",
            label="Speakers",
            heading="Speaker lineup",
            help_text="Put the keynote speaker first",
        ),
        InlinePanel("related_links", label="Related links"),
        FieldPanel("categories"),
        # InlinePanel related model uses `pk` not `id`
        InlinePanel("head_counts", label="Head Counts"),
    ]

    promote_panels = [
        FieldPanel("feed_image"),
    ]

    class Meta:
        permissions = [
            ("custom_see_panel_setting", "Can see the panel."),
            ("other_custom_see_panel_setting", "Can see the panel."),
        ]


class SingleEventPage(EventPage):
    excerpt = models.TextField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Short text to describe what is this action about",
    )

    # Give this page model a custom URL routing scheme
    def get_url_parts(self, request=None):
        url_parts = super().get_url_parts(request=request)
        if url_parts is None:
            return None
        else:
            site_id, root_url, page_path = url_parts
            return (site_id, root_url, page_path + "pointless-suffix/")

    def route(self, request, path_components):
        if path_components == ["pointless-suffix"]:
            # treat this as equivalent to a request for this page
            return super().route(request, [])
        else:
            # fall back to default routing rules
            return super().route(request, path_components)

    def get_admin_display_title(self):
        return "%s (single event)" % super().get_admin_display_title()

    content_panels = [FieldPanel("excerpt")] + EventPage.content_panels
