from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.documents.models import AbstractDocument, Document
from wagtail.fields import RichTextField
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.models import Orderable, Page, RevisionMixin, TranslatableMixin
from wagtail.search import index

# Custom document models to avoid related_name clashes with models from wagtail.test.testapp.models


class CustomDocument(AbstractDocument):
    admin_form_fields = Document.admin_form_fields


# Custom image models to avoid related_name clashes with models from wagtail.test.testapp.models


class CustomImage(AbstractImage):
    admin_form_fields = Image.admin_form_fields


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


# Models from wagtail.test.testapp.models

EVENT_AUDIENCE_CHOICES = (
    ("public", "Public"),
    ("private", "Private"),
)


COMMON_PANELS = (
    FieldPanel("slug"),
    FieldPanel("seo_title"),
    FieldPanel("show_in_menus"),
    FieldPanel("search_description"),
)


class SimplePage(Page):
    content = models.TextField()
    page_description = "A simple page description"

    content_panels = [
        FieldPanel("title", classname="title"),
        FieldPanel("content"),
    ]

    def get_admin_display_title(self):
        return "%s (simple page)" % super().get_admin_display_title()


class BusinessIndex(Page):
    """Can be placed anywhere, can only have Business children"""

    subpage_types = ["modeladmintest.BusinessChild", "modeladmintest.BusinessSubIndex"]


class BusinessSubIndex(Page):
    """Can be placed under BusinessIndex, and have BusinessChild children"""

    # BusinessNowherePage is 'incorrectly' added here as a possible child.
    # The rules on BusinessNowherePage prevent it from being a child here though.
    subpage_types = [
        "modeladmintest.BusinessChild",
        "modeladmintest.BusinessNowherePage",
    ]
    parent_page_types = ["modeladmintest.BusinessIndex", "modeladmintest.BusinessChild"]


class BusinessChild(Page):
    """Can only be placed under Business indexes, no children allowed"""

    subpage_types = []
    parent_page_types = ["modeladmintest.BusinessIndex", BusinessSubIndex]
    page_description = _("A lazy business child page description")


class BusinessNowherePage(Page):
    """Not allowed to be placed anywhere"""

    parent_page_types = []


class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    link_document = models.ForeignKey(
        "modeladmintest.CustomDocument",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel("link_external"),
        FieldPanel("link_page"),
        FieldPanel("link_document"),
    ]

    class Meta:
        abstract = True


class CarouselItem(LinkFields):
    image = models.ForeignKey(
        "modeladmintest.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("embed_url"),
        FieldPanel("caption"),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class RelatedLink(LinkFields):
    title = models.CharField(
        max_length=255,
    )
    link = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="+")

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("link"),
            ],
            heading="Related Link",
        ),
    ]


class EventPageCarouselItem(TranslatableMixin, Orderable, CarouselItem):
    page = ParentalKey(
        "modeladmintest.EventPage",
        related_name="carousel_items",
        on_delete=models.CASCADE,
    )

    class Meta(TranslatableMixin.Meta, Orderable.Meta):
        pass


class EventPageRelatedLink(TranslatableMixin, Orderable, RelatedLink):
    page = ParentalKey(
        "modeladmintest.EventPage",
        related_name="related_links",
        on_delete=models.CASCADE,
    )

    class Meta(TranslatableMixin.Meta, Orderable.Meta):
        pass


class EventPageSpeakerAward(TranslatableMixin, Orderable, models.Model):
    speaker = ParentalKey(
        "modeladmintest.EventPageSpeaker",
        related_name="awards",
        on_delete=models.CASCADE,
    )
    name = models.CharField("Award name", max_length=255)
    date_awarded = models.DateField(null=True, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("date_awarded"),
    ]

    class Meta(TranslatableMixin.Meta, Orderable.Meta):
        pass


