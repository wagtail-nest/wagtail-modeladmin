from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.documents.models import AbstractDocument, Document
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.models import Orderable, RevisionMixin, TranslatableMixin
from wagtail.search import index

if WAGTAIL_VERSION >= (8, 0):
    import swapper

    swapper.set_app_prefix("wagtailcore", "wagtail")
    PAGE_MODEL_NAME = swapper.get_model_name("wagtailcore", "Page")
else:
    PAGE_MODEL_NAME = "wagtailcore.Page"


# The page models are in 'testmodels_default' or 'testmodels_custombasepage' depending on the USE_CUSTOM_PAGE_MODEL setting.
# Both apps label themselves as 'modeladmintest_pages' so that the rest of the code can refer to them consistently.

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


class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        PAGE_MODEL_NAME,
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
    link = models.ForeignKey(
        PAGE_MODEL_NAME, on_delete=models.CASCADE, related_name="+"
    )

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
        "modeladmintest_pages.EventPage",
        related_name="carousel_items",
        on_delete=models.CASCADE,
    )

    class Meta(TranslatableMixin.Meta, Orderable.Meta):
        pass


class EventPageRelatedLink(TranslatableMixin, Orderable, RelatedLink):
    page = ParentalKey(
        "modeladmintest_pages.EventPage",
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
        "modeladmintest_pages.EventPage",
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


class EventPageForm(WagtailAdminPageForm):
    def clean(self):
        cleaned_data = super().clean()

        # Make sure that the event starts before it ends
        start_date = cleaned_data["date_from"]
        end_date = cleaned_data["date_to"]
        if start_date and end_date and start_date > end_date:
            raise ValidationError("The end date must be after the start date")

        return cleaned_data


class HeadCountRelatedModelUsingPK(models.Model):
    """Related model that uses a custom primary key (pk) not id"""

    custom_id = models.AutoField(primary_key=True)
    event_page = ParentalKey(
        "modeladmintest_pages.EventPage",
        on_delete=models.CASCADE,
        related_name="head_counts",
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
