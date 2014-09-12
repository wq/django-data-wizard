from .settings import *

SWAP = True

INSTALLED_APPS += ("tests.swap_app",)
WQ_REPORT_MODEL = "swap_app.Report"
WQ_SITE_MODEL = "swap_app.Site"
