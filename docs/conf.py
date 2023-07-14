# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from datetime import date

import sphinx_wagtail_theme
from wagtail import __version__

# on_rtd is whether we are on readthedocs.org, this line of code grabbed from docs.readthedocs.org
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath(".."))

project = "Wagtail ModelAdmin"
copyright = f"{date.today().year}, Wagtail Core Team"
author = "Wagtail Core Team"
release = __version__
version = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "myst_parser",
    "sphinx_wagtail_theme",
]

if not on_rtd:
    extensions.append("sphinxcontrib.spelling")

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ["_static"]

html_theme = "sphinx_wagtail_theme"
html_theme_path = [sphinx_wagtail_theme.get_html_theme_path()]

html_theme_options = {
    "project_name": "Wagtail ModelAdmin Documentation",
    "github_url": "https://github.com/wagtail-nest/wagtail-modeladmin/blob/main/docs/",
}

html_last_updated_fmt = "%b %d, %Y"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None  # covered by sphinx_wagtail_theme

spelling_lang = "en_US"
spelling_word_list_filename = "spelling_wordlist.txt"

# sphinx.ext.intersphinx settings
intersphinx_mapping = {
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
    "wagtail": (
        "https://docs.wagtail.org/en/stable/",
        "https://docs.wagtail.org/en/stable/objects.inv",
    ),
}
