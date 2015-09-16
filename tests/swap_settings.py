from .settings import *  # noqa

SWAP = True

INSTALLED_APPS += ("tests.swap_app",)
WQ_REPORT_MODEL = "swap_app.Record"
WQ_SITE_MODEL = "swap_app.Site"
