---
repo: django-data-wizard
date: 2020-02-21
tag: latest
tag_color: primary
---

# Django Data Wizard 1.3.0

**Django Data Wizard 1.3.0** brings support for **Django 3.0**, **Django REST Framework 3.11**, and **wq 1.2**, together with configuration enhancements to improve integration with the ecosystem.

## Improvements

### Foreign Key Mapping

Previously, all foreign keys and slugs needed to be mapped manually the first time they were encountered in a file, even if the IDs exactly matched known records in the database (#14, #25).  The new `DATA_WIZARD['IDMAP']` setting provides more flexibility over this behavior.

  * `"data_wizard.idmap.never"`: Require user to manually map all IDs the first time they are found in a file
  * `"data_wizard.idmap.existing"`: Automatically map existing IDs, but require user to map unknown ids
  * `"data_wizard.idmap.always"`: Always map IDs (skip manual mapping).  Unknown IDs will be passed on as-is to the serializer, which will cause per-row errors (unless using natural keys).

For backwards compatibility with the 1.x series, `"data_wizard.idmap.never"` is the default setting.  The default will change to `"data_wizard.idmap.existing"` in version 2.0.

### Django Integration

 * New `DATA_WIZARD['AUTHENTICATION']` setting (see #24)
     * The default value is `"rest_framework.authentication.SessionAuthentication"`, for smooth integration with the Django Admin.
     * This is important for cases where `REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']` is overridden for another purpose that does not include `SessionAuthentication` (see discussion in #24)
 * Don't break if `"data_wizard"` is listed after `"wq.db.rest"` in `INSTALLED_APPS` (see #26)
 * Don't break if `"data_wizard"` is listed before`"django.contrib.admin"` in `INSTALLED_APPS` (see #27)

### wq Framework Integration

The included [wq Framework Integration](https://github.com/wq/django-data-wizard#wq-framework-integration) has been updated for compatibility with the Redux and NPM integration introduced in [wq.app 1.2](https://wq.io/releases/wq.app-1.2.0) (#28).  In addition, the former wq.io dependency has been renamed to [IterTable](https://github.com/wq/itertable).  See the [IterTable release notes] for more information on the name change.

## Upgrade Notes

If you are using Django Data Wizard's built-in admin integration and loaders, then upgrading to 1.3.0 should not affect you.  However:

 * If you created a custom UI that accesses the Wizard's REST API with something other than `SessionAuthentication`, update your `DATA_WIZARD["AUTHENTICATION"]` setting.  Django Data Wizard no longer uses the `REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]` setting.
 * If you were using a [custom loader](https://github.com/wq/django-data-wizard#custom-loader) based on wq.io, rename the `load_io()` method to `load_iter()` and update your import paths as described in the [IterTable release notes].
 * If you are using the wq framework integration, you will need to install [@wq/progress](https://github.com/wq/django-data-wizard/tree/master/packages/progress) from NPM as it is no longer provided in the wq.app PyPI package.

[IterTable release notes]: ./itertable-2.0.0b1.md