class EventPageSpeaker(TranslatableMixin, Orderable, LinkFields, ClusterableModel):
    page = ParentalKey(
        "modeladmintest.EventPage",
        related_name="speakers",
        related_query_name="speaker",
        on_delete=models.CASCADE,
    )
    first_name = models.CharField("Name", max_length=255, blank=True)
    last_name = models.CharField("Surname", max_length=255, blank=True)
    image = models.ForeignKey(
        "modeladmintest.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    @property
    def name_display(self):
        return self.first_name + " " + self.last_name

    panels = [
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("image"),
        MultiFieldPanel(LinkFields.panels, "Link"),
        InlinePanel("awards", label="Awards"),
    ]

    class Meta(TranslatableMixin.Meta, Orderable.Meta):
        pass


class EventCategory(TranslatableMixin, models.Model):
    name = models.CharField("Name", max_length=255)

    def __str__(self):
        return self.name


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
        FieldPanel("title", classname="title"),
        FieldPanel("intro"),
    ]


class EventPageForm(WagtailAdminPageForm):
    def clean(self):
        cleaned_data = super().clean()

        # Make sure that the event starts before it ends
        start_date = cleaned_data["date_from"]
        end_date = cleaned_data["date_to"]
        if start_date and end_date and start_date > end_date:
            raise ValidationError("The end date must be after the start date")

        return cleaned_data


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
    categories = ParentalManyToManyField(EventCategory, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("get_audience_display"),
        index.SearchField("location"),
        index.SearchField("body"),
        index.FilterField("url_path"),
    ]

    password_required_template = "tests/event_page_password_required.html"
    base_form_class = EventPageForm

    content_panels = [
        FieldPanel("title", classname="title"),
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
        MultiFieldPanel(
            COMMON_PANELS, "Common page configuration", help_text="For SEO nerds only"
        ),
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


class HeadCountRelatedModelUsingPK(models.Model):
    """Related model that uses a custom primary key (pk) not id"""

    custom_id = models.AutoField(primary_key=True)
    event_page = ParentalKey(
        EventPage, on_delete=models.CASCADE, related_name="head_counts"
    )
    head_count = models.IntegerField()
    panels = [FieldPanel("head_count")]


# Models from wagtail.test.modeladmintest


class Author(models.Model):
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()

    def author_birth_string(self):
        return "This author was born in pallet town"

    author_birth_string.short_description = "Birth information"

    def __str__(self):
        return self.name

    def first_book(self):
        # For testing use of object methods in list_display
        book = self.book_set.first()
        if book:
            return book.title
        return ""


class Book(models.Model, index.Indexed):
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    cover_image = models.ForeignKey(
        "modeladmintest.CustomImage", on_delete=models.SET_NULL, null=True, blank=True
    )
    extract_document = models.ForeignKey(
        "modeladmintest.CustomDocument",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    search_fields = [
        index.SearchField("title"),
        index.FilterField("title"),
        index.FilterField("id"),
    ]

    def __str__(self):
        return self.title


class SoloBook(models.Model):
    author = models.OneToOneField(Author, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class TranslatableBook(TranslatableMixin, models.Model, index.Indexed):
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    cover_image = models.ForeignKey(
        "modeladmintest.CustomImage", on_delete=models.SET_NULL, null=True, blank=True
    )

    search_fields = [
        index.SearchField("title"),
        index.FilterField("title"),
        index.FilterField("id"),
    ]

    def __str__(self):
        return self.title


class Token(models.Model):
    key = models.CharField(max_length=40, primary_key=True)

    def __str__(self):
        return self.key


class Publisher(RevisionMixin, models.Model):
    name = models.CharField(max_length=50)
    headquartered_in = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class VenuePage(Page):
    address = models.CharField(max_length=300)
    capacity = models.IntegerField()


class Visitor(models.Model):
    """model used to test modeladmin.edit_handler usage in get_edit_handler"""

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name


class Contributor(models.Model):
    """model used to test modeladmin.panels usage in get_edit_handler"""

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name


class Person(models.Model):
    """model used to test model.edit_handlers usage in get_edit_handler"""

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    panels = [
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("phone_number"),
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(panels),
        ]
    )

    def __str__(self):
        return self.first_name


class Friend(models.Model):
    """model used to test model.panels usage in get_edit_handler"""

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    panels = [
        FieldPanel("first_name"),
        FieldPanel("phone_number"),
    ]

    def __str__(self):
        return self.first_name


class Enemy(models.Model):
    """model used to test add_to_admin_menu usage in ModelAdminMenuItem"""

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
