from wq.db.contrib.files.models import BaseFile
from data_wizard.models import IoFile


class File(IoFile, BaseFile):
    pass
