# `ModelAdmin`

The `modeladmin` module allows you to add any model in your project to the Wagtail admin. You can create customisable listing pages for a model, including plain Django models, and add navigation elements so that a model can be accessed directly from the Wagtail admin. Simply extend the `ModelAdmin` class, override a few attributes to suit your needs, register it with Wagtail using an easy one-line `modeladmin_register` method (you can copy and paste from the examples below), and you're good to go. Your model doesn’t need to extend `Page` or be registered as a `Snippet`, and it won’t interfere with any of the existing admin functionality that Wagtail provides.

```{note}
This package was originally incorporated into Wagtail as `wagtail.contrib.modeladmin`. To manage non-page models in Wagtail, we recommend using {ref}`wagtail:snippets` instead.
```

(modeladmin_feature_summary)=

## Summary of features

-   A customisable list view, allowing you to control what values are displayed for each row, available options for result filtering, default ordering, spreadsheet downloads and more.
-   Access your list views from the Wagtail admin menu easily with automatically generated menu items, with automatic 'active item' highlighting. Control the label text and icons used with easy-to-change attributes on your class.
-   An additional `ModelAdminGroup` class, that allows you to group your related models, and list them together in their own submenu, for a more logical user experience.
-   Simple, robust **add** and **edit** views for your non-Page models that use the panel configurations defined on your model using Wagtail's edit panels.
-   For Page models, the system directs to Wagtail's existing add and edit views, and returns you back to the correct list page, for a seamless experience.
-   Full respect for permissions assigned to your Wagtail users and groups. Users will only be able to do what you want them to!
-   All you need to easily hook your `ModelAdmin` classes into Wagtail, taking care of URL registration, menu changes, and registering any missing model permissions, so that you can assign them to Groups.
-   **Built to be customisable** - While `modeladmin` provides a solid experience out of the box, you can easily use your own templates, and the `ModelAdmin` class has a large number of methods that you can override or extend, allowing you to customise the behaviour to a greater degree.

## Index

```{toctree}
---
maxdepth: 2
titlesonly:
---
installation
usage
primer
base_url
menu_item
indexview
create_edit_delete_views
inspectview
chooseparentview
tips_and_tricks/index
```
