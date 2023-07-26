# Installation

Install the package from PyPI:

```sh
python -m pip install wagtail-modeladmin
```

Add `wagtail_modeladmin` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "wagtail_modeladmin",
    ...,
]
```

## Migrating from `wagtail.contrib.modeladmin`

If you are migrating from `wagtail.contrib.modeladmin`, replace `wagtail.contrib.modeladmin` with `wagtail_modeladmin` in your `INSTALLED_APPS` setting.

```diff
 INSTALLED_APPS = [
     ...,
-     "wagtail.contrib.modeladmin",
+     "wagtail_modeladmin",
     ...,
 ]
```

Then, replace all imports of `wagtail.contrib.modeladmin` with `wagtail_modeladmin` in your code.

```diff
- from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
+ from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
```
