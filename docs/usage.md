(modeladmin_usage)=

# How to use

(modeladmin_example_simple)=

## A simple example

Let's say your website is for a local library. They have a model called `Book` that appears across the site in many places. You can define a normal Django model for it, then use ModelAdmin to create a menu in Wagtail's admin to create, view, and edit `Book` entries.

`models.py` looks like this:

```python
from django.db import models
from wagtail.admin.panels import FieldPanel


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover_photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [FieldPanel("title"), FieldPanel("author"), FieldPanel("cover_photo")]
```

```{note}
You can specify panels like `MultiFieldPanel` within the `panels` attribute of the model.
This lets you use Wagtail-specific layouts in an otherwise traditional Django model.
```

`wagtail_hooks.py` in your app directory would look something like this:

```python
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import Book


class BookAdmin(ModelAdmin):
    model = Book
    base_url_path = "bookadmin"  # customise the URL from default to admin/bookadmin
    menu_label = "Book"  # ditch this to use verbose_name_plural from model
    menu_icon = "pilcrow"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    add_to_admin_menu = True  # or False to exclude your model from the menu
    list_display = ("title", "author")
    list_filter = ("author",)
    search_fields = ("title", "author")


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(BookAdmin)
```

(modeladmin_example_complex)=

## A more complicated example

In addition to `Book`, perhaps we also want to add `Author` and `Genre` models to our app and display a menu item for each of them, too. Creating lots of menus can add up quickly, so it might be a good idea to group related menus together. This section show you how to create one menu called _Library_ which expands to show submenus for _Book_, _Author_, and _Genre_.

Assume we've defined `Book`, `Author`, and `Genre` models in `models.py`.

`wagtail_hooks.py` in your app directory would look something like this:

```python
from wagtail_modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from .models import Book, Author, Genre


class BookAdmin(ModelAdmin):
    model = Book
    menu_label = "Book"  # ditch this to use verbose_name_plural from model
    menu_icon = "pilcrow"  # change as required
    list_display = ("title", "author")
    list_filter = ("genre", "author")
    search_fields = ("title", "author")


class AuthorAdmin(ModelAdmin):
    model = Author
    menu_label = "Author"  # ditch this to use verbose_name_plural from model
    menu_icon = "user"  # change as required
    list_display = ("first_name", "last_name")
    list_filter = ("first_name", "last_name")
    search_fields = ("first_name", "last_name")


class GenreAdmin(ModelAdmin):
    model = Genre
    menu_label = "Genre"  # ditch this to use verbose_name_plural from model
    menu_icon = "group"  # change as required
    list_display = ("name",)
    list_filter = ("name",)
    search_fields = ("name",)


class LibraryGroup(ModelAdminGroup):
    menu_label = "Library"
    menu_icon = "folder-open-inverse"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (BookAdmin, AuthorAdmin, GenreAdmin)


# When using a ModelAdminGroup class to group several ModelAdmin classes together,
# you only need to register the ModelAdminGroup class with Wagtail:
modeladmin_register(LibraryGroup)
```

(modeladmin_multi_registration)=

## Registering multiple classes in one `wagtail_hooks.py` file

Each time you call `modeladmin_register(MyAdmin)` it creates a new top-level menu item in Wagtail's left sidebar. You can call this multiple times within the same `wagtail_hooks.py` file if you want. The example below will create 3 top-level menus.

```python
class BookAdmin(ModelAdmin):
    model = Book
    ...


class MovieAdmin(ModelAdmin):
    model = MovieModel
    ...


class MusicAdminGroup(ModelAdminGroup):
    menu_label = _("Music")
    items = (AlbumAdmin, ArtistAdmin)
    ...


modeladmin_register(BookAdmin)
modeladmin_register(MovieAdmin)
modeladmin_register(MusicAdminGroup)
```
