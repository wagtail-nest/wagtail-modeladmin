# Wagtail ModelAdmin

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![PyPI version](https://badge.fury.io/py/wagtail-modeladmin.svg)](https://badge.fury.io/py/wagtail-modeladmin)
[![ModelAdmin CI](https://github.com/wagtail-nest/wagtail-modeladmin/actions/workflows/test.yml/badge.svg)](https://github.com/wagtail-nest/wagtail-modeladmin/actions/workflows/test.yml)

Add any model in your project to the Wagtail admin. Formerly `wagtail.contrib.modeladmin`.

This package is in maintenance mode and will not receive new features. Consider [migrating to Snippets](https://docs.wagtail.org/en/stable/reference/contrib/modeladmin/migrating_to_snippets.html) and opening new feature requests in the [Wagtail issue tracker](https://github.com/wagtail/wagtail/issues).

## Links

- [Documentation](https://wagtail-modeladmin.readthedocs.io)
- [Changelog](https://github.com/wagtail-nest/wagtail-modeladmin/blob/main/CHANGELOG.md)
- [Contributing](https://github.com/wagtail-nest/wagtail-modeladmin/blob/main/CHANGELOG.md)
- [Discussions](https://github.com/wagtail-nest/wagtail-modeladmin/discussions)
- [Security](https://github.com/wagtail-nest/wagtail-modeladmin/security)

## Supported versions

- Python 3.8, 3.9, 3.10, 3.11, 3.12
- Django 4.2, 5.0
- Wagtail 5.2, 6.0

## Installation

- `python -m pip install wagtail-modeladmin`
- Add `wagtail_modeladmin` to your `INSTALLED_APPS` setting.
  ```python
  INSTALLED_APPS = [
      # ...
      "wagtail_modeladmin",
      # ...
  ]
  ```

## Contributing

### Install

To make changes to this project, first clone this repository:

```sh
git clone https://github.com/wagtail-nest/wagtail-modeladmin.git
cd wagtail-modeladmin
```

With your preferred virtualenv activated, install testing dependencies:

#### Using pip

```sh
python -m pip install --upgrade pip>=21.3
python -m pip install -e .[testing] -U
```

#### Using flit

```sh
python -m pip install flit
flit install
```

### pre-commit

Note that this project uses [pre-commit](https://github.com/pre-commit/pre-commit).
It is included in the project testing requirements. To set up locally:

```shell
# go to the project directory
$ cd wagtail-modeladmin
# initialize pre-commit
$ pre-commit install

# Optional, run all checks once for this, then the checks will run only on the changed files
$ git ls-files --others --cached --exclude-standard | xargs pre-commit run --files
```

### How to run tests

Now you can run tests as shown below:

```sh
tox
```

or, you can run them for a specific environment `tox -e python3.10-django4.2-wagtail4.1` or specific test
`tox -e python3.10-django4.2-wagtail4.1-sqlite wagtail-modeladmin.tests.test_file.TestClass.test_method`

To run the test app interactively, use `tox -e interactive`, visit `http://127.0.0.1:8020/admin/` and log in with `admin`/`changeme`.
