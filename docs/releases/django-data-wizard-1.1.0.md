---
repo: django-data-wizard
date: 2019-03-15
---

# Django Data Wizard 1.1.0

**Django Data Wizard 1.1.0** brings a number of exciting improvements while (mostly) maintaining backwards compatibility with 1.0.

## New Features
 * Full integration with the [Django admin](https://docs.djangoproject.com/en/2.1/ref/contrib/admin/), including:
    * Admin-styled Django templates (#7), complementing the existing wq/Mustache templates.
    * ["Import via data wizard" admin action](https://github.com/wq/django-data-wizard#new-run)
    * Optional ready-to-use data source models to streamline setup (`FileSource` and `URLSource`) (#8)
    * Admin view for identifier mappings (#6)
 * Removed hard dependency on Celery/Redis
    * Async processing now uses a simple threading backend, but can still use celery if desired
    * This is configurable via the new [`DATA_WIZARD["BACKEND']`](https://github.com/wq/django-data-wizard#task-backends) setting.
  * Compatibility with Django 2.0/2.1 and Python 3.7 (#11)
  * [CLI](https://github.com/wq/django-data-wizard#command-line-interface) for automated processing (#12)
  * Fixed issues with content type id serialization (#9, #13)

## Upgrade Notes

The Django Data Wizard 1.1 API is designed to be backwards compatible with 1.0, but there are two breaking configuration changes:

  1. The provided `data_wizard.urls` no longer include the `datawizard/` prefix, so you need to add it yourself.

```diff
 urlpatterns = [
     # ...
-    path('', include('data_wizard.urls')),
+    path('datawizard/', include('data_wizard.urls')),
 ]
```

 2. The permission to create, view, and execute `Run` instances via the API is now restricted by default to [`rest_framework.permissions.IsAdminUser`](https://www.django-rest-framework.org/api-guide/permissions/#isadminuser).  Previously the permissions were whatever you had configured for [`REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']`](https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy).  To override the new default, set `DATA_WIZARD['PERMISSION']` to your desired permissions setting.
