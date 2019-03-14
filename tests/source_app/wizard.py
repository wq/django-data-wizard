import data_wizard
from .models import CustomSource


data_wizard.set_loader(CustomSource, "tests.source_app.loaders.CustomLoader")
